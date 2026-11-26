import random
import time
import black_box
import time
import numpy as np
from error_metrics import get_average_q_error, get_percentile_q_error
from pg_hint_utility import get_single_table_pointer, inject_single_table_sels_and_get_cost, gen_final_hint, get_real_latency
from utility import parse_inserted_field

class Leo1D:
    def __init__(
        self,
        name=None,
        conn=None,
        cursor=None,
        sql=None,
        overlap_ratio_lb=None, # We will do the correction only when overlap_ratio, i.e., overlap_ratio >= overlap_ratio_lb; And we need to ensure that overlap_ratio in [0., 1.] 
        info_id=None,
        sel_by_domain=None,
        assigned_alias=None,
        enable_lazy_tuple_updates=False,
    ):
        self.name = name
        if assigned_alias is not None:
            self.abbrev = assigned_alias
        else:
            self.abbrev = ""
            for piece in name.strip().split("_"):
                self.abbrev += piece[0]

        self.conn = conn
        self.cursor = cursor

        self.dbname_prefix = ""

        self.sql = sql
        assert self.sql is not None
        self.n_tabs_in_from = sql.lower().split("from")[1].split("where")[0].count(",") + 1

        self.overlap_ratio_lb = overlap_ratio_lb
        assert self.overlap_ratio_lb is not None and self.overlap_ratio_lb >= 0. and self.overlap_ratio_lb <= 1.

        self.info_id = info_id
        self.sel_by_domain = sel_by_domain

        self.enable_lazy_tuple_updates = enable_lazy_tuple_updates
        if self.enable_lazy_tuple_updates:
            self.to_insert_buffer = []
            self.to_delete_range = [None, None]

        self._query_id = 0 # the 0-based query id for all the queries that have been seen so far
        self.leo_set = []  # a list of [RangeSelection, true_card]
        self.preds = [] # a list of model's pred, where each one is corresponding to the 

    def load_table(self, file, sel_col, jk_cols, pgtype, timestamp_col=None):
        self.sel_col = sel_col
        self.jk_cols = jk_cols
        self.attrs = list(pgtype.keys())
        self.pgtype = pgtype

        dbname = self.dbname_prefix + self.name

        print(f"Load Table {self.name} to {dbname}")
        self.cursor.execute(f"drop table if exists {dbname};")
        if " " in sel_col:
            # for the case where selection is on an expression, e.g., "ss_sales_price / ss_list_price"
            for each in sel_col.split(" "):
                if each.startswith(dbname[0]): # share the same first bit as the table_name
                    self.cursor.execute(f"drop index if exists idx_{dbname}_{each};")
        else: 
            self.cursor.execute(f"drop index if exists idx_{dbname}_{sel_col};")
        for jk_col in jk_cols:
            self.cursor.execute(f"drop index if exists idx_{dbname}_{jk_col};")

        fake_table_name = "fake_" + dbname
        q = f"create table {fake_table_name} ("
        q += ", ".join(k + " " + v for k, v in pgtype.items())
        q += ");"
        self.cursor.execute(q)
        q = f"copy {fake_table_name} from stdin delimiter ',' csv header"
        self.cursor.copy_expert(q, open(file, "r"))

        q = f"create table {dbname} ("
        q += "row_id serial, "
        q += ", ".join(k + " " + v for k, v in pgtype.items())
        q += ");"
        self.cursor.execute(q)

        q = f"insert into {dbname} select nextval('{dbname}_row_id_seq'), * from {fake_table_name}"
        if timestamp_col is not None:
            q += f" order by {timestamp_col} asc;"
        self.cursor.execute(q)
        self.cursor.execute(f"drop table if exists {fake_table_name};")

        if " " in sel_col:
            # for the case where selection is on an expression, e.g., "ss_sales_price / ss_list_price"
            for each in sel_col.split(" "):
                if each.startswith(dbname[0]): # share the same first bit as the table_name
                    self.cursor.execute(f"create index idx_{dbname}_{each} on {dbname}({each});")
        else:
            self.cursor.execute(
                f"create index idx_{dbname}_{sel_col} on {dbname}({sel_col});"
            )
        for jk_col in jk_cols:
            self.cursor.execute(f"create index idx_{dbname}_{jk_col} on {dbname}({jk_col});")
        self.conn.commit()

        self.cursor.execute(f"select count(*) from {dbname};")
        self.cur_table_size = self.cursor.fetchone()[0]


    def clean(self):
        # dbname = self.dbname_prefix + self.name
        # self.cursor.execute(f"drop table if exists {dbname};")
        # self.cursor.execute(f"drop index if exists idx_{dbname}_{self.sel_col};")
        # for jk_col in self.jk_cols:
        #     self.cursor.execute(f"drop index if exists idx_{dbname}_{jk_col};")
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    def setup_single_table_pointer(self):
        _map = get_single_table_pointer(
            sql=self.get_sql_with_range(
                rs=self.sel_by_domain
            )
        )
        if self.abbrev in _map:
            self.pointer = _map[self.abbrev]
        elif self.name in _map:
            self.pointer = _map[self.name]
        else:
            assert True == False

    def nothing_to_flush(self):
        assert self.enable_lazy_tuple_updates
        return len(self.to_insert_buffer) == 0 \
            and self.to_delete_range[0] is None \
                and self.to_delete_range[1] is None
    
    def flush_tuple_updates(self):
        if not self.enable_lazy_tuple_updates:
            return 0.
        if self.nothing_to_flush():
            return 0.
        
        dbname = self.dbname_prefix + self.name

        if len(self.to_insert_buffer) > 0:
            self.cursor.execute(
                f"insert into {dbname} ({', '.join(list(self.pgtype.keys()))}) values " \
                    + ','.join([x.decode('utf-8') for x in self.to_insert_buffer]) \
                    + f" returning {self.sel_col};"
            )

            leo_start_ts = time.time()
            if len(self.leo_set) > 0:
                batch_returned_rows = self.cursor.fetchall()
                assert len(batch_returned_rows) == len(self.to_insert_buffer)

                for returned_row in batch_returned_rows:
                    sel_val = returned_row[0]
                    for i in range(len(self.leo_set)):
                        # self.leo_set[i] = (RangeSelection, card)
                        if (
                            sel_val is not None
                            and self.leo_set[i][0].lb <= sel_val
                            and sel_val <= self.leo_set[i][0].ub
                        ):  # pass the predicate?
                            self.leo_set[i][1] += 1

            self.to_insert_buffer = []
            return time.time() - leo_start_ts
        
        elif self.to_delete_range[0] is not None:
            self.cursor.execute(
                f"delete from {dbname} where row_id >= {self.to_delete_range[0]} and row_id <= {self.to_delete_range[1]}" \
                    + f" returning {self.sel_col};"
            )

            leo_start_ts = time.time()
            if len(self.leo_set) > 0:
                batch_returned_rows = self.cursor.fetchall()
                assert len(batch_returned_rows) == (self.to_delete_range[1] - self.to_delete_range[0] + 1)

                for returned_row in batch_returned_rows:
                    sel_val = returned_row[0]
                    for i in range(len(self.leo_set)):
                        # self.leo_set[i] = (RangeSelection, card)
                        if (
                            sel_val is not None
                            and self.leo_set[i][0].lb <= sel_val
                            and sel_val <= self.leo_set[i][0].ub
                        ):  # pass the predicate?
                            self.leo_set[i][1] -= 1

            self.to_delete_range = [None, None]
            return time.time() - leo_start_ts
        
        return 0.

    def insert(self, table_name, attr_in_str, flush=False):
        assert table_name == self.name
        start_time = time.time()
        
        attr_vals = parse_inserted_field(attr_in_str)
        attr_vals = tuple(attr_vals)
        dbname = self.dbname_prefix + self.name

        if not self.enable_lazy_tuple_updates:
            q = (
                f"insert into {dbname} ("
                + ",".join(self.attrs)
                + ") values ("
                + ",".join(["%s"] * len(self.attrs))
                + f") returning {self.sel_col};"
            )
            self.cursor.execute(q, attr_vals)
            sel_val = self.cursor.fetchone()[0]
        else:
            self.to_insert_buffer.append(
                self.cursor.mogrify("(" + ",".join(['%s'] * len(self.pgtype)) + ")", attr_vals)
            )
            sel_val = None

        self.cur_table_size += 1
        
        leo_start_time = time.time()
        if sel_val is not None and len(self.leo_set) > 0:
            # it is not lazy tuple updates, we can directly get the sel_val and update the leo_set
            for i in range(len(self.leo_set)):
                # self.leo_set[i] = (RangeSelection, card)
                if (
                    sel_val is not None
                    and self.leo_set[i][0].lb <= sel_val
                    and sel_val <= self.leo_set[i][0].ub
                ):  # pass the predicate?
                    self.leo_set[i][1] += 1
        leo_time = time.time() - leo_start_time

        if flush:
            leo_time += self.flush_tuple_updates()

        info = f"leoset_size{self.info_id}={len(self.leo_set)},time{self.info_id}={round(time.time() - start_time, 6)},leo_time{self.info_id}={round(leo_time, 6):.6f}"
        return info

    def delete(self, table_name, id, flush=False):
        assert table_name == self.name
        start_time = time.time()

        dbname = self.dbname_prefix + self.name
        if not self.enable_lazy_tuple_updates:
            q = f"delete from {dbname} where row_id = {id} returning {self.sel_col};"
            self.cursor.execute(q)
            sel_val = self.cursor.fetchone()[0]
        else:
            if self.to_delete_range[0] is None or self.to_delete_range[0] > id:
                self.to_delete_range[0] = id
            if self.to_delete_range[1] is None or self.to_delete_range[1] < id:
                self.to_delete_range[1] = id
            sel_val = None

        self.cur_table_size -= 1

        leo_start_time = time.time()
        if sel_val is not None and len(self.leo_set) > 0:
            for i in range(len(self.leo_set)):
                # self.leo_set[i] = (RangeSelection, card)
                if (
                    sel_val is not None
                    and self.leo_set[i][0].lb <= sel_val
                    and sel_val <= self.leo_set[i][0].ub
                ):  # pass the predicate?
                    self.leo_set[i][1] -= 1
        leo_time = time.time() - leo_start_time

        if flush:
            leo_time += self.flush_tuple_updates()

        info = f"leoset_size{self.info_id}={len(self.leo_set)},time{self.info_id}={round(time.time() - start_time, 6)},leo_time{self.info_id}={round(leo_time, 6):.6f}"
        return info

    def get_error(self):
        true_cards = [self.leo_set[i][1] for i in range(len(self.leo_set))]
        if len(true_cards) == 0:
            return 0
        if self.error_metric == "avg":
            return get_average_q_error(true_cards, self.preds)
        elif self.error_metric == "90th":
            return get_percentile_q_error(true_cards, self.preds, 90)
        else:
            raise NotImplementedError

    def get_sql_with_range(self, rs):
        return self.sql.replace("{lb" + str(self.info_id) + "}", str(rs.lb)).replace("{ub" + str(self.info_id) + "}", str(rs.ub))

    def insert_to_leoset(self, rs, true_card, model_pred):
        if true_card > 0 and 1.0 * abs(model_pred - true_card) / true_card > 0.05:
            self.leo_set.append([rs, true_card])
            self.preds.append(model_pred)
        self._query_id += 1

    def query(self, rs, true_card):
        assert not self.enable_lazy_tuple_updates or self.nothing_to_flush()
        start_time = time.time()
        assert rs.table_name == self.name

        model_pred = black_box.predict_one(
            self.name,
            [rs.lb, rs.ub],
            [f"{self.name} {self.abbrev}"],
            [""],
        )
        adj_model_pred = model_pred

        max_overlap_ratio, which, which_true_card = None, None, None
        for _i in range(len(self.leo_set)):
            leo_rs = self.leo_set[_i][0]
            # length of intersection / length of union
            if max(rs.ub, leo_rs.ub) - min(rs.lb, leo_rs.lb) == 0:
                overlap_ratio = 0.
            else:
                overlap_ratio = (max(0, min(rs.ub, leo_rs.ub) - max(rs.lb, leo_rs.lb))) / (max(rs.ub, leo_rs.ub) - min(rs.lb, leo_rs.lb))
            # 0 means non-overlapping at all; 1 means identical
            if which is None or max_overlap_ratio < overlap_ratio:
                which = leo_rs
                which_true_card = self.leo_set[_i][1]
                max_overlap_ratio = overlap_ratio
        if which is not None and max_overlap_ratio >= self.overlap_ratio_lb:
            # let's do the correction: replace the overlap with the true card
            # adj_model_pred += 1. * (max(0, min(rs.ub, which.ub) - max(rs.lb, which.lb))) / (which.ub - which.lb) * (self.leo_set[which].true_card - self.leo_set[which].pred)

            adj_model_pred = max(0, adj_model_pred - black_box.predict_one(self.name, [max(rs.lb, which.lb), min(rs.ub, which.ub)], [f"{self.name} {self.abbrev}"], [""])) \
                + 1. * (max(0, min(rs.ub, which.ub) - max(rs.lb, which.lb))) / (which.ub - which.lb) * which_true_card
            adj_model_pred = round(adj_model_pred)
            adj_model_pred = max(0, min(adj_model_pred, self.cur_table_size))

        leo_time = time.time() - start_time
        q = self.get_sql_with_range(rs)

        # inject the "adj_model_pred" and get the plan info
        _, join_order, scan_mtd = inject_single_table_sels_and_get_cost(
            pointer=self.pointer,
            sel=adj_model_pred / self.cur_table_size,
            n_tabs_in_from=self.n_tabs_in_from,
            q=q,
            hint=None,
            plan_info=True,
        ) 

        # construct the plan by the info
        inj_plan = gen_final_hint(scan_mtd=scan_mtd, str=join_order)

        # lets run it!
        _, execution_time, planning_time, model_name_to_have = get_real_latency(
            sql=q,
            hint=inj_plan,
            if_have=[self.name, self.abbrev],
        )

        # we cost the plan by the true_card, which is not counted as the cost 
        # of Leo1D. Because this info is just for reporting, but not utilized
        # by the algorithm
        plan_cost = inject_single_table_sels_and_get_cost(
            pointer=self.pointer,
            sel=true_card / self.cur_table_size,
            n_tabs_in_from=self.n_tabs_in_from,
            q = q,
            hint=inj_plan,
            plan_info=False,
        )

        start_time_2 = time.time()
        self.insert_to_leoset(rs, true_card, model_pred)
        leo_time += time.time() - start_time_2

        info = f"leoset_size{self.info_id}={len(self.leo_set)}" 
        if which is not None and max_overlap_ratio >= self.overlap_ratio_lb:
            info += f",corrected_card{self.info_id}={adj_model_pred}"
        info += f",plan_cost{self.info_id}={plan_cost}"
        info += f",execution_time{self.info_id}={round(execution_time / 1000., 6):.6f}"
        info += f",leo_time{self.info_id}={round(leo_time, 6):0.6f}"
        info += f",got_true_card{self.info_id}="
        if (self.name in model_name_to_have and model_name_to_have[self.name]) or (self.abbrev in model_name_to_have and model_name_to_have[self.abbrev]):
            info += "True"
        else:
            info += "False"

        hint_wo_newline = inj_plan.replace('\n', '')
        info += f",plan{self.info_id}={hint_wo_newline}"

        return (
            np.round(adj_model_pred, 6),
            get_average_q_error([true_card], [adj_model_pred]),
            info,
        )

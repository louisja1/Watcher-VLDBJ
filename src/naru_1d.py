import csv
import os
import copy

from tqdm import tqdm
import time
import numpy as np
import black_box
import random
import json
import sys
from operation import TupleUpdateType, RangeSelection
import warnings
from connection import get_connection, close_connection
from error_metrics import get_average_q_error
from pg_hint_utility import gen_final_hint, get_real_latency, inject_single_table_sels_and_get_cost, get_single_table_pointer

warnings.filterwarnings("ignore")

class Naru1D:
    def __init__(
        self,
        name=None,
        conn=None,
        cursor=None,
        sql=None,
        fetch_snapshot_sql=None,
        random_seed=None,
        update_strategy=None,
        based_on=None,
        X=None,
        info_id=None,
        sel_by_domain=None,
        assigned_alias=None,
    ):
        self.name = name
        if assigned_alias is not None:
            self.abbrev = assigned_alias
        else:
            self.abbrev = ""
            for piece in name.strip().split("_"):
                self.abbrev += piece[0]
        
        self.model_name = self.abbrev

        self.conn = conn
        self.cursor = cursor

        self.dbname_prefix = ""

        self.sql = sql
        assert self.sql is not None
        self.n_tabs_in_from = sql.lower().split("from")[1].split("where")[0].count(",") + 1
        self.fetch_snapshot_sql = fetch_snapshot_sql
        assert self.fetch_snapshot_sql is not None

        if random_seed is not None:
            random.seed(random_seed)
        
        self.update_strategy = update_strategy

        self.based_on = based_on
        assert self.based_on in ["tuples"]
        self.X = X
        assert isinstance(self.X, list)

        self.info_id = info_id
        self.sel_by_domain = sel_by_domain

        self._query_id = 0
        self.op_cnts = {"tuples": 0, "queries": 0}
        self.xid = 0

        self.naru_csv_filename = "naru/datasets/" + self.model_name + ".csv"
        self.start_to_record_incremental_content = False
        self.incremental_content = []

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
        # self.cursor.execute(f"drop table if exists {self.dbname};")
        # self.cursor.execute(f"drop index if exists idx_{self.dbname}_{self.sel_col};")
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

        if os.path.exists(self.naru_csv_filename):
            os.remove(self.naru_csv_filename)
        else:
            assert True == False
    

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

    def check_retrain(self):
        check_start_time = time.time()
        info = ""

        cur_n_ops = None
        if self.X is not None and self.xid < len(self.X):
            cur_n_ops = self.op_cnts[self.based_on]
        check_time = time.time() - check_start_time

        if cur_n_ops is not None and cur_n_ops == self.X[self.xid]:
            self.xid += 1
            retrain_time = 0.
            training_set_collecting_time = self.get_training_set()
            retrain_time += training_set_collecting_time

            retrain_start_time = time.time()
            black_box.naru_retrain(
                self.model_name,
                cols=[self.sel_col]
            )
            retrain_time += time.time() - retrain_start_time
            return check_time, True, info, retrain_time
        return check_time, False, None, None

    def get_training_set(self):
        start_time = time.time()

        if self.update_strategy == "retrain" or (
            self.update_strategy == "incremental_on_inserts_only" 
            and self.start_to_record_incremental_content == False
        ):
            self.cursor.execute(self.fetch_snapshot_sql)
            training_set = self.cursor.fetchall()
        else:
            training_set = copy.deepcopy(self.incremental_content)

        csv_header = [self.sel_col]
        with open(self.naru_csv_filename, "w") as fout:
            writer = csv.writer(fout)
            writer.writerow(csv_header)
            for row in training_set:
                writer.writerow(["None" if val is None else val for val in row])
        
        if self.update_strategy == "incremental_on_inserts_only":
            if not self.start_to_record_incremental_content:
                self.start_to_record_incremental_content = True
                self.incremental_content = copy.deepcopy(training_set) # initialize the incremental content by the current training set, and then it will be updated by the new insertions
            else:
                # do nothing: we just keep the incremental_content updated by the new insertions
                pass

        return time.time() - start_time

    def insert(self, name, attr_in_str):
        assert name == self.name
        start_time = time.time()

        self.op_cnts["tuples"] += 1
        attr_vals = []
        for x in attr_in_str.split(","):
            if x == "None":
                attr_vals.append(None)
            else:
                attr_vals.append(x)
        attr_vals = tuple(attr_vals)
        dbname = self.dbname_prefix + self.name

        q = (
            f"insert into {dbname} ("
            + ",".join(self.attrs)
            + ") values ("
            + ",".join(["%s"] * len(self.attrs))
            + f") returning {self.sel_col};"
        )
        self.cursor.execute(q, attr_vals)

        baseline_start_ts = time.time()
        if self.start_to_record_incremental_content:
            returned_row = self.cursor.fetchone()
            if returned_row is not None and returned_row[0] is not None:
                self.incremental_content.append((returned_row[0],))
        baseline_time = time.time() - baseline_start_ts
        self.cur_table_size += 1
        
        check_time, if_retrain, retrain_info, retrain_time = self.check_retrain()
        if if_retrain:
            baseline_time += check_time
        info = f"time{self.info_id}={round(time.time() - start_time, 6)},baseline_time{self.info_id}={round(baseline_time, 6):.6f}"
        if if_retrain:
            info += retrain_info + f",retrain_time{self.info_id}={round(retrain_time, 6):.6f}"
        return info

    def delete(self, name, id):
        assert name == self.name
        start_time = time.time()

        self.op_cnts["tuples"] += 1
        dbname = self.dbname_prefix + self.name
        q = f"delete from {dbname} where row_id = {id} returning {self.sel_col};"
        self.cursor.execute(q)
        self.cur_table_size -= 1

        check_time, if_retrain, retrain_info, retrain_time = self.check_retrain()

        baseline_time = 0.
        if if_retrain:
            baseline_time += check_time
        info = f"time{self.info_id}={round(time.time() - start_time, 6)},baseline_time{self.info_id}={round(baseline_time, 6):.6f}"
        if if_retrain:
            info += retrain_info + f",retrain_time{self.info_id}={round(retrain_time, 6):.6f}"
        return info
    
    def get_sql_with_range(self, rs):
        return self.sql.replace("{lb" + str(self.info_id) + "}", str(rs.lb)).replace("{ub" + str(self.info_id) + "}", str(rs.ub))

    def query(self, rs, true_card):
        start_time = time.time()
        assert rs.table_name == self.name
        naru_to_predict_cols = [self.sel_col, self.sel_col]
        naru_to_predict_ops = [">=", "<="]
        naru_to_predict_vals = [rs.lb, rs.ub]

        self.op_cnts["queries"] += 1

        model_pred = black_box.naru_predict_one(
            self.model_name,
            cols=naru_to_predict_cols,
            ops=naru_to_predict_ops,
            vals=naru_to_predict_vals,
        )
        baseline_time = time.time() - start_time
        q = self.get_sql_with_range(rs)

        # inject the "model_pred" and get the plan info
        _, join_order, scan_mtd = inject_single_table_sels_and_get_cost(
            pointer=self.pointer,
            sel=model_pred / self.cur_table_size,
            n_tabs_in_from=self.n_tabs_in_from,
            q=q,
            hint=None,
            plan_info=True,
        ) 

        # construct the plan by the info
        inj_plan = gen_final_hint(scan_mtd=scan_mtd, str=join_order)

        # lets run it!
        _, execution_time, planning_time = get_real_latency(
            sql=q,
            hint=inj_plan,
        )

        # we cost the plan by the true_card, which is not counted as the cost 
        # of Baseline1D. Because this info is just for reporting, but not utilized
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
        baseline_time += time.time() - start_time_2

        info = f"plan_cost{self.info_id}={plan_cost}"
        info += f",execution_time{self.info_id}={round(execution_time / 1000., 6):.6f}"
        info += f",baseline_time{self.info_id}={round(baseline_time, 6):0.6f}"
        
        hint_wo_newline = inj_plan.replace('\n', '')
        info += f",plan{self.info_id}={hint_wo_newline}"

        return (
            np.round(model_pred, 6),
            get_average_q_error([true_card], [model_pred]),
            info,
        )

def load_trainingset(
    tabs_for_naru1d,
    naru1ds,
):
    print("Initial training:")
    for tab in tabs_for_naru1d:
        training_set_collection_time = naru1ds[tab].get_training_set()
        retrain_start_ts = time.time()
        black_box.naru_retrain(
            naru1ds[tab].model_name,
            cols=[naru1ds[tab].sel_col]
        )
        retrain_time = time.time() - retrain_start_ts
        print("Finish training " + naru1ds[tab].model_name + f" in {round(training_set_collection_time + retrain_time, 6):.6f} seconds")

def load_log(
    conn,
    cursor,
    log_filename,
    output_prefix,
    n_tabs,
    sel_cols,
    tabs_for_naru1d,
    naru1ds,
    pgtypes,
):
    print("Load Log")
    n_tu = 0
    total_tu_time = 0.0
    total_q_time = 0.0

    to_insert_buffer = []
    to_delete_range = [None, None]

    last_op_type = None
    last_tab = None

    with open(log_filename, "r") as fin, open(
        output_prefix + "_answer.txt", "w"
    ) as fout:
        for row_num, line in enumerate(tqdm(fin)):
            op_type = line[0]
            if op_type == "Q":
                tab = None
            else:
                tab = line.split(",")[1]
            # we flush the tuple updates for non-baseline tables
            if (last_op_type != op_type or last_tab != tab) and (last_tab not in tabs_for_naru1d) and (last_op_type != "Q"):
                if last_op_type == "I" and len(to_insert_buffer) > 0:
                    cursor.execute(f"insert into {last_tab} ({', '.join(list(pgtypes[last_tab].keys()))}) values " + ','.join([x.decode('utf-8') for x in to_insert_buffer]))
                    # print(f"flush {len(to_insert_buffer)} insertions to {last_tab}")
                    to_insert_buffer = []
                if last_op_type == "D" and to_delete_range[0] is not None:
                    cursor.execute(f"delete from {last_tab} where row_id >= {to_delete_range[0]} and row_id <= {to_delete_range[1]};")
                    # print(f"flush {to_delete_range[1] - to_delete_range[0] + 1} deletions to {last_tab}")
                    to_delete_range = [None, None]
            if last_op_type != "Q" and op_type == "Q":
                # # TODO
                # pass
                cursor.execute("vacuum (full, analyze);")
            last_op_type, last_tab = op_type, tab

            ret = str(row_num) + ":"
            if op_type in ["I", "D"]:
                start_tu_ts = time.time()
                n_tu += 1
                _type = TupleUpdateType.from_str(line.split(",")[0])
                t = line.split(",")[1]
                field = line[2 + len(t) + 1 :].strip()
                if t not in tabs_for_naru1d:
                    total_tu_time += time.time() - start_tu_ts
                    if _type == TupleUpdateType.INSERT:
                        # q = (
                        #     f"insert into {t} ("
                        #     + ",".join(pgtypes[t])
                        #     + ") values ("
                        #     + ",".join(["%s"] * len(pgtypes[t]))
                        #     + f");"
                        # )
                        attr_vals = []
                        for x in field.split(","):
                            if x == "None":
                                attr_vals.append(None)
                            else:
                                attr_vals.append(x)
                        attr_vals = tuple(attr_vals)
                        to_insert_buffer.append(cursor.mogrify("(" + ",".join(['%s'] * len(pgtypes[t])) + ")", attr_vals))
                    elif _type == TupleUpdateType.DELETE:
                        # q = f"delete from {t} where row_id = {int(field)};"
                        # cursor.execute(q)
                        row_id = int(field)
                        if to_delete_range[0] is None or to_delete_range[0] > row_id:
                            to_delete_range[0] = row_id
                        if to_delete_range[1] is None or to_delete_range[1] < row_id:
                            to_delete_range[1] = row_id
                    fout.write(ret + f"time={round(time.time() - start_tu_ts, 6):.6f}\n")
                    continue

                if _type == TupleUpdateType.INSERT:
                    ret += naru1ds[t].insert(t, field)
                elif _type == TupleUpdateType.DELETE:
                    ret += naru1ds[t].delete(t, int(field))
                total_tu_time += time.time() - start_tu_ts

            elif op_type == "Q":
                row = line.strip().split(",")
                for jj in range(n_tabs):
                    if row[1 + jj] in tabs_for_naru1d:
                        tab = row[1 + jj]
                        lb_id = 1 + n_tabs + 2 * jj
                        ub_id = lb_id + 1
                        card_id = 1 + n_tabs * 3 + jj
                        _col = list(sel_cols[tab].keys())[0]
                        if "/" in _col:
                            lb, ub = float(row[lb_id]), float(row[ub_id])
                        elif pgtypes[tab][_col].lower() == "real" or pgtypes[tab][_col].lower().startswith("decimal"):
                            lb, ub = float(row[lb_id]), float(row[ub_id])
                        elif pgtypes[tab][_col].lower() == "integer" or pgtypes[tab][_col].lower() == "smallint":
                            lb, ub = int(row[lb_id]), int(row[ub_id])
                        else:
                            raise NotImplementedError
                        true_card = int(row[card_id])

                        rs = RangeSelection(tab, lb, ub)
                        rs.update_by(
                            sel_cols[tab][_col]["min"], sel_cols[tab][_col]["max"]
                        )

                        start_q_ts = time.time()
                        est, single_err, info = naru1ds[tab].query(rs, true_card)
                        total_q_time += time.time() - start_q_ts

                        if ret[-1] != ":":
                            ret += ","
                        info_id = naru1ds[tab].info_id
                        ret += f"est{info_id}=" + str(est) + ","
                        ret += f"observed_err{info_id}=" + str(single_err)

                        if len(info) > 0:
                            ret += "," + info
            else:
                raise NotImplementedError
            fout.write(ret + "\n")

        with open(output_prefix + "_time.txt", "w") as fout:
            fout.write(f"Total TU time: {total_tu_time}\n")
            fout.write(f"Total Q time: {total_q_time}\n")

def load_non_watch_table(conn, cursor, table_name, file, jk_cols, pgtypes, timestamp_col=None):
    cursor.execute(f"drop table if exists {table_name};")
    for jk_col in jk_cols:
        cursor.execute(f"drop index if exists idx_{table_name}_{jk_col};")

    fake_table_name = "fake_" + table_name
    q = f"create table {fake_table_name} ("
    q += ", ".join(k + " " + v for k, v in pgtypes.items())
    q += ");"
    cursor.execute(q)
    q = f"copy {fake_table_name} from stdin delimiter ',' csv header"
    cursor.copy_expert(q, open(file, "r"))

    q = f"create table {table_name} ("
    q += "row_id serial, "
    q += ", ".join(k + " " + v for k, v in pgtypes.items())
    q += ");"
    cursor.execute(q)

    q = f"insert into {table_name} select nextval('{table_name}_row_id_seq'), * from {fake_table_name}"
    if timestamp_col is not None:
        q += f" order by {timestamp_col} asc;"
    cursor.execute(q)
    cursor.execute(f"drop table if exists {fake_table_name};")

    for jk_col in jk_cols:
        cursor.execute(
            f"create index idx_{table_name}_{jk_col} on {table_name}({jk_col});"
        )

if __name__ == "__main__":
    json_filename = sys.argv[1]
    with open(json_filename, "r") as json_fin:
        config = json.load(json_fin)
        tabs = config["tables"]
        if "static_tables" in config:
            static_tabs = config["static_tables"]
        else:
            static_tabs = []

        if "algorithm" in config:
            algorithm = config["algorithm"]
            assert algorithm == "naru"
            black_box.config["algorithm"] = algorithm

        sel_cols = config["sel_cols"]
        timestamp_cols = config["timestamp_cols"]
        jk_cols = config["jk_cols"]
        sql = config["sql"]
        fetch_snapshot_sql = config["fetch_snapshot_sql"]
        pgtypes = config["pgtypes"]

        update_strategy = config["update_strategy"]
        assert update_strategy in ["retrain", "incremental_on_inserts_only"]
        # retrain is fully rebuilding; 
        # incremental_on_inserts_only is only incrementally updating the model by the new insertions by ignoring the deletes

        if "training_epochs" in config:
            training_epochs = config["training_epochs"]
            black_box.config["training_epochs"] = training_epochs

        if update_strategy == "retrain":
            assert "incremental_epochs" not in config
        elif update_strategy == "incremental_on_inserts_only":
            assert "incremental_epochs" in config
            incremental_epochs = config["incremental_epochs"]
            black_box.config["incremental_epochs"] = incremental_epochs
        
        update_based_on = config["update_based_on"]
        update_after = config["update_after"]
        # for example, update_based_on = "tuples" or "queries"
        # update_after = [X1, X2, X3, ...]
        # Xi means the number of tuple updates happen on any table in "join_to_watch"

        debug = config["debug"]
        table_filenames = config["table_filenames"]
        log_filename = config["log_filename"]

        output_prefix = config["output_prefix"]
        if debug:
            output_prefix = "/".join(output_prefix.split("/")[:-1]) + "/test"
        else:
            output_prefix += "_naru-" 
            if update_strategy == "retrain":
                output_prefix += "retrain"
            else:
                output_prefix += "incre"
            
            output_prefix += "["
            output_prefix += ",".join(
                [f"{k}-after-" + "|".join([str(x) for x in update_after[k]]) + f"-{update_based_on}" for k in update_after]
            )
            output_prefix += "]"

        # get db connection
        conn, cursor = get_connection()
        # load the static tables
        for static_tab in static_tabs:
            load_non_watch_table(
                conn=conn,
                cursor=cursor,
                table_name=static_tab,
                file=table_filenames[static_tab],
                jk_cols=jk_cols[static_tab],
                pgtypes=pgtypes[static_tab],
                timestamp_col=None,
            )

        # we only need to build Naru1D for tables with selections
        tabs_for_naru1d = list(sel_cols.keys())
        naru1ds = {}
        tab_to_alias = {}
        for ii in range(len(tabs)):
            if (" " in tabs[ii] or "as" in tabs[ii]):
                # there is an assigned alias name
                _tab = tabs[ii].split(" ")[0]
                assigned_alias = tabs[ii].split(" ")[-1]
                tabs[ii] = _tab
                tab_to_alias[_tab] = assigned_alias
            else:
                assigned_alias = None
            tab = tabs[ii]
            if tab in tabs_for_naru1d:
                naru1ds[tab] = Naru1D(
                    name=tab,
                    conn=conn,
                    cursor=cursor,
                    sql=sql,
                    fetch_snapshot_sql=fetch_snapshot_sql,
                    random_seed=2023,
                    update_strategy=update_strategy,
                    based_on=update_based_on,
                    X=update_after[tab],
                    info_id=ii + 1, # 1-base info ids
                    sel_by_domain=RangeSelection( # only utilized to get the pointer for single table
                        table_name=tab,
                        lb=sel_cols[tab][list(sel_cols[tab].keys())[0]]["min"],
                        ub=sel_cols[tab][list(sel_cols[tab].keys())[0]]["max"]
                    ),
                    assigned_alias=assigned_alias,
                )
                naru1ds[tab].load_table(
                    file=table_filenames[tab],
                    # we only support one sel col per table for now
                    sel_col=list(sel_cols[tab].keys())[0],
                    jk_cols=jk_cols[tab],
                    pgtype=pgtypes[tab],
                    timestamp_col=timestamp_cols[tab],
                )
            else:
                load_non_watch_table(
                    conn=conn,
                    cursor=cursor,
                    table_name=tab,
                    file=table_filenames[tab],
                    jk_cols=jk_cols[tab],
                    pgtypes=pgtypes[tab],
                    timestamp_col=timestamp_cols[tab],
                )

        # analyze
        cursor.execute("vacuum (full, analyze);")

        # setup the single table pointers
        for tab in naru1ds:
            naru1ds[tab].setup_single_table_pointer()

        load_trainingset(
            tabs_for_naru1d=tabs_for_naru1d,
            naru1ds=naru1ds,
        )

        load_log(
            conn,
            cursor,
            log_filename,
            output_prefix,
            len(tabs),
            sel_cols,
            tabs_for_naru1d,
            naru1ds,
            pgtypes,
        )

        for tab in tabs_for_naru1d:
            naru1ds[tab].clean()

        close_connection(conn=conn, cursor=cursor)

import csv
import os
import random
import resource
import time
import black_box
import time
import numpy as np
import copy
import sys
from error_metrics import get_average_q_error, get_percentile_q_error
from pg_hint_utility import inject_single_table_sels_and_get_cost, inject_single_and_join_sels_and_get_cost, inject_true_cards_and_get_cost, gen_final_hint, get_real_latency, get_single_table_pointer
from operation import QueryInfo, TupleUpdateType
from utility import parse_inserted_field


def _deep_getsizeof(obj, seen=None):
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)

    size = sys.getsizeof(obj)

    if isinstance(obj, dict):
        size += sum(_deep_getsizeof(key, seen) + _deep_getsizeof(value, seen) for key, value in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(_deep_getsizeof(item, seen) for item in obj)
    elif hasattr(obj, "__dict__"):
        size += _deep_getsizeof(vars(obj), seen)
    elif hasattr(obj, "__slots__"):
        size += sum(
            _deep_getsizeof(getattr(obj, slot), seen)
            for slot in obj.__slots__
            if hasattr(obj, slot)
        )

    return size


def _peak_rss_bytes():
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return peak_rss
    return peak_rss * 1024

class TwoTierWatcher1D:
    def __init__(
        self,
        name=None,
        conn=None,
        cursor=None,
        query_pool_size=black_box.config["training_size"], # this is the size of query_pool.
        training_size=black_box.config["training_size"],
        sql=None,
        triggers=None,
        random_seed=None,
        execution_time_lb=None, # Watchset: execution_time >= execution_time_lb; If None, this check always fails;
        planning_time_ub=None, # Watchset: 1. if planning_time_ub is a 'int': planning_time <= planning_time_ub; 2. If None, this checks always fails; 3. if planning_time_ub is a percentage: planning_time <= execution_time * planning_time_ub
        # And we need to make sure that execution_time_lb >= planning_time_ub
        plancost_check_ratio=None, # Watchset: pc(pred) >= pc(true) * plancost_check_ratio; If None, this check always fails; And we need to ensure that plancost_check_ratio >= 1
        overlap_ratio_lb=None, # We will do the correction only when overlap_ratio, i.e., overlap_ratio >= overlap_ratio_lb; And we need to ensure that overlap_ratio in [0., 1.] 
        enable_lazy_tuple_updates=False, # If True: TwoTierWatcher1D will postpone the tuple updates till we really need them (a retraining is triggered, a refill is needed, different type of tuple updates show up)
        enable_correct_the_joins=False, # If True: the join cardinality of the plan nodes where table 'self.name' is involved are also corrected
        correct_exactly_ntabsjoin=None, # This is useful only when enable_correct_the_joins=True, which means we only correct join cards where there are exactly X tables involved in the joins
        debug_show_all_correction_factors=False, # DEBUG: show all correction factors
        debug_print_the_monitored_part=False,
        info_id=None,
        sel_by_domain=None,
        assigned_alias=None,
        update_strategy=None, # for Naru only
        fetch_snapshot_sql=None, # for Naru only
        track_memory_usage=False,
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
        self.query_pool_size = query_pool_size
        self.training_size = training_size
        if random_seed is not None:
            random.seed(random_seed)
        self.triggers = triggers

        self.sql = sql
        assert self.sql is not None
        self.n_tabs_in_from = sql.lower().split("from")[1].split("where")[0].count(",") + 1

        if update_strategy is not None:
            # its naru + incremental update
            assert black_box.config["algorithm"] == "naru"
            assert fetch_snapshot_sql is not None
            self.is_naru = True
            self.update_strategy = update_strategy
            self.fetch_snapshot_sql = fetch_snapshot_sql
            
            self.naru_model_name = "twotier_" + self.abbrev
            self.naru_csv_filename = "naru/datasets/" + self.naru_model_name + ".csv"
            self.start_to_record_incremental_content = False
            self.incremental_content = []
        else:
            self.is_naru = False

        self.execution_time_lb = execution_time_lb
        self.planning_time_ub = planning_time_ub
        if isinstance(self.planning_time_ub, str):
            assert self.planning_time_ub.endswith("%")
            try:
                self.planning_time_ub = float(self.planning_time_ub.split("%")[0]) / 100.
            except ValueError:
                print("planning_time_ub is not a percentage")
                assert True == False
            self.planning_time_ub_is_percentage = True
        else:
            self.planning_time_ub_is_percentage = False

        assert (self.execution_time_lb is None and self.planning_time_ub is None) \
            or (not self.planning_time_ub_is_percentage and self.execution_time_lb >= self.planning_time_ub) \
                or (self.planning_time_ub_is_percentage and self.planning_time_ub <= 100.)
        
        self.plancost_check_ratio = plancost_check_ratio
        assert self.plancost_check_ratio is None or self.plancost_check_ratio >= 1.
        self.overlap_ratio_lb = overlap_ratio_lb
        assert self.overlap_ratio_lb is not None and self.overlap_ratio_lb >= 0. and self.overlap_ratio_lb <= 1.

        self.enable_lazy_tuple_updates = enable_lazy_tuple_updates
        if self.enable_lazy_tuple_updates:
            self.to_insert_buffer = []
            self.to_delete_range = [None, None]

        self.enable_correct_the_joins = enable_correct_the_joins
        if self.enable_correct_the_joins:
            self.correct_exactly_ntabsjoin = correct_exactly_ntabsjoin
            assert isinstance(self.correct_exactly_ntabsjoin, int) # we only support correct one X for all X-way joins

        self.debug_show_all_correction_factors = debug_show_all_correction_factors
        self.debug_print_the_monitored_part = debug_print_the_monitored_part

        self.info_id = info_id
        self.sel_by_domain = sel_by_domain

        self.query_pool = [] # [rs, ...]
        self.watch_set = {} # {rs -> QueryInfo}

        self.query_pool_query_id = 0

        self.track_memory_usage = track_memory_usage
        if self.track_memory_usage:
            self.peak_memory_bytes = {
                "watcher": 0,
                "watch_set": 0,
                "query_pool": 0,
                "process_rss": 0,
            }
            self._record_memory_peak()

    def _current_memory_snapshot(self):
        watcher_payload = {
            key: value
            for key, value in self.__dict__.items()
            if key not in {"conn", "cursor", "peak_memory_bytes"}
        }
        return {
            "watcher": _deep_getsizeof(watcher_payload),
            "watch_set": _deep_getsizeof(self.watch_set),
            "query_pool": _deep_getsizeof(self.query_pool),
            "process_rss": _peak_rss_bytes(),
        }

    def _record_memory_peak(self):
        if not self.track_memory_usage:
            return

        current_snapshot = self._current_memory_snapshot()
        for key, value in current_snapshot.items():
            if value > self.peak_memory_bytes[key]:
                self.peak_memory_bytes[key] = value

    def get_memory_usage_info(self):
        if not self.track_memory_usage:
            return None

        current_snapshot = self._current_memory_snapshot()
        return {
            "current": current_snapshot,
            "peak": copy.deepcopy(self.peak_memory_bytes),
        }

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
        dbname = self.dbname_prefix + self.name
        # self.cursor.execute(f"drop table if exists {dbname};")
        # self.cursor.execute(f"drop index if exists idx_{dbname}_{self.sel_col};")
        # for jk_col in self.jk_cols:
        #     self.cursor.execute(f"drop index if exists idx_{dbname}_{jk_col};")
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

        if self.is_naru:
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

            watcher_start_ts = time.time()
            # Lazy tuple updates: we get the sel_val of each inserted tuple only after we flush the insertions, and then we can update the watchset based on these sel_vals
            if len(self.watch_set) > 0 \
                or (self.is_naru and self.start_to_record_incremental_content): 
                # at least one of the two conditions is true, we need to go through the returned sel_vals to update the watchset or the incremental content
                
                batch_returned_rows = self.cursor.fetchall()
                assert len(batch_returned_rows) == len(self.to_insert_buffer)

                for returned_row in batch_returned_rows:
                    sel_val = returned_row[0]
                    if sel_val is not None:
                        for rs in self.watch_set:
                            if (
                                rs.lb <= sel_val
                                and sel_val <= rs.ub
                            ):  # pass the predicate? card ++ 
                                self.watch_set[rs].true_card += 1

                        if self.is_naru and self.start_to_record_incremental_content:
                            self.incremental_content.append((sel_val,))
            
            self.to_insert_buffer = []
            return time.time() - watcher_start_ts
        elif self.to_delete_range[0] is not None:
            self.cursor.execute(
                f"delete from {dbname} where row_id >= {self.to_delete_range[0]} and row_id <= {self.to_delete_range[1]}" \
                    + f" returning {self.sel_col};"
            )

            watcher_start_ts = time.time()
            # Lazy tuple updates: we get the sel_val of each deleted tuple only after we flush the deletions, and then we can update the watchset based on these sel_vals
            if len(self.watch_set) > 0:
                batch_returned_rows = self.cursor.fetchall()
                assert len(batch_returned_rows) == self.to_delete_range[1] - self.to_delete_range[0] + 1

                for returned_row in batch_returned_rows:
                    sel_val = returned_row[0]
                    if sel_val is not None:
                        for rs in self.watch_set:
                            if (
                                rs.lb <= sel_val
                                and sel_val <= rs.ub
                            ):  # pass the predicate?
                                self.watch_set[rs].true_card -= 1
            
            self.to_delete_range = [None, None]
            return time.time() - watcher_start_ts
        return 0.

    def get_training_set(self):
        assert not self.enable_lazy_tuple_updates or self.nothing_to_flush()
        
        start_time = time.time()

        if black_box.config["algorithm"] == "postgres": 
            return time.time() - start_time, None
        elif not self.is_naru:
            # MSCN's inteface for retraining: [tables], [joins], [lb,ub,card]
            training_set = []

            if len(self.watch_set) > 0:
                all_rss_from_watchset = list(self.watch_set.keys())
                random.shuffle(all_rss_from_watchset)
                for i in range(min(len(self.watch_set), self.training_size)):
                    rs = all_rss_from_watchset[i]
                    training_set.append((rs.lb, rs.ub, self.watch_set[rs].true_card))
                
            if len(training_set) < self.training_size:
                remaining_size = self.training_size - len(training_set)
                sample = random.sample(self.query_pool, remaining_size)
                dbname = self.dbname_prefix + self.name
                for rs in sample:
                    # we only support selection on a single column for now
                    q = (
                        f"select count(*) from "
                        + dbname
                        + " where "
                        + f"{dbname}.{self.sel_col} >= {rs.lb}"
                        + " and "
                        + f"{dbname}.{self.sel_col} <= {rs.ub}"
                        + ";"
                    )
                    self.cursor.execute(q)
                    training_set.append((rs.lb, rs.ub, self.cursor.fetchone()[0]))
            return (
                time.time() - start_time,
                (
                    [f"{self.name} {self.abbrev}"],
                    [""],
                    training_set,
                )
            )
        else:
            if (
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

            return time.time() - start_time, None


    def check_retrain(self):
        check_start_time = time.time()
        info = ""

        err = None
        cur_watchset_size = None

        assert len(self.triggers) == 0 or (not self.enable_lazy_tuple_updates)
        # for now, we do not support lazy tuple updates + triggers at the same time.
        # for example, if it is a watchset_err trigger, the current watch_set is not up-to-date before we flush the tuple updates.

        for trigger in self.triggers:
            if trigger == "watchset_err":
                err = self.get_error()
            elif trigger == "watchset_size":
                cur_watchset_size = len(self.watch_set)
        check_time = time.time() - check_start_time

        if err is not None and err > self.threshold:
            check_time += self.flush_tuple_updates() if self.enable_lazy_tuple_updates else 0.

            retrain_time = 0.
            while err > self.threshold:
                training_set_collecting_time, training_info = self.get_training_set()
                retrain_time += training_set_collecting_time

                retrain_start_time = time.time()
                if black_box.config["algorithm"] == "postgres":
                    dbname = self.dbname_prefix + self.name
                    black_box.pg_retrain(self.cursor, dbname)
                elif not self.is_naru:
                    black_box.retrain(self.name, *training_info)
                else:
                    black_box.naru_retrain(self.naru_model_name, cols=[self.sel_col])

                for rs in self.watch_set:
                    if black_box.config["algorithm"] == "postgres":
                        dbname = self.dbname_prefix + self.name
                        self.watch_set[rs].pred = black_box.pg_predict_one(
                            self.cursor, dbname, self.sel_col, rs.lb, rs.ub
                        )
                    elif not self.is_naru:
                        self.watch_set[rs].pred = black_box.predict_one(
                            self.name,
                            [rs.lb, rs.ub],
                            [f"{self.name} {self.abbrev}"],
                            [""],
                        )
                    else:
                        self.watch_set[rs].pred = black_box.naru_predict_one(
                            self.naru_model_name,
                            cols=[self.sel_col, self.sel_col],
                            ops=[">=", "<="],
                            vals=[rs.lb, rs.ub],
                        )
                
                if len(info) == 0:
                    info = ","
                    
                info += "retrain_"
                err = self.get_error()
                if err > self.threshold:
                    info += (
                        f"failed{self.info_id}=" + str(err) + ">" + str(self.threshold)
                    )
                    self.threshold *= 1.1
                    info += f",adjust_threshold{self.info_id}=" + str(self.threshold) + ","
                else:
                    info += (
                        f"successful{self.info_id}="
                        + str(err)
                        + "<="
                        + str(self.threshold)
                        + ","
                    )
                    break
                retrain_time += time.time() - retrain_start_time
            refill_time = self.refill_watchset([(rs, self.watch_set[rs]) for rs in self.watch_set])
            return check_time + refill_time, True, info, retrain_time
        
        if cur_watchset_size is not None and cur_watchset_size >= self.size_budget:
            retrain_time = 0.
            refill_time = 0.
            offset = 0. # this is to correct the time needed for refillin the watchset
            while cur_watchset_size >= self.size_budget:
                training_set_collecting_time, training_info = self.get_training_set()
                retrain_time += training_set_collecting_time

                retrain_start_time = time.time()
                if black_box.config["algorithm"] == "postgres":
                    dbname = self.dbname_prefix + self.name
                    black_box.pg_retrain(self.cursor, dbname)
                elif not self.is_naru:
                    black_box.retrain(self.name, *training_info)
                else:
                    black_box.naru_retrain(self.naru_model_name, cols=[self.sel_col])
                for rs in self.watch_set:
                    if black_box.config["algorithm"] == "postgres":
                        dbname = self.dbname_prefix + self.name
                        self.watch_set[rs].pred = black_box.pg_predict_one(
                            self.cursor, dbname, self.sel_col, rs.lb, rs.ub
                        )
                    elif not self.is_naru:
                        self.watch_set[rs].pred = black_box.predict_one(
                            self.name,
                            [rs.lb, rs.ub],
                            [f"{self.name} {self.abbrev}"],
                            [""],
                        )
                    else:
                        self.watch_set[rs].pred = black_box.naru_predict_one(
                            self.naru_model_name,
                            cols=[self.sel_col, self.sel_col],
                            ops=[">=", "<="],
                            vals=[rs.lb, rs.ub],
                        )
                if len(info) == 0:
                    info = ","
                    
                info += "retrain_"

                _ts = time.time()
                refill_time += self.refill_watchset([(rs, self.watch_set[rs]) for rs in self.watch_set])
                offset -= (time.time() - _ts)

                cur_watchset_size = len(self.watch_set)

                retrain_time += time.time() - retrain_start_time
                if cur_watchset_size >= self.size_budget:
                    info += (
                        f"failed{self.info_id}=" + str(cur_watchset_size) + ">" + str(self.size_budget)
                    )
                    self.size_budget *= 2
                    info += f",adjust_size_budget{self.info_id}=" + str(self.size_budget) + ","
                else:
                    info += (
                        f"successful{self.info_id}="
                        + str(cur_watchset_size)
                        + "<="
                        + str(self.size_budget)
                        + ","
                    )
                    break
            return check_time + refill_time, True, info, retrain_time + offset

        return check_time, False, None, None
    

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

        watcher_start_time = time.time()
        if sel_val is not None and len(self.watch_set) > 0:
            # it is not lazy tuple updates, we can directly get the sel_val and update the watchset
            for rs in self.watch_set:
                if (
                    rs.lb <= sel_val
                    and sel_val <= rs.ub
                ):  # pass the predicate? card ++ 
                    self.watch_set[rs].true_card += 1

        if sel_val is not None and self.is_naru \
            and self.start_to_record_incremental_content:
                self.incremental_content.append((sel_val,))

        watcher_time = time.time() - watcher_start_time

        if self.triggers is not None and len(self.triggers) > 0:
            check_time_and_refill_time, if_retrain, retrain_info, retrain_time = self.check_retrain()
        else:
            if_retrain = False
        
        if if_retrain:
            watcher_time += check_time_and_refill_time

        if flush:
            watcher_time += self.flush_tuple_updates()

        info = f"watchset_size{self.info_id}={len(self.watch_set)},time{self.info_id}={round(time.time() - start_time, 6)},watcher_time{self.info_id}={round(watcher_time, 6):.6f}"
        if if_retrain:
            info += retrain_info + f"retrain_time{self.info_id}={round(retrain_time, 6):.6f}"

        if self.track_memory_usage:
            self._record_memory_peak()
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

        watcher_start_time = time.time()
        if sel_val is not None and len(self.watch_set) > 0:
            for rs in self.watch_set:
                if (
                    rs.lb <= sel_val
                    and sel_val <= rs.ub
                ):  # pass the predicate?
                    self.watch_set[rs].true_card -= 1
        watcher_time = time.time() - watcher_start_time

        if self.triggers is not None and len(self.triggers) > 0:
            check_time_and_refill_time, if_retrain, retrain_info, retrain_time = self.check_retrain()
        else:
            if_retrain = False
        
        if if_retrain:
            watcher_time += check_time_and_refill_time

        if flush:
            watcher_time += self.flush_tuple_updates()

        info = f"watchset_size{self.info_id}={len(self.watch_set)},time{self.info_id}={round(time.time() - start_time, 6)},watcher_time{self.info_id}={round(watcher_time, 6):.6f}"
        if if_retrain:
            info += retrain_info + f"retrain_time{self.info_id}={round(retrain_time, 6):.6f}"
        
        if self.track_memory_usage:
            self._record_memory_peak()
        return info

    def get_error(self):
        true_cards = []
        preds = []
        for query_info in self.watch_set.values():
            true_cards.append(query_info.true_card)
            preds.append(query_info.pred)
        if len(true_cards) == 0:
            return 0
        if self.error_metric == "avg":
            return get_average_q_error(true_cards, preds)
        elif self.error_metric == "95th":
            return get_percentile_q_error(true_cards, preds, 95)
        elif self.error_metric == "25th":
            return get_percentile_q_error(true_cards, preds, 25)
        elif self.error_metric == "50th":
            return get_percentile_q_error(true_cards, preds, 50)
        else:
            raise NotImplementedError

    def _check_the_cache(self, rs):
        max_overlap_ratio, which = None, None

        for watch_rs in self.watch_set:
            # length of intersection / length of union
            overlap_ratio = (max(0, min(rs.ub, watch_rs.ub) - max(rs.lb, watch_rs.lb))) / (max(rs.ub, watch_rs.ub) - min(rs.lb, watch_rs.lb))
            # 0 means non-overlapping at all; 1 means identical
            if which is None or max_overlap_ratio < overlap_ratio:
                which = watch_rs
                max_overlap_ratio = overlap_ratio
        
        if black_box.config["algorithm"] == "postgres":
            dbname = self.dbname_prefix + self.name
            answer = black_box.pg_predict_one(
                self.cursor, dbname, self.sel_col, rs.lb, rs.ub
            )
        elif not self.is_naru:
            answer = black_box.predict_one(
                self.name,
                [rs.lb, rs.ub],
                [f"{self.name} {self.abbrev}"],
                [""],
            )
        else:
            answer = black_box.naru_predict_one(
                self.naru_model_name,
                cols=[self.sel_col, self.sel_col],
                ops=[">=", "<="],
                vals=[rs.lb, rs.ub],
            )
        pred = copy.copy(answer)

        if which is not None and max_overlap_ratio >= self.overlap_ratio_lb:
            # let's do the correction: replace the overlap with the true card
            # answer += 1. * (max(0, min(rs.ub, which.ub) - max(rs.lb, which.lb))) / (which.ub - which.lb) * (self.watch_set[which].true_card - self.watch_set[which].pred)
            if black_box.config["algorithm"] == "postgres":
                dbname = self.dbname_prefix + self.name
                partial_pred = black_box.pg_predict_one(
                    self.cursor, dbname, self.sel_col, max(rs.lb, which.lb), min(rs.ub, which.ub)
                )
            elif not self.is_naru:
                partial_pred = black_box.predict_one(self.name, [max(rs.lb, which.lb), min(rs.ub, which.ub)], [f"{self.name} {self.abbrev}"], [""])
            else:
                partial_pred = black_box.naru_predict_one(
                    self.naru_model_name,
                    cols=[self.sel_col, self.sel_col],
                    ops=[">=", "<="],
                    vals=[max(rs.lb, which.lb), min(rs.ub, which.ub)],
                )

            answer = max(0, answer - partial_pred) \
                + 1. * (max(0, min(rs.ub, which.ub) - max(rs.lb, which.lb))) / (which.ub - which.lb) * self.watch_set[which].true_card
            answer = round(answer)
            answer = max(0, min(answer, self.cur_table_size))

        return max_overlap_ratio, answer, pred, which

    def _load_pg_join_subquery_info(self):
        tableset_to_joinid = {}
        tableset_to_sel = {}
        tableset_to_rawrows = {}
        tableset_to_estrows = {}
        tableset_to_outerrel = {}
        min_join_qid = None
        max_join_qid = None

        with open("/winhomes/ANONYMOUS/watcher_data/join_est_record_job.txt", "r") as test_fin:
            lines = list(test_fin.readlines())
            query_id = None
            relations = []
            outerrel = []
            selectivity = None
            est_rows = None
            raw_rows = None
            for line_id in range(len(lines)):
                line = lines[line_id].strip()
                if line.startswith("query:"):
                    query_id = int(line.split(" ")[-1])
                    if min_join_qid is None or min_join_qid > query_id:
                        min_join_qid = query_id
                    if max_join_qid is None or max_join_qid < query_id:
                        max_join_qid = query_id
                    relations = []
                    outerrel = []
                    selectivity = None
                    est_rows = None
                    raw_rows = None
                elif line.startswith("RELOPTINFO"):
                    if len(relations) > 0:
                        # the outer part
                        outerrel.extend(line.split("(")[1].split(")")[0].split(" "))
                    relations.extend(line.split("(")[1].split(")")[0].split(" "))
                elif line.startswith("Selectivity"):
                    selectivity = float(line.split(" ")[-1])
                elif line.startswith("Estimated Rows"):
                    est_rows = int(float(line.split(": ")[-1]))
                elif line.startswith("Raw Rows"):
                    raw_rows = int(float(line.split(": ")[-1]))
                elif len(line) == 0 and query_id is not None and (self.abbrev in relations or self.name in relations) and selectivity is not None:
                    relations.sort()
                    tableset = tuple(relations)
                    outerrel.sort()


                    tableset_to_joinid[tableset] = query_id
                    tableset_to_sel[tableset] = selectivity
                    tableset_to_rawrows[tableset] = raw_rows
                    tableset_to_estrows[tableset] = est_rows
                    tableset_to_outerrel[tableset] = tuple(outerrel)

                    query_id = None
                    relations = []
                    outerrel = []
                    selectivity = None
                    est_rows = None
                    raw_rows = None
        return tableset_to_joinid, tableset_to_sel, tableset_to_rawrows, tableset_to_estrows, min_join_qid, max_join_qid, tableset_to_outerrel

    def _debug_check_hint(self, hint_to_inject):
        assert len([line for line in hint_to_inject.split('\n') if line.strip() != '']) == self.n_tabs_in_from + (self.n_tabs_in_from - 1) + 1 + 1 
        # N scan methods, (N - 1) join methods, 1 for header, 1 for leading, i.e., join order and join direction

    def query(self, rs, card):
        assert not self.enable_lazy_tuple_updates or self.nothing_to_flush()
        start_time = time.time()
        assert rs.table_name == self.name

        overlap_ratio, answer, model_pred, which = self._check_the_cache(rs)

        if rs in self.watch_set:
            hit = True
        else:
            hit = False

        if overlap_ratio is not None and overlap_ratio >= self.overlap_ratio_lb:
            correction = True
        else:
            correction = False

        watcher_time = time.time() - start_time
        q = self.get_sql_with_range(rs)

        # inject the "answer" and get the plan info
        _, join_order, scan_mtd = inject_single_table_sels_and_get_cost(
            pointer=self.pointer,
            sel=answer / self.cur_table_size,
            n_tabs_in_from=self.n_tabs_in_from,
            q=q,
            hint=None,
            plan_info=True,
        ) # this plan_cost if useful only when answer == true_card, otherwise we need to pay extra 1x planning_time to cost the plan

        # construct the plan by the info
        hint = gen_final_hint(scan_mtd=scan_mtd, str=join_order)
        # self._debug_check_hint(hint)
        
        if self.enable_correct_the_joins:
            tableset_to_joinid, tableset_to_sel, tableset_to_rawrows, tableset_to_estrows, min_join_qid, max_join_qid, tableset_to_outerrel = self._load_pg_join_subquery_info()

        flag_for_injecting_join_sels = False
        if self.enable_correct_the_joins \
            and overlap_ratio is not None \
                and overlap_ratio >= self.overlap_ratio_lb \
                    and which is not None \
                        and self.watch_set[which].tableset_to_correction is not None:
            n_single = min_join_qid
            n_all = max_join_qid + 1

            pointers = [self.pointer]
            single_sels = [answer / self.cur_table_size]
            join_sels = []
            tableset_to_correctedrows = {}
            for tableset, factor in self.watch_set[which].tableset_to_correction.items():
                if tableset in tableset_to_joinid and len(tableset) == self.correct_exactly_ntabsjoin:
                    pointers.append(tableset_to_joinid[tableset])
                    new_join_sel = max(min(tableset_to_sel[tableset] * factor, 1.0), 0.0)
                    join_sels.append(new_join_sel)
                    tableset_to_correctedrows[tableset] = round(tableset_to_rawrows[tableset] * new_join_sel)

            if len(join_sels) > 0:
                _, corrected_join_order, corrected_scan_mtd = inject_single_and_join_sels_and_get_cost(
                    pointers=pointers,
                    single_sels=single_sels,
                    n_single=n_single,
                    join_sels=join_sels,
                    n_all=n_all,
                    q=q,
                    hint=None,
                    plan_info=True,
                ) 
                flag_for_injecting_join_sels = True
                # get the "corrected" plan
                corrected_hint = gen_final_hint(scan_mtd=corrected_scan_mtd, str=corrected_join_order)
                self._debug_check_hint(corrected_hint)

        # lets run it!    
        if self.enable_correct_the_joins:
            pg_plan_cost, execution_time, planning_time, tableset_to_truecard, model_name_to_have = get_real_latency(
                sql=q,
                hint=corrected_hint if flag_for_injecting_join_sels else hint, # if we have corrected plan, we use the correct one; otherwise, use the one by single-card injection
                extract_plan_info=True,
                focus_on=[self.abbrev, self.name],
                enable_join_sel_injection=flag_for_injecting_join_sels,
                debug_print_the_monitored_part=self.debug_print_the_monitored_part,
                if_have=[self.name, self.abbrev],
            ) # the first item is "plan cost" based on Postgres's own stats, but it is not the plan cost based on the injected cardinality
            tableset_to_correction = {}
            for tableset in tableset_to_truecard:
                if tableset in tableset_to_estrows and len(tableset) == self.correct_exactly_ntabsjoin:
                    tableset_to_correction[tableset] = tableset_to_truecard[tableset] / max(1, tableset_to_estrows[tableset])
        else:
            pg_plan_cost, execution_time, planning_time, tableset_to_truecard, model_name_to_have = get_real_latency(
                sql=q,
                hint=hint,
                extract_plan_info=True,
                focus_on=[self.abbrev, self.name],
                debug_print_the_monitored_part=self.debug_print_the_monitored_part,
                if_have=[self.name, self.abbrev],
            ) # the first item is "plan cost" based on Postgres's own stats, but it is not the plan cost based on the injected cardinality
            tableset_to_correction = None

        if self.enable_correct_the_joins and correction and which is not None and tableset_to_correction is not None:
            self.watch_set[which].merge_new_join_correction(tableset_to_correction)

        start_time_2 = time.time()
        # let's see if we have a new member for the watchset
        query_info = QueryInfo(
            true_card=card,
            pred=model_pred,
            plan_cost=pg_plan_cost,
            execution_time=execution_time,
            execution_time_based_on_model_pred=None,
            planning_time=planning_time,
            pc_pred=None,
            pc_true=None,
            tableset_to_correction=tableset_to_correction,
        )
        if hit:
            del self.watch_set[rs]

        checks_info = [
            "fail_long_exectime_but_short_optime_check",
            "fail_plan_cost_check",
            "fail_extrapolated_exectime_check",
            "pass",
        ]
        checks_id = 0

        if self.pass_long_exectime_but_short_optime_check(query_info):
            checks_id += 1
            if hit:
                # because answer = true_card, hint == the plan by injecting single-table true_card
                #  tableset_to_joinid, tableset_to_sel, tableset_to_rawrows, tableset_to_estrows, min_join_qid, max_join_qid, tableset_to_outerrel are what we need when we cost the plans

                # first, we get the plan for injecting model_pred
                # 1. we get the plan by injecting query_info.pred
                inj_start_ts = time.time()
                _, model_pred_inj_join_order, model_pred_inj_scan_method = inject_single_table_sels_and_get_cost(
                    pointer=self.pointer,
                    sel=query_info.pred / self.cur_table_size,
                    n_tabs_in_from=self.n_tabs_in_from,
                    q=q,
                    hint=None,
                    plan_info=True,
                )
                model_pred_inj_plan = gen_final_hint(model_pred_inj_join_order, model_pred_inj_scan_method)
                # self._debug_check_hint(model_pred_inj_plan)
                if not self.enable_correct_the_joins:
                    (tableset_to_joinid, 
                    _, 
                    tableset_to_rawrows, 
                    tableset_to_estrows, 
                    min_join_qid, 
                    max_join_qid, 
                    tableset_to_outerrel) = self._load_pg_join_subquery_info()

                watcher_time = watcher_time - (time.time() - inj_start_ts) + (planning_time / 1000.) # here we replace the time cost for "injection" with 1x planning_time

                # now we cost both plans by true cards
                inj_start_ts = time.time()
                query_info.pc_true = inject_true_cards_and_get_cost(
                    pointer=self.pointer,
                    sel=query_info.true_card / self.cur_table_size,
                    join_pointer=tableset_to_joinid,
                    join_true_cards=tableset_to_truecard,
                    join_est_rows=tableset_to_estrows,
                    join_raw_rows=tableset_to_rawrows,
                    join_outerrel=tableset_to_outerrel,
                    n_single = min_join_qid,
                    n_all = max_join_qid + 1,
                    q = q,
                    hint=hint,
                    plan_info=False,
                )
                watcher_time = watcher_time - (time.time() - inj_start_ts) + (planning_time / 1000.) # here we replace the time cost for "injection" with 1x planning_time

                # 3. and we cost it by query_info.true_card
                inj_start_ts = time.time()
                query_info.pc_pred = inject_true_cards_and_get_cost(
                    pointer=self.pointer,
                    sel=query_info.true_card / self.cur_table_size,
                    join_pointer=tableset_to_joinid,
                    join_true_cards=tableset_to_truecard,
                    join_est_rows=tableset_to_estrows,
                    join_raw_rows=tableset_to_rawrows,
                    join_outerrel=tableset_to_outerrel,
                    n_single = min_join_qid,
                    n_all = max_join_qid + 1,
                    q = q,
                    hint=model_pred_inj_plan,
                    plan_info=False,
                )
                # if hit, it means we need to estimate the execution_time_based_on_model_pred by interpolation
                query_info.execution_time_based_on_model_pred = query_info.execution_time / query_info.plan_cost * query_info.pc_pred
                watcher_time = watcher_time - (time.time() - inj_start_ts) + (planning_time / 1000.) # here we replace the time cost for "injection" with 1x planning_time
                #################################################

            else:
                # get the plan by model_pred
                inj_start_ts = time.time()
                _, model_pred_inj_join_order, model_pred_inj_scan_method = inject_single_table_sels_and_get_cost(
                    pointer=self.pointer,
                    sel=query_info.pred / self.cur_table_size,
                    n_tabs_in_from=self.n_tabs_in_from,
                    q=q,
                    hint=None,
                    plan_info=True,
                )
                model_pred_inj_plan = gen_final_hint(model_pred_inj_join_order, model_pred_inj_scan_method)
                # self._debug_check_hint(model_pred_inj_plan)
                watcher_time = watcher_time - (time.time() - inj_start_ts) + (planning_time / 1000.) # here we replace the time cost for "injection" with 1x planning_time
                #############################################

                # get the plan by true_card
                inj_start_ts = time.time()
                _, true_card_inj_join_order, true_card_inj_scan_method = inject_single_table_sels_and_get_cost(
                    pointer=self.pointer,
                    sel=query_info.true_card / self.cur_table_size,
                    n_tabs_in_from=self.n_tabs_in_from,
                    q=q,
                    hint=None,
                    plan_info=True,
                )
                true_card_tableset_to_joinid, _, true_card_tableset_to_rawrows, true_card_tableset_to_estrows, true_card_min_join_qid, true_card_max_join_qid, true_card_tableset_to_outerrel = self._load_pg_join_subquery_info()
                true_card_inj_plan = gen_final_hint(true_card_inj_join_order, true_card_inj_scan_method)
                # self._debug_check_hint(true_card_inj_plan)
                watcher_time = watcher_time - (time.time() - inj_start_ts) + (planning_time / 1000.) # here we replace the time cost for "injection" with 1x planning_time
                #############################################

                # we cost both plans by true_card
                inj_start_ts = time.time()
                query_info.pc_pred = inject_true_cards_and_get_cost(
                    pointer=self.pointer,
                    sel=query_info.true_card / self.cur_table_size,
                    join_pointer=true_card_tableset_to_joinid,
                    join_true_cards=tableset_to_truecard,
                    join_est_rows=true_card_tableset_to_estrows,
                    join_raw_rows=true_card_tableset_to_rawrows,
                    join_outerrel=true_card_tableset_to_outerrel,
                    n_single=true_card_min_join_qid,
                    n_all=true_card_max_join_qid + 1,
                    q = q,
                    hint=model_pred_inj_plan,
                    plan_info=False,
                )
                watcher_time = watcher_time - (time.time() - inj_start_ts) + (planning_time / 1000.) # here we replace the time cost for "injection" with 1x planning_time

                inj_start_ts = time.time()
                query_info.pc_true = inject_true_cards_and_get_cost(
                    pointer=self.pointer,
                    sel=query_info.true_card / self.cur_table_size,
                    join_pointer=true_card_tableset_to_joinid,
                    join_true_cards=tableset_to_truecard,
                    join_est_rows=true_card_tableset_to_estrows,
                    join_raw_rows=true_card_tableset_to_rawrows,
                    join_outerrel=true_card_tableset_to_outerrel,
                    n_single=true_card_min_join_qid,
                    n_all=true_card_max_join_qid + 1,
                    q = q,
                    hint=true_card_inj_plan,
                    plan_info=False,
                )
                # we extroplate the excution_time_based_on_model_pred, based on the current plan cost and current plan execution time
                query_info.execution_time_based_on_model_pred = query_info.execution_time / query_info.plan_cost * query_info.pc_pred
                watcher_time = watcher_time - (time.time() - inj_start_ts) + (planning_time / 1000.) # here we replace the time cost for "injection" with 1x planning_time
                #############################################

            if self.pass_cost_check(query_info):
                checks_id += 1
                if self.pass_execution_time_check(query_info):
                    checks_id += 1  
                    self.watch_set[rs] = query_info

        # update query_pool
        self.insert_to_query_pool(rs)
        watcher_time += time.time() - start_time_2
        info = f"watchset_size{self.info_id}={len(self.watch_set)}" 
        info += f",plan_cost{self.info_id}={query_info.plan_cost}"
        info += f",planning_time{self.info_id}={query_info.planning_time}"
        info += f",execution_time{self.info_id}={round(execution_time / 1000., 6):.6f}"
        if query_info.execution_time_based_on_model_pred is None:
            info += f",expected_execution_time_based_on_pred{self.info_id}=None"
        else:
            info += f",expected_execution_time_based_on_pred{self.info_id}={round(query_info.execution_time_based_on_model_pred / 1000., 6):.6f}"
        info += f",watcher_time{self.info_id}={round(watcher_time, 6):0.6f}"
        info += f",got_true_card{self.info_id}="
        if (self.name in model_name_to_have and model_name_to_have[self.name]) or (self.abbrev in model_name_to_have and model_name_to_have[self.abbrev]):
            info += "True"
        else:
            info += "False"
        if query_info.pc_true is None:
            info += f",pc_true{self.info_id}=None"
        else:
            info += f",pc_true{self.info_id}={query_info.pc_true}"
        if query_info.pc_pred is None:
            info += f",pc_pred{self.info_id}=None"
        else:
            info += f",pc_pred{self.info_id}={query_info.pc_pred}"
        info += f",sensitivity_check={self.info_id}={checks_info[checks_id]}"
        if overlap_ratio is None: 
            info += f",max_overlap_ratio{self.info_id}={None},correction{self.info_id}?={False}"
        else:
            info += f",max_overlap_ratio{self.info_id}={round(overlap_ratio, 2):.2f},correction{self.info_id}?={correction}"
            if correction:
                info += f",pred{self.info_id}={model_pred}"
                if which is not None:
                    info += f",corrected_by{self.info_id}={which.lb}-{which.ub}"

        if flag_for_injecting_join_sels:
            info += f",correcting_join_sels{self.info_id}={True}"
            est_corrected_actual = []
            for tableset in tableset_to_correctedrows:
                if self.correct_exactly_ntabsjoin is None or len(tableset) == self.correct_exactly_ntabsjoin:
                    # tableset is a tuple of string, e.g., ('ss', 'cs', 'i1')
                    # let's translate it into 'ss-cs-i1'
                    tableset_to_print = '-'.join(list(tableset))
                    # so it will look like: ",est/corrected/actual_rows{info_id}=ss-cs-i1>est/corrected/actual|ss-cs-i1-i2>est/corrected/actual|..."
                    _est = None if tableset not in tableset_to_estrows else tableset_to_estrows[tableset]
                    _corrected = tableset_to_correctedrows[tableset]
                    _truecard = None if tableset not in tableset_to_truecard else tableset_to_truecard[tableset]
                    est_corrected_actual.append(tableset_to_print + ">" + str(_est) + "/" + str(_corrected) + "/" + str(_truecard))
            if len(est_corrected_actual) > 0:
                info += f",est/corrected/actual_rows{self.info_id}={'|'.join(est_corrected_actual)}"
            if self.debug_show_all_correction_factors and which in self.watch_set:
                debug_to_print = []
                for tableset in self.watch_set[which].tableset_to_correction:
                    tableset_to_print = '-'.join(list(tableset))
                    factors_to_print = f'current={self.watch_set[which].tableset_to_correction[tableset]}' + '/others='
                    if tableset in self.watch_set[which].debug_all_previous_tableset_to_correction:
                        factors_to_print += '-'.join([str(_x) for _x in self.watch_set[which].debug_all_previous_tableset_to_correction[tableset]])
                    debug_to_print.append(tableset_to_print + '>' + factors_to_print)
                if len(debug_to_print):
                    info += f",all_tableset_to_corrections{self.info_id}=" + "|".join(debug_to_print)

        if flag_for_injecting_join_sels:
            hint_wo_newline = corrected_hint.replace('\n', '')
        else:
            hint_wo_newline = hint.replace('\n', '')
        info += f",plan{self.info_id}={hint_wo_newline}"

        if self.track_memory_usage:
            self._record_memory_peak()

        return (
            np.round(answer, 6),
            get_average_q_error([card], [answer]),
            info,
        )
    
    def insert_to_query_pool(self, rs):
        if len(self.query_pool) < self.query_pool_size:
            self.query_pool.append(rs)
        else:
            i = random.randint(0, self.query_pool_query_id)
            if i < self.query_pool_size:
                self.query_pool[i] = rs
        self.query_pool_query_id += 1
        if self.track_memory_usage:
            self._record_memory_peak()

    def pass_long_exectime_but_short_optime_check(self, query_info):
        if self.planning_time_ub is None:
            return False
        if self.execution_time_lb is None:
            return False
        assert query_info.execution_time is not None
        assert query_info.planning_time is not None
        
        if query_info.execution_time < self.execution_time_lb / self.plancost_check_ratio:
            # because we have another check on query_info.execution_time_based_on_model_pred
            # so we approximately want query_info.execution_time >= self.execution_time_lb / self.plancost_check_ratio
            # meaning that we don't want to let those queries which are "relatively fast" to pass this check
            return False
        
        if not self.planning_time_ub_is_percentage:
            if query_info.planning_time > self.planning_time_ub:
                return False
        else:
            if query_info.planning_time > query_info.execution_time * self.planning_time_ub:
                return False
        return True
    
    def pass_execution_time_check(self, query_info):
        if self.execution_time_lb is None:
            return False
        assert query_info.execution_time_based_on_model_pred is not None
        return query_info.execution_time_based_on_model_pred >= self.execution_time_lb
    
    def pass_cost_check(self, query_info):
        if self.plancost_check_ratio is None:
            return False
        assert query_info.pc_true is not None
        assert query_info.pc_pred is not None

        return query_info.pc_pred >= query_info.pc_true * self.plancost_check_ratio

    def get_sql_with_range(self, rs):
        return self.sql.replace("{lb" + str(self.info_id) + "}", str(rs.lb)).replace("{ub" + str(self.info_id) + "}", str(rs.ub))

    def refill_watchset(self, list_of_rs_and_query_info):
        assert not self.enable_lazy_tuple_updates or self.nothing_to_flush()

        # we run this function only at the beginning (after we get the first model) or right after we retrain the model
        # for this implementation: for every query that passes the time check, we collect the new prediction and re-computes their pc(true) and pc(pred)
        refill_start_time = time.time()
        offset = 0. # the offset caused by replacing TimeCost("inject_...") with 1xplanning_time

        self.watch_set = {}
        qualified = []
        
        for _item in list_of_rs_and_query_info:
            rs, query_info = _item[0], _item[1]
            q = self.get_sql_with_range(rs)

            if self.pass_long_exectime_but_short_optime_check(query_info):
                # get prediction
                if black_box.config["algorithm"] == "postgres":
                    dbname = self.dbname_prefix + self.name
                    query_info.pred = black_box.pg_predict_one(
                        self.cursor, dbname, self.sel_col, rs.lb, rs.ub
                    )
                elif not self.is_naru:
                    query_info.pred = black_box.predict_one(
                        self.name,
                        [rs.lb, rs.ub],
                        [f"{self.name} {self.abbrev}"],
                        [""],
                    )
                else:
                    query_info.pred = black_box.naru_predict_one(
                        self.naru_model_name,
                        cols=[self.sel_col, self.sel_col],
                        ops=[">=", "<="],
                        vals=[rs.lb, rs.ub],
                    )
                
                inj_start_ts = time.time()
                query_info.pc_true = inject_single_table_sels_and_get_cost(
                    pointer=self.pointer,
                    sel=query_info.true_card / self.cur_table_size,
                    n_tabs_in_from=self.n_tabs_in_from,
                    q=q,
                    hint=None,
                    plan_info=False,
                )
                offset += (query_info.planning_time / 1000.) - (time.time() - inj_start_ts) # replace TimeCost("inject_...") with 1x planning_time

                # 1. get the join order and scan method for the plan generated by injecting query_info.pred
                inj_start_ts = time.time()
                _, inj_join_order, inj_scan_method = inject_single_table_sels_and_get_cost(
                    pointer=self.pointer,
                    sel=query_info.pred / self.cur_table_size,
                    n_tabs_in_from=self.n_tabs_in_from,
                    q=q,
                    hint=None,
                    plan_info=True,
                )
                #2. generate the hint
                inj_hint = gen_final_hint(inj_join_order, inj_scan_method)
                # self._debug_check_hint(inj_hint)
                offset += (query_info.planning_time / 1000.) - (time.time() - inj_start_ts) # replace TimeCost("inject_...") with 1x planning_time
                #3. cost it by query_info.true_card
                inj_start_ts = time.time()
                query_info.pc_pred = inject_single_table_sels_and_get_cost(
                    pointer=self.pointer,
                    sel=query_info.true_card / self.cur_table_size,
                    n_tabs_in_from=self.n_tabs_in_from,
                    q=q,
                    hint=inj_hint,
                    plan_info=False,
                )
                offset += (query_info.planning_time / 1000.) - (time.time() - inj_start_ts) # replace TimeCost("inject_...") with 1x planning_time

                query_info.execution_time_based_on_model_pred = query_info.execution_time / query_info.plan_cost * query_info.pc_pred
                if self.pass_execution_time_check(query_info) and self.pass_cost_check(query_info):
                    qualified.append((rs, query_info))
            
        for i in range(len(qualified)):
            self.watch_set[qualified[i][0]] = qualified[i][1]

        refill_time = time.time() - refill_start_time + offset
        return refill_time 
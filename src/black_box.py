import learnedcardinalities.train
import jgmp.dsb_test
import naru.train_model, naru.eval_model
import torch
import random
import numpy as np
import time

# disable randomness
torch.manual_seed(2023)
random.seed(2023)
np.random.seed(2023)
torch.use_deterministic_algorithms(True)

# hard-coded parameters
config = {
    "training_size": 1500, 
    "algorithm": "mscn" # by default, it is mscn, but we can use jgmp as well
}
# for mscn
epochs = 200
batch = 1024
hid = 256
cuda = False

# model details
name2details = {}

# default info
default_column_min_max_vals = {
    "join": {
        "ss.ss_item_sk": [1.0, 18000.0],
        "ss.ss_store_sk": [1.0, 10.0],
        "sr.sr_item_sk": [1.0, 18000.0],
        "sr.sr_store_sk": [1.0, 10.0],
    }
}
default_predicate_templates = {}


def retrain(model_name, tables, joins, training_set, query_template=None):
    global config
    global name2details
    if config["algorithm"] == "mscn": 
        if model_name not in name2details:
            name2details[model_name] = (None, None, None, None)
        name2details[model_name] = learnedcardinalities.train.run(
            training_set,
            tables,
            joins,
            default_column_min_max_vals[model_name],
            default_predicate_templates[model_name],
            config["training_size"],
            epochs,
            batch,
            hid,
            cuda,
        )
    elif config["algorithm"] == "jgmp":
        if model_name not in name2details:
            name2details[model_name] = (None, None, None)
        else:
            assert query_template is None
            query_template = name2details[model_name][-1]
        list_of_name_and_sql_and_truecard = []
        for i in range(len(training_set)):
            bounds = list(training_set[i][:-1])
            truecard = training_set[i][-1]
            sql = query_template
            for ii in range(0, len(bounds), 2):
                if isinstance(bounds[ii], float):
                    bounds[ii] -= 0.01
                    bounds[ii + 1] += 0.01
                elif isinstance(bounds[ii], int):
                    bounds[ii] -= 1
                    bounds[ii + 1] += 1
                else:
                    raise NotImplementedError
                sql = sql.replace(
                        "{" + "lb" + str(ii + 1) + "}", str(bounds[ii])
                    ).replace(
                        "{" + "ub" + str(ii + 1) + "}", str(bounds[ii + 1])
                    )
            list_of_name_and_sql_and_truecard.append((f"q{i}", sql, truecard))
        schema, estimator = jgmp.dsb_test.watcher_dsb_train(
            list_of_name_and_sql_and_truecard,
            5555
        )
        name2details[model_name] = (schema, estimator, query_template)
    else:
        raise NotImplementedError

def naru_retrain(model_name, cols):
    global config
    global name2details

    assert config["algorithm"] == "naru"

    is_incremental = False
    if model_name not in name2details:
        name2details[model_name] = (
            None, # table
            None # model
        ) 
        epochs = config["training_epochs"] # first time will be a full training
        is_incremental = False
    else:
        if "incremental_epochs" in config:
            epochs = config["incremental_epochs"] # if in incremental mode, ...
            is_incremental = True
        else:
            epochs = config["training_epochs"] # otherwise, it is still a full (re-)training
            is_incremental = False

    filename = model_name + ".csv"

    if not is_incremental:
        name2details[model_name] = naru.train_model.train_called_by_watcher(filename, cols, epochs=epochs)
    else:
        _, model = name2details[model_name]
        name2details[model_name] = naru.train_model.incremental_update_called_by_watcher(filename, cols, model, epochs=epochs)

def pg_retrain(cursor, tab):
    _start_ts = time.time()
    cursor.execute(f"vacuum (analyze) {tab};")
    return 1, time.time() - _start_ts # number of vacuum analyze commands, time taken

def predict_one(model_name, bounds, table_template, join_template):
    global config
    global name2details
    if config["algorithm"] == "mscn":
        assert model_name in name2details
        dicts, min_val, max_val, model = name2details[model_name]
        return learnedcardinalities.train.predict_one(
            bounds,
            table_template,
            join_template,
            dicts,
            min_val,
            max_val,
            default_column_min_max_vals[model_name],
            default_predicate_templates[model_name],
            batch,
            model,
            cuda,
        )
    elif config["algorithm"] == "jgmp":
        assert model_name in name2details
        schema, estimator, query_template = name2details[model_name]
        sql = query_template
        for ii in range(0, len(bounds), 2):
            if isinstance(bounds[ii], float):
                bounds[ii] -= 0.01
                bounds[ii + 1] += 0.01
            elif isinstance(bounds[ii], int):
                bounds[ii] -= 1
                bounds[ii + 1] += 1
            else:
                raise NotImplementedError
            sql = sql.replace(
                    "{" + "lb" + str(ii + 1) + "}", str(bounds[ii])
                ).replace(
                    "{" + "ub" + str(ii + 1) + "}", str(bounds[ii + 1])
                )
        return jgmp.dsb_test.watcher_dsb_test(schema, estimator, sql)
    else:
        raise NotImplementedError

def naru_predict_one(model_name, cols, ops, vals):
    global config
    global name2details

    assert config["algorithm"] == "naru"
    assert model_name in name2details

    table, model = name2details[model_name]

    return naru.eval_model.predict_one_called_by_watcher(table, model, cols, ops, vals)

def pg_predict_one(cursor, tab, sel_col, lb, ub):
    sql = f"SELECT * FROM {tab} WHERE {sel_col} BETWEEN {lb} AND {ub};"
    cursor.execute("EXPLAIN (SUMMARY, COSTS, FORMAT JSON) " + sql)
    query_plan = cursor.fetchall()
    est = query_plan[0][0][0]["Plan"]["Plan Rows"]
    return est
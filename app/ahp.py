import datetime
from collections import Counter

import numpy as np
import db as database
import pprint
import pandas as pd

pp = pprint.PrettyPrinter()


def containers(column, **kwargs):
    kwargs["column"] = column
    kwargs["where"] = "status = 'running'"
    kwargs["sort"] = "name"
    data = database.select("containers", **kwargs)
    return data


def weight_of_criteria(*args, **kwargs):
    # read from cfg file
    kwargs["config"] = True
    parameter = database.select("parameter", **kwargs)
    parameter = sorted(parameter.items(), key=lambda x: x[1])
    p_name = [x[1] for x in parameter]
    index = p_name
    columns = p_name
    type_data = ['float32'] * len(p_name)
    dtype = list(zip(p_name, type_data))
    values = np.zeros(len(p_name), dtype=dtype)
    data_matrix = pd.DataFrame(values, index=index, columns=columns)

    kwargs.clear()
    kwargs["config"] = True
    comparison = database.select("comparison", **kwargs)
    c_key = [x for x in list(comparison.keys())]
    for idx, row in enumerate(data_matrix.index.values):
        for idy, column in enumerate(data_matrix.columns.values):
            for i in range(len(c_key)):
                if c_key[i].split("/")[0] == row.lower() and c_key[i].split("/")[1] == column.lower():
                    data_matrix.loc[row, column] = comparison[c_key[i]]
                    data_matrix.loc[column, row] = 1 / int(comparison[c_key[i]])
                    break
            if column == row:
                data_matrix.loc[row, column] = 1
    data_matrix["3rd root of product"] = data_matrix.product(axis=1) ** (1 / len(parameter))
    data_matrix["priority vector"] = data_matrix["3rd root of product"] / data_matrix["3rd root of product"].sum()
    return data_matrix


def rating_each_node(column_name, *args, **kwargs):
    name = column_name
    # print("{} rating".format(name))
    # 1. mendapatkan semua data CPU, memory, LTA, cari terendah dan tertinggi, bagi 9 kolom
    kwargs["column"] = "container_id, timestamps, name"
    kwargs["where"] = "status = 'running'"
    kwargs["sort"] = "name"
    container = database.select("containers", **kwargs)
    if not container:
        return False, {"message": "no container active"}
    c_id = '{}'.format([x[0] for x in container])
    c_id = "".join(c_id)
    c_id = c_id[1:-1]
    ts = container[0][1]

    # kwargs.clear()
    kwargs["column"] = "container_id, {column}, container_name".format(column=name)
    kwargs["sort"] = "container_name"
    # data = database.select("stats", **kwargs)
    if "hour" in kwargs.keys():
        kwargs["where"] = "container_id IN ({c_id}) AND timestamps BETWEEN '{hour_from}' and '{hour_to}'".format(
            c_id=c_id, hour_from=kwargs["hour_from"], hour_to=kwargs["hour_to"])
    elif "day" in kwargs.keys():
        kwargs["where"] = "container_id IN ({c_id}) AND timestamps BETWEEN '{day_from}' and '{day_to}'".format(
            c_id=c_id, day_from=kwargs["day_from"], day_to=kwargs["day_to"])
    elif "week" in kwargs.keys():
        kwargs["where"] = "container_id IN ({c_id}) AND timestamps BETWEEN '{week_from}' and '{week_to}'".format(
            c_id=c_id, week_from=kwargs["week_from"], week_to=kwargs["week_to"])
    else:
        kwargs["where"] = "container_id IN ({c_id}) AND timestamps = '{ts}'".format(c_id=c_id, ts=ts)
    data = database.select("stats", **kwargs)

    c = Counter(v[2] for v in data)

    data_average = list()
    for val in c:
        average = sum(v[1] for v in data if v[2] == val) / float(c[val])
        id = [v for i, v in enumerate(data) if v[2] == val]
        id = id[0][0]
        data_average.append((id, average, val))
    if data_average:
        data = data_average
    if not all(data):
        return False, {"message": "no stats"}
    data_min = min(data, key=lambda key: key[1])
    data_max = max(data, key=lambda key: key[1])
    if not data_min and not data_max:
        data_range = list(np.arange(data_min[1], data_max[1], (data_max[1] - data_min[1]) / 9))
    else:
        data_range = [0]
    # 2. untuk setiap data, cek data ada pada kolom mana, masukkan ke matrik
    c_name = [x[2] for x in container]
    index = c_name
    columns = c_name
    type_data = ['float32'] * len(c_name)
    dtype = list(zip(c_name, type_data))
    values = np.zeros(len(c_name), dtype=dtype)

    data_matrix = pd.DataFrame(values, index=index, columns=columns)
    for idx, row in enumerate(data_matrix.index.values):
        for idy, column in enumerate(data_matrix.columns.values):
            tx = [item for item in data if item[2] == row][0][1]
            # ty = tx
            ty = [item for item in data if item[2] == column][0][1]

            for idx, val in enumerate(data_range[1:len(data_range)]):
                if (tx >= data_range[idx - 1] and tx < data_range[idx]):
                    tx = idx
                    break
                elif tx >= data_range[len(data_range) - 1]:
                    tx = len(data_range)
                    break

            for idx, val in enumerate(data_range[1:len(data_range)]):
                if (ty >= data_range[idx - 1] and ty < data_range[idx]):
                    ty = idx
                    break
                elif ty >= data_range[len(data_range) - 1]:
                    ty = len(data_range)
                    break

            # 3. Bandingkan row dan column
            if ty == 0:
                tz = 1
            else:
                tz = tx / ty
            data_matrix.loc[row, column] = tz

    # 4. untuk setiap row, hitung nilai geomean dan eigenvector
    data_matrix["3rd root of product"] = data_matrix.product(axis=1) ** (1 / database.total_data("containers"))
    data_matrix["priority vector"] = data_matrix["3rd root of product"] / data_matrix["3rd root of product"].sum()
    return True, data_matrix


def score(**kwargs):
    
    CPU = rating_each_node("CPU", **kwargs)
    Memory = rating_each_node("Memory", **kwargs)
    LTA = rating_each_node("last_time_access_percentage", **kwargs)
    
    if CPU[0] != False and Memory[0] != False and LTA[0] != False:
        cpu_dot_wc = np.dot(weight_of_criteria()["priority vector"].iloc[weight_of_criteria().index.get_loc("CPU")],
                            CPU[1]["priority vector"])
        mem_dot_wc = np.dot(weight_of_criteria()["priority vector"].iloc[weight_of_criteria().index.get_loc("Memory")],
                            Memory[1]["priority vector"])
        lta_dot_wc = np.dot(weight_of_criteria()["priority vector"].iloc[weight_of_criteria().index.get_loc("LTA")],
                            LTA[1]["priority vector"])

        c_score = cpu_dot_wc + mem_dot_wc + lta_dot_wc
        c_score = [x.item() for x in list(c_score)]
        c_name = list(map(list, containers("container_id")))
        c_ts = list(map(list, containers("timestamps")))[0][0].strftime("%Y-%m-%d %H:%M:%S")
        c_name = [x[0] for x in c_name]
        score_final = dict(zip(c_name, c_score))
        score_max = max(score_final, key=score_final.get)
        score_min = min(score_final, key=score_final.get)

        score_final = {"status": "success", "result": score_final, "max": str(score_max), "min": str(score_min), "ts": c_ts}
        return score_final
    else:
        error = CPU[1]
        return {"status": "error", "message": error}

# print("weight_of_criteria:\n",weight_of_criteria(),"\n")
# print("cpu:\n", rating_each_node("cpu"),"\n")[1]
# print("cpu:\n", rating_each_node("memory"),"\n")[1]
# print("lta:\n", rating_each_node("last_time_access_percentage")[1],"\n")
# print("score:\n",score())

# data = dict()
# data["day"] = True
# now = datetime.datetime.now()
# data["day_from"] = now - datetime.timedelta(days=2)
# data["day_to"] = now
# print("cpu:\n", score(**data), "\n")

# print("memory:\n", rating_each_node("memory", **data)[1],"\n")

import numpy as np
import math
import db as database
import pprint
import pandas as pd

pp = pprint.PrettyPrinter()

def weight_of_criteria(*args,**kwargs):
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
                    data_matrix.iloc[data_matrix.index.get_loc(row), data_matrix.columns.get_loc(column)] = comparison[c_key[i]]
                    data_matrix.iloc[data_matrix.index.get_loc(column), data_matrix.columns.get_loc(row)] = 1 / int(comparison[c_key[i]])
                    break
                if column == row:
                    data_matrix.iloc[data_matrix.index.get_loc(row), data_matrix.columns.get_loc(column)] = 1
    data_matrix["3rd root of product"] = data_matrix.product(axis=1) ** (1 / len(parameter))
    data_matrix["priority vector"] = data_matrix["3rd root of product"] / data_matrix["3rd root of product"].sum()
    print(data_matrix)

def rating_each_node(column_name,*args,**kwargs):
    name = column_name
    print("{} rating".format(name))

    # 1. mendapatkan semua data CPU, memory, LTA, cari terendah dan tertinggi, bagi 9 kolom
    kwargs["column"] = "container_id, timestamps, name"
    kwargs["where"] = "status = 'running'"
    kwargs["sort"] = "name"
    container = database.select("containers", **kwargs)
    c_id = '{}'.format([x[0] for x in container])
    c_id = "".join(c_id)
    c_id = c_id[1:-1]
    ts = container[0][1]

    kwargs.clear()
    kwargs["column"] = "container_id, {column}, container_name".format(column=name)
    kwargs["where"] = "container_id IN ({c_id}) AND timestamps = '{ts}'".format(c_id=c_id, ts=ts)
    kwargs["sort"] = "container_name"
    data = database.select("stats", **kwargs)
    data_min = min(data, key=lambda key: key[1])
    data_max = max(data, key=lambda key: key[1])
    data_range = list(np.arange(data_min[1], data_max[1], (data_max[1] - data_min[1]) / 9))

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
            data_matrix.iloc[data_matrix.index.get_loc(row), data_matrix.columns.get_loc(column)] = tz
            # cpu_matrix = cpu_matrix.where(np.triu(np.ones(cpu_matrix.shape)))
            # cpu_matrix = cpu_matrix.transpose()

    # 4. untuk setiap row, hitung nilai geomean dan eigenvector
    data_matrix["3rd root of product"] = data_matrix.product(axis=1) ** (1 / database.total_data("containers"))
    data_matrix["priority vector"] = data_matrix["3rd root of product"] / data_matrix["3rd root of product"].sum()
    # print(data_matrix, "\n")
    return data_matrix

weight_of_criteria()

# print(rating_each_node("cpu"),"\n")
# print(rating_each_node("memory"),"\n")
# print(rating_each_node("last_time_access_percentage"),"\n")

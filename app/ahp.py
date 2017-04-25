import numpy as np
import math
import db as database
import pprint
import pandas as pd
from flask import jsonify
import re
pp = pprint.PrettyPrinter()


def f(num):
    return math.sqrt(math.sqrt(num))


def weight_of_criteria(*args,**kwargs):
    Memory_raw = {"Memory":{0:1,1:2, 2:4}}
    LTA_raw = {"LTA": {0:0.5, 1:1, 2:2}}
    CPU_raw = {"CPU":{0:0.25,1:0.5, 2:1}}
    Memory = pd.DataFrame(Memory_raw)
    LTA = pd.DataFrame(LTA_raw)
    CPU = pd.DataFrame(CPU_raw)
    result = Memory.join(LTA)
    result = result.join(CPU)
    return result

def each_node(*args,**kwargs):
    # langkah2
    # 1. mendapatkan semua data CPU, memory, LTA, cari terendah dan tertinggi, bagi 9 kolom
    kwargs["column"] = "container_id, timestamps, name"
    kwargs["where"] = "status = 'running'"
    kwargs["sort"] = "name"
    container = database.select("containers",**kwargs)
    c_id = '{}'.format([x[0] for x in container])
    c_id = "".join(c_id)
    c_id = c_id[1:-1]
    ts = container[0][1]

    kwargs.clear()
    kwargs["column"] = "container_id, cpu, container_name"
    kwargs["where"] = "container_id IN ({c_id}) AND timestamps = '{ts}'".format(c_id=c_id,ts=ts)
    kwargs["sort"] = "container_name"
    cpu = database.select("stats",**kwargs)
    cpu_min = min(cpu, key=lambda key: key[1])
    cpu_max = max(cpu, key=lambda key: key[1])
    cpu_range = list(np.arange(cpu_min[1], cpu_max[1], (cpu_max[1]-cpu_min[1])/9))

    kwargs.clear()
    kwargs["column"] = "container_id, memory"
    kwargs["where"] = "container_id IN ({c_id}) AND timestamps = '{ts}'".format(c_id=c_id, ts=ts)
    kwargs["sort"] = "container_name"
    memory = database.select("stats",**kwargs)
    memory_min = min(memory, key=lambda key: key[1])
    memory_max = max(memory, key=lambda key: key[1])
    memory_range = list(np.arange(memory_min[1], memory_max[1], (memory_max[1] - memory_min[1]) / 9))

    kwargs.clear()
    kwargs["column"] = "container_id, last_time_access_percentage"
    kwargs["where"] = "container_id IN ({c_id}) AND timestamps = '{ts}'".format(c_id=c_id, ts=ts)
    kwargs["sort"] = "container_name"
    lta = database.select("stats", **kwargs)
    lta_min = min(lta, key=lambda key: key[1])
    lta_max = max(lta, key=lambda key: key[1])
    lta_range = list(np.arange(lta_min[1], lta_max[1], (lta_max[1] - lta_min[1]) / 9))

    # 2. untuk setiap data, cek data ada pada kolom mana, masukkan ke matrik
    c_name = [x[2] for x in container]
    index = c_name
    columns = c_name
    type_data = ['float32'] * len(c_name)
    dtype = list(zip(c_name,type_data))
    values = np.zeros(len(c_name), dtype = dtype)
    cpu_matrix = pd.DataFrame(values, index=index, columns=columns)
    for row in enumerate(cpu_matrix.index.values):
        for column in enumerate(cpu_matrix.columns.values):
            tx = [item for item in cpu if item[2] == row[1]][0][1]
            ty = [item for item in cpu if item[2] == column[1]][0][1]

            for idx,val in enumerate(cpu_range[1:len(cpu_range)]):
                if (tx >=cpu_range[idx-1] and tx < cpu_range[idx]):
                    tx = idx
                    break
                elif tx>=cpu_range[len(cpu_range)-1]:
                    tx = len(cpu_range)
                    break

            for idx,val in enumerate(cpu_range[1:len(cpu_range)]):
                if (ty >=cpu_range[idx-1] and ty < cpu_range[idx]):
                    ty = idx
                    break
                elif ty>=cpu_range[len(cpu_range)-1]:
                    ty = len(cpu_range)
                    break

            # 3. Bandingkan row dan column
            tz = tx/ty
            cpu_matrix.iloc[cpu_matrix.index.get_loc(row[1]), cpu_matrix.columns.get_loc(column[1])] = tz
            # cpu_matrix = cpu_matrix.where(np.triu(np.ones(cpu_matrix.shape)))
            # cpu_matrix = cpu_matrix.transpose()

    # 4. untuk setiap row, cari nilai geomean dan eigenvector
    cpu_matrix["3rd root of product"] = cpu_matrix.product(axis=1) ** (1 / 3)
    cpu_matrix["priority vector"] = cpu_matrix["3rd root of product"] / cpu_matrix["3rd root of product"].sum()
    print(cpu_matrix)

    # 6. pastikan nilai sum of eigenvector = 1

each_node()

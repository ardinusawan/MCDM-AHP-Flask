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
    kwargs["column"] = "container_id, timestamps"
    kwargs["where"] = "status = 'running'"
    container = database.select("containers",**kwargs)
    c_id = '{}'.format([x[0] for x in container])
    c_id = "".join(c_id)
    c_id = c_id[1:-1]
    ts = container[0][1]

    kwargs.clear()
    kwargs["column"] = "container_id, cpu"
    kwargs["where"] = "container_id IN ({c_id}) AND timestamps = '{ts}'".format(c_id=c_id,ts=ts)
    cpu = database.select("stats",**kwargs)
    cpu_min = min(cpu, key=lambda key: key[1])
    cpu_max = max(cpu, key=lambda key: key[1])
    cpu_range = list(np.arange(cpu_min[1], cpu_max[1], (cpu_max[1]-cpu_min[1])/9))

    kwargs.clear()
    kwargs["column"] = "container_id, memory"
    kwargs["where"] = "container_id IN ({c_id}) AND timestamps = '{ts}'".format(c_id=c_id, ts=ts)
    memory = database.select("stats",**kwargs)
    memory_min = min(memory, key=lambda key: key[1])
    memory_max = max(memory, key=lambda key: key[1])
    memory_range = list(np.arange(memory_min[1], memory_max[1], (memory_max[1] - memory_min[1]) / 9))

    kwargs.clear()
    kwargs["column"] = "container_id, last_time_access_percentage"
    kwargs["where"] = "container_id IN ({c_id}) AND timestamps = '{ts}'".format(c_id=c_id, ts=ts)
    lta = database.select("stats", **kwargs)
    lta_min = min(lta, key=lambda key: key[1])
    lta_max = max(lta, key=lambda key: key[1])
    lta_range = list(np.arange(lta_min[1], lta_max[1], (lta_max[1] - lta_min[1]) / 9))

    # 2. untuk setiap data, cek data ada pada kolom mana, masukkan ke matrik
    # 3. kalikan row dan column
    # 4. untuk setiap row, cari nilai geomean
    # 5. untuk setiap row, cari eigenvector
    # 6. pastikan nilai sum of eigenvector = 1


    # membandingkan
    # for i in range(len(result.columns)):
    #     for j in range(len(result.columns)):
    #         # result.iloc[i][j] = result.iloc[i][j] / result.iloc[j][i]
    #         # result.iloc[j][i] = 1 / result.iloc[i][j]
    #         pass
    # geomean dan eigenvector
    # for i in range(len(result.columns)):
    #     for j in range(len(result.columns)):
    #         pass
            # result.index.names = "A"
            # # result.index = {"docker1","docker2"}
            # a = result.iloc[1][0] * result["docker2"][1]
            # print(result)
            # print(a)

each_node()

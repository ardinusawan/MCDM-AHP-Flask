import numpy as np
import math
import db as database
import pprint

pp = pprint.PrettyPrinter()

def f(num):
    return math.sqrt(math.sqrt(num))

def get_container(**kwargs):
    kwargs["sort"] = {"column": "name", "order": "ASD"}
    kwargs["select"] = {"data":"container_id"}

    data = database.all_data(table_name, **kwargs)
    return data

# langkah 1
# data = np.array(
#     [
#         (1.0, 1.0 / 3, 1 / 9, 1 / 5),
#         (3.0, 1.0, 1.0, 1.0),
#         (9.0, 1.0, 1.0, 3.0),
#         (5.0, 1.0, 1 / 3, 1.0)],dtype=[('MSFT','float'),('CSCO','float'),('GOOG','float'),('F','float')])
def weight_of_criteria():
    data = np.matrix([
        # memory,waktu,cpu
        [1, 2, 4],
        [0.5, 1, 2],
        [0.25, 0.5, 1]])
    total = 0
    weigh_of_criteria = []
    for idx, val in enumerate(data):
        temp = 1
        for val2 in range(val.size):
            temp = temp * val.item(val2)
        weigh_of_criteria.append(f(temp))
        # print(t[idx])
        total += f(temp)
    for i in range(len(weigh_of_criteria)):
        weigh_of_criteria[i] = weigh_of_criteria[i] / total

    # memory,waktu,cpu
    return weigh_of_criteria

'''
def rating_of_each_node(*args, **kwargs):
    params = ''.join(args)
    if params == "LTA":
        params = 7
    table_name = "containers"
    sort = {"column": "name", "order": "ASD"}
    total = database.total_data(table_name)

    # mendapatkan semua container id, ASC nama kontainer
    data = database.all_data(table_name, **sort)

    temp = np.zeros((total,total))
    for i in range(total):
        # mendapatkan data terakhir pada stats
        ts = "'" + data[i][3].strftime('%Y-%m-%d %H:%M:%S') + "'"
        container_id = "'" + data[i][0] + "'"
        find_by = {"container_id": container_id, "timestamps": ts}
        res1 = database.find_data("stats", **find_by)
        # hitung dari 1 - n, n1/nN
        for j in range(total):
            # mendapatkan data terakhir pada stats
            ts = "'" + data[j][3].strftime('%Y-%m-%d %H:%M:%S') + "'"
            container_id = "'" + data[j][0] + "'"
            find_by = {"container_id": container_id, "timestamps": ts}
            res2 = database.find_data("stats", **find_by)
            # print(res[0][params])
            temp[i][j] = res1[0][params]/res2[0][params]


        # temp = data[i]
        # setelah dapat, buat skala antara 1 - 9, dari 0 sampai +- data terbesar
        # untuk setiap hasil perbandingan, bandingkan cocoknya berada pada posisi mana, apakah - atau 0 atau +
        # taruh dalam list
    print(temp)
    print("min: ",np.amin(temp),"\nmax: ",np.amax(temp))
'''
def rating_of_each_node(*args, **kwargs):
    params = ''.join(args)
    if params == "CPU":
        params = 3
    elif params == "Memory":
        params = 5
    elif params == "LTA":
        params = 7
    table_name = "containers"
    total = database.total_data(table_name)
    kwargs["sort"] = {"column": "name", "order": "ASD"}
    data = database.all_data(table_name, **kwargs)

    temp = np.zeros(total)
    sum = 0
    for i in range(total):
        # mendapatkan data terakhir pada stats
        ts = "'" + data[i][3].strftime('%Y-%m-%d %H:%M:%S') + "'"
        container_id = "'" + data[i][0] + "'"
        find_by = {"container_id": container_id, "timestamps": ts}
        res = database.find_data("stats", **find_by)

        sum += res[0][params]

    for j in range(total):
        ts = "'" + data[j][3].strftime('%Y-%m-%d %H:%M:%S') + "'"
        container_id = "'" + data[j][0] + "'"
        find_by = {"container_id": container_id, "timestamps": ts}
        res = database.find_data("stats", **find_by)
        if sum == 0:
            sum = 1
        temp[j]= res[0][params]/sum
    return temp


table_name = "containers"
total = database.total_data(table_name)

option = weight_of_criteria()

score = [0] * total
node = [0] * total
calculate = "Memory"
node[0] = rating_of_each_node(*calculate)
calculate = "LTA"
node[1] = rating_of_each_node(*calculate)
calculate = "CPU"
node[2] = rating_of_each_node(*calculate)

for i in range(total-1):
    for j in range(total-1):
        score[i] += node[i][j] * option[j]

container = []
for item in get_container():
    container.append(str(item[0]))

data = dict(zip(container,score))
container_selected = max(data, key=lambda key: data[key])
print("Last Score for each node:")
pp.pprint(data)
print("Best container to kill:",container_selected)
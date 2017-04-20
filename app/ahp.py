import numpy as np
import math
import db as DB

def f(num):
    return math.sqrt(math.sqrt(num))

#langkah 1
# data = np.array(
#     [
#         (1.0, 1.0 / 3, 1 / 9, 1 / 5),
#         (3.0, 1.0, 1.0, 1.0),
#         (9.0, 1.0, 1.0, 3.0),
#         (5.0, 1.0, 1 / 3, 1.0)],dtype=[('MSFT','float'),('CSCO','float'),('GOOG','float'),('F','float')])
data = np.matrix([
    [1, 2, 4],
    [0.5, 1, 2],
    [0.25, 0.5, 1]])
sum = 0
weigh_of_criteria = []
for idx, val in enumerate(data):
    temp = 1
    for val2 in range(val.size):
        temp = temp * val.item(val2)
    weigh_of_criteria.append(f(temp))
    # print(t[idx])
    sum += f(temp)
for i in range(len(weigh_of_criteria)):
    print(weigh_of_criteria[i] / sum)


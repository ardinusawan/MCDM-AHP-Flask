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
    [1, 1 / 3, 1 / 9, 1 / 5],
    [3, 1, 1, 1],
    [9, 1, 1, 3],
    [5, 1, 1 / 3, 1]])
sum = 0
t = []
for idx, val in enumerate(data):
    temp = 1
    for val2 in range(val.size):
        temp = temp * val.item(val2)
    t.append(f(temp))
    # print(t[idx])
    sum += f(temp)
for i in range(len(t)):
    print(t[i] / sum)


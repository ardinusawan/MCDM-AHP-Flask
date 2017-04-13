import numpy as np
import math


def f(num):
    return math.sqrt(math.sqrt(num))

#langkah 1

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
        # print(val.item(val2))
        temp = temp * val.item(val2)
    t.append(f(temp))
    print(t[idx])
    sum += f(temp)
print(t[0] / sum)


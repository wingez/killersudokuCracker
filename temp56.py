def f(n):
    s = 1
    m = n
    while m >= 1:
        for i in range(1,int(m)):
            s += 1
        m /= 2
    return s


import numpy as np
import matplotlib.pyplot as plt

n=100_000_000

x = np.linspace(0, n)
y = np.array(list(map(f, x)))

plt.plot(x, y, 'o', color='black')
plt.show()
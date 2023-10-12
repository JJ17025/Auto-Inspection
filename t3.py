import numpy as np

e = np.array(1.0, dtype=np.float16)

while e + 1 != 1:
    e = e / 2

print(e)  # 1.1102230246251565e-16
print(type(e))  # <class 'numpy.float64'>

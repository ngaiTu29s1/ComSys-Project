import sys, platform
import numpy as np
import pandas as pd
import sklearn
import simpy

print("PY:", sys.executable)
print("OS:", platform.platform())
print("numpy:", np.__version__)
print("pandas:", pd.__version__)
print("sklearn:", sklearn.__version__)
print("simpy:", simpy.__version__)

# thử một phép tính nhỏ với numpy
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print("dot(a,b):", a @ b)

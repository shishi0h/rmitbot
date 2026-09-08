import array
import numpy as np

merged_data = np.full((10, 10), -1, dtype=np.int8)
# Test 1: tolist
l = merged_data.ravel().tolist()
# Test 2: array.array from bytes
a = array.array('b', merged_data.tobytes())
print(len(l) == len(a))
print(l[0] == a[0])

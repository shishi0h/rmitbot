import numpy as np
import scipy.ndimage
import math

# Grid 3x3
arr = np.zeros((3, 3))
arr[0, 2] = 1 # y=0, x=2
# If we rotate by 90 degrees CCW, x=2, y=0 should become x=0, y=2?
# In standard math: (1, 0) rotated by 90 is (0, 1). So (2, 0) -> (0, 2).
rot = scipy.ndimage.rotate(arr, 90, reshape=True, order=0)
print(np.where(rot == 1))

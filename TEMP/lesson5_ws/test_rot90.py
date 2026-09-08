import numpy as np

arr = np.array([
    [1, 2],
    [3, 4]
])
# arr[0,0]=1, arr[0,1]=2, arr[1,0]=3, arr[1,1]=4
# Y is row (0=bottom? In ROS, origin is usually bottom-left. Let's assume standard matrix)

rot_cw = np.rot90(arr, k=-1)
print("Rotated CW 90 (-90 deg):")
print(rot_cw)

rot_ccw = np.rot90(arr, k=1)
print("Rotated CCW 90 (+90 deg):")
print(rot_ccw)

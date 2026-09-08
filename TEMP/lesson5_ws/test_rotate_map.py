import numpy as np
import scipy.ndimage
import math

def get_rotated_map(src_data, origin_x_local, origin_y_local, res, tf_x, tf_y, yaw_rad):
    yaw_deg = math.degrees(yaw_rad)
    
    # 1. Rotate the array
    # scipy.ndimage.rotate rotates counter-clockwise.
    rotated_data = scipy.ndimage.rotate(src_data, yaw_deg, reshape=True, order=0, cval=-1)
    
    height, width = src_data.shape
    new_height, new_width = rotated_data.shape
    
    # 2. Calculate centers
    cx_local = origin_x_local + (width * res) / 2.0
    cy_local = origin_y_local + (height * res) / 2.0
    
    cx_global = cx_local * math.cos(yaw_rad) - cy_local * math.sin(yaw_rad) + tf_x
    cy_global = cx_local * math.sin(yaw_rad) + cy_local * math.cos(yaw_rad) + tf_y
    
    # 3. Calculate new origin
    new_origin_x = cx_global - (new_width * res) / 2.0
    new_origin_y = cy_global - (new_height * res) / 2.0
    
    return rotated_data, new_origin_x, new_origin_y

# Simple test
src = np.array([[100]]) # 1x1, origin 0,0, res 1. tf_x 5, tf_y 5, yaw 90 deg
rot, nx, ny = get_rotated_map(src, 0, 0, 1.0, 5, 5, math.radians(90))
print(nx, ny) # should be 5, 5. wait! cx_local=0.5, cy_local=0.5.
# cx_global = 0.5*0 - 0.5*1 + 5 = 4.5
# cy_global = 0.5*1 + 0.5*0 + 5 = 5.5
# new_origin_x = 4.5 - 0.5 = 4.0
# new_origin_y = 5.5 - 0.5 = 5.0
# Let's see!

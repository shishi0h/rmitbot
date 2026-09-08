import re

with open("/home/ben/Testing/lesson5_ws/src/rmitbot_description/launch/gazebo.launch.py", "r") as f:
    text = f.read()
text = text.replace('"-Y", "0.0"', '"-Y", "4.71"')
with open("/home/ben/Testing/lesson5_ws/src/rmitbot_description/launch/gazebo.launch.py", "w") as f:
    f.write(text)

with open("/home/ben/Testing/lesson5_ws/src/rmitbot_mapping/launch/mapping.launch.py", "r") as f:
    text = f.read()
text = text.replace("'--yaw', '0.0'", "'--yaw', '4.71'")
with open("/home/ben/Testing/lesson5_ws/src/rmitbot_mapping/launch/mapping.launch.py", "w") as f:
    f.write(text)

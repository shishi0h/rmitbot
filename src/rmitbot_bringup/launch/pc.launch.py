import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, TimerAction, RegisterEventHandler
from ament_index_python.packages import get_package_share_directory
from launch.event_handlers import OnProcessExit

# Launch the file
# ros2 launch rmitbot_bringup pc.launch.py

def generate_launch_description():
    
    # Launch rviz
    rviz = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_description"),
            "launch", "rviz.launch.py"
        ),
    )
    
    # Launch the twistmux instead of keyboard node only
    twistmux = IncludeLaunchDescription(
        os.path.join(get_package_share_directory("rmitbot_navigation"),
            "launch","twistmux.launch.py"
        ),
    )
    
    navigation = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_navigation"),
            "launch","nav.launch.py"
        ),
    )
    
    # Delay the navigation node, to make sure that a map is available
    navigation_delayed = TimerAction(
        period = 5., 
        actions=[navigation]
    )
    
    # PC launches rviz, twistmux, and nav2
    # RPI launches rsp, controller, rplidar, slamtoolbox
    return LaunchDescription([
        rviz, 
        twistmux, 
        navigation_delayed,         
    ])
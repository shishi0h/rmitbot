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
    
    from launch.actions import GroupAction
    from launch_ros.actions import PushRosNamespace

    # Launch twistmux for robot1 (with joy and keyboard)
    twistmux_robot1 = GroupAction([
        PushRosNamespace('robot1'),
        IncludeLaunchDescription(
            os.path.join(get_package_share_directory("rmitbot_navigation"),
                "launch","twistmux.launch.py"
            ),
            launch_arguments={
                'prefix': 'robot1/',
                'use_joy': 'true',
                'use_keyboard': 'true'
            }.items()
        )
    ])
    
    # Launch twistmux for robot2 (with keyboard only)
    twistmux_robot2 = GroupAction([
        PushRosNamespace('robot2'),
        IncludeLaunchDescription(
            os.path.join(get_package_share_directory("rmitbot_navigation"),
                "launch","twistmux.launch.py"
            ),
            launch_arguments={
                'prefix': 'robot2/',
                'use_joy': 'false',
                'use_keyboard': 'true'
            }.items()
        )
    ])
    
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
    
    # Launch map merge
    map_merge = IncludeLaunchDescription(
        os.path.join(get_package_share_directory("rmitbot_map_merge"),
            "launch", "map_merge.launch.py"
        ),
    )

    # PC launches rviz, twistmux, nav2, and map_merge
    # RPI launches rsp, controller, rplidar, slamtoolbox
    return LaunchDescription([
        rviz, 
        twistmux_robot1,
        twistmux_robot2, 
        map_merge,
        # navigation_delayed,         
    ])
    
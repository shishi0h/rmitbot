import os
from launch import LaunchDescription
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory

from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

# CLI command (just in case)
# ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/my_robot_controller/cmd_vel -p stamped:=True

def generate_launch_description():
    
    teleop_robot0 = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_robot0',
        output='screen',
        prefix='xterm -T "Robot 0 Teleop" -e',
        parameters=[
            {"use_sim_time": True},
            {"stamped": True}
        ],
        remappings=[
        ('cmd_vel', '/robot_0/diff_drive_controller/cmd_vel')
        ]
    )   


    teleop_robot1 = Node(
    package='teleop_twist_keyboard',
    executable='teleop_twist_keyboard',
    name='teleop_robot1',
    output='screen',
    prefix='xterm -T "Robot 1 Teleop" -e',
    parameters=[
        {"use_sim_time": True},
        {"stamped": True}
    ],
    remappings=[
        ('cmd_vel', '/robot_1/diff_drive_controller/cmd_vel')
    ]
)
    
    return LaunchDescription(
        [
            teleop_robot0, 
            teleop_robot1,
        ]
    )
    
    
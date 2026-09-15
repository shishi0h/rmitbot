import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    
    prefix = LaunchConfiguration('prefix')
    prefix_arg = DeclareLaunchArgument('prefix', default_value='')

    return LaunchDescription([
        prefix_arg,
        Node(
            package='rplidar_ros',
            executable='rplidar_composition',
            output='screen',
            parameters=[{
                'serial_port': '/dev/ttyUSB2',
                'frame_id': [prefix, 'laser_link'],
                'angle_compensate': True,
                'scan_mode': 'Standard',
                'use_sim_time': False, 
            }]
        )
    ])
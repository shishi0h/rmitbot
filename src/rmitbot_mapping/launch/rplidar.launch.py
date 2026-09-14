import os
from launch import LaunchDescription
from launch_ros.actions import Node

from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.actions import DeclareLaunchArgument

def generate_launch_description():
    prefix = LaunchConfiguration('prefix', default='')
    prefix_arg = DeclareLaunchArgument('prefix', default_value='')

    return LaunchDescription([
        prefix_arg,

        Node(
            package='rplidar_ros',
            executable='rplidar_composition',
            output='screen',
            parameters=[{
                'serial_port': '/dev/ttyUSB0',
                # 'serial_port': '/dev/rplidar',
                'frame_id': PythonExpression(["'", prefix, "' + 'laser_link'"]),
                'serial_baudrate': 115200,
                'angle_compensate': True,
                'scan_mode': 'Standard', 
                'use_sim_time': False, # This is important for simulation/hardware
            }]
        )
    ])
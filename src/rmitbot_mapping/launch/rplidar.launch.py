import os
from launch import LaunchDescription
from launch_ros.actions import Node

from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.actions import DeclareLaunchArgument

def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    namespace_arg = DeclareLaunchArgument('namespace', default_value='')
    
    serial_port_arg = DeclareLaunchArgument(
        'serial_port', 
        default_value='/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'
    )
    
    frame_id = PythonExpression(["'", namespace, "/laser_link' if '", namespace, "' else 'laser_link'"])

    return LaunchDescription([
        namespace_arg,
        serial_port_arg,
        Node(
            package='rplidar_ros',
            executable='rplidar_composition',
            output='screen',
            parameters=[{
                'serial_port': LaunchConfiguration('serial_port'),
                'frame_id': frame_id,
                'angle_compensate': True,
                'scan_mode': 'Standard', 
                'use_sim_time': False,
            }]
        )
    ])
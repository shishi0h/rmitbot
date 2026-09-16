import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    namespace = LaunchConfiguration('namespace')

    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Top-level namespace'
    )
    
    bypass_cliff_sensor = LaunchConfiguration('bypass_cliff_sensor')
    bypass_cliff_sensor_arg = DeclareLaunchArgument(
        'bypass_cliff_sensor',
        default_value='false',
        description='Bypass the cliff safety filter logic'
    )

    cliff_sensor_node = Node(
        package='rmitbot_cliff_sensor',
        executable='cliff_sensor_node',
        name='cliff_sensor_node',
        output='screen',
        parameters=[{
            'use_sim_time': False,
            'port': '/dev/serial/by-path/platform-xhci-hcd.1-usb-0:2:1.0-port0',
            'cliff_threshold': 0.50
        }]
    )

    cliff_safety_filter_node = Node(
        package='rmitbot_cliff_sensor',
        executable='cliff_safety_filter_node',
        name='cliff_safety_filter_node',
        output='screen',
        parameters=[{
            'use_sim_time': False,
            'cliff_threshold': 0.50,
            'bypass_cliff_sensor': bypass_cliff_sensor
        }],
        remappings=[
            ('cmd_vel_filter', 'diff_drive_controller/cmd_vel')
        ]
    )

    return LaunchDescription([
        namespace_arg,
        bypass_cliff_sensor_arg,
        cliff_sensor_node,
        cliff_safety_filter_node
    ])

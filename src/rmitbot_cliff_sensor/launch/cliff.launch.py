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

    cliff_sensor_node = Node(
        package='rmitbot_cliff_sensor',
        executable='cliff_sensor_node',
        name='cliff_sensor_node',
        namespace=namespace,
        output='screen',
        parameters=[{
            'use_sim_time': False,
            'port': '/dev/ttyUSB2',
            'cliff_threshold': 0.15
        }]
    )

    cliff_safety_filter_node = Node(
        package='rmitbot_cliff_sensor',
        executable='cliff_safety_filter_node',
        name='cliff_safety_filter_node',
        namespace=namespace,
        output='screen',
        parameters=[{
            'use_sim_time': False,
            'cliff_threshold': 0.15
        }],
        remappings=[
            ('cmd_vel_filter', 'diff_drive_controller/cmd_vel')
        ]
    )

    return LaunchDescription([
        namespace_arg,
        cliff_sensor_node,
        cliff_safety_filter_node
    ])

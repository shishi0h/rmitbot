import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    cliff_sensor_node = Node(
        package='rmitbot_cliff_sensor',
        executable='cliff_sensor_node',
        name='cliff_sensor_node',
        output='screen',
        parameters=[{'use_sim_time': False}]
    )

    cliff_safety_filter_node = Node(
        package='rmitbot_cliff_sensor',
        executable='cliff_safety_filter_node',
        name='cliff_safety_filter_node',
        output='screen',
        parameters=[{'use_sim_time': False}]
    )

    return LaunchDescription([
        cliff_sensor_node,
        cliff_safety_filter_node
    ])

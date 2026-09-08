import os

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    map_merge_node = Node(
        package='rmitbot_map_merge',
        executable='map_merge_node',
        name='map_merge_node',
        output='screen',
        parameters=[
            {"use_sim_time": True},
            {"robot0_topic": "/robot_0/map"},
            {"robot1_topic": "/robot_1/map"},
            {"merged_topic": "/map"}
        ]
    )

    global_costmap_merge_node = Node(
        package='rmitbot_map_merge',
        executable='map_merge_node',
        name='global_costmap_merge_node',
        output='screen',
        parameters=[
            {"use_sim_time": True},
            {"robot0_topic": "/robot_0/global_costmap/costmap"},
            {"robot1_topic": "/robot_1/global_costmap/costmap"},
            {"merged_topic": "/global_costmap/costmap"}
        ]
    )

    local_costmap_merge_node = Node(
        package='rmitbot_map_merge',
        executable='map_merge_node',
        name='local_costmap_merge_node',
        output='screen',
        parameters=[
            {"use_sim_time": True},
            {"robot0_topic": "/robot_0/local_costmap/costmap"},
            {"robot1_topic": "/robot_1/local_costmap/costmap"},
            {"merged_topic": "/local_costmap/costmap"}
        ]
    )

    return LaunchDescription([
        map_merge_node,
        global_costmap_merge_node,
        local_costmap_merge_node
    ])

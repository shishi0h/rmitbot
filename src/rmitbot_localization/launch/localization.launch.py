from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import os

def generate_launch_description():

    prefix = LaunchConfiguration('prefix')
    prefix_arg = DeclareLaunchArgument('prefix', default_value='')

    ekf_config = os.path.join(get_package_share_directory("rmitbot_localization"), "config", "ekf.yaml")

    robot_localization = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        output="screen",
        parameters=[
            ekf_config,
            {
                "map_frame": "map",
                "odom_frame": [prefix, "odom"],
                "base_link_frame": [prefix, "base_footprint"],
                "world_frame": [prefix, "odom"],
            }
        ],
    )

    return LaunchDescription([
        prefix_arg,
        robot_localization,
    ])
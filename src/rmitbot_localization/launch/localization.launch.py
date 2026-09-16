from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import UnlessCondition, IfCondition
import os

def generate_launch_description():

    namespace = LaunchConfiguration('namespace')
    namespace_arg = DeclareLaunchArgument('namespace', default_value='')

    base_frame_id = PythonExpression(["'", namespace, "/base_footprint' if '", namespace, "' else 'base_footprint'"])
    odom_frame_id = PythonExpression(["'", namespace, "/odom' if '", namespace, "' else 'odom'"])
    map_frame_id = 'map' # Global map for swarm
    robot_localization = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        output="screen",
        parameters=[
            os.path.join(get_package_share_directory("rmitbot_localization"), "config", "ekf.yaml"),
            {
                'map_frame': map_frame_id,
                'odom_frame': odom_frame_id,
                'base_link_frame': base_frame_id,
                'world_frame': odom_frame_id
            }
        ],
    )

    return LaunchDescription([
        namespace_arg,
        robot_localization,
    ])
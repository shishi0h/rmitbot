from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
import os


def generate_launch_description():

    pkg_path = get_package_share_directory("rmitbot_localization")
    ekf_config = os.path.join(pkg_path, "config", "ekf.yaml")
    print(f"EKF config: {ekf_config}")

    nodes = []

    for i in range(2):

        namespace = f"robot_{i}"

        ekf_node = Node(
            package="robot_localization",
            executable="ekf_node",
            namespace=namespace,
            name="ekf_filter_node",
            output="screen",

            parameters=[
                ekf_config,
                {
                    "map_frame": "map",
                    "odom_frame": f"{namespace}/odom",
                    "base_link_frame": f"{namespace}/base_footprint",
                    "world_frame": f"{namespace}/odom",
                    "odom0": f"/{namespace}/odom",
                }
            ],

        )

        nodes.append(ekf_node)

    return LaunchDescription(nodes)
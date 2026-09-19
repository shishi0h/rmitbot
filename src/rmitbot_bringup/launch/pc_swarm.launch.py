import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, TimerAction, GroupAction
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import PushRosNamespace

def generate_launch_description():
    
    # Rviz
    rviz = IncludeLaunchDescription(
        os.path.join(get_package_share_directory("rmitbot_description"), "launch", "rviz.launch.py")
    )
    
    # Map Merge
    map_merge = IncludeLaunchDescription(
        os.path.join(get_package_share_directory("rmitbot_map_merge"), "launch", "map_merge.launch.py")
    )

    # Robot 1 (Smallbot) Nodes
    twistmux_1 = IncludeLaunchDescription(
        os.path.join(get_package_share_directory("rmitbot_navigation"), "launch", "twistmux.launch.py"),
        launch_arguments={'namespace': 'robot_1', 'joy_dev': '0'}.items()
    )
    navigation_1 = IncludeLaunchDescription(
        os.path.join(get_package_share_directory("rmitbot_navigation"), "launch", "nav.launch.py"),
        launch_arguments={'namespace': 'robot_1'}.items()
    )
    robot_1_nodes = GroupAction([PushRosNamespace('robot_1'), twistmux_1, TimerAction(period=5., actions=[navigation_1])])

    # Robot 2 (Bigbot) Nodes
    twistmux_2 = IncludeLaunchDescription(
        os.path.join(get_package_share_directory("rmitbot_navigation"), "launch", "twistmux.launch.py"),
        launch_arguments={'namespace': 'robot_2', 'joy_dev': '1'}.items()
    )
    navigation_2 = IncludeLaunchDescription(
        os.path.join(get_package_share_directory("rmitbot_navigation"), "launch", "nav.launch.py"),
        launch_arguments={'namespace': 'robot_2'}.items()
    )
    robot_2_nodes = GroupAction([PushRosNamespace('robot_2'), twistmux_2, TimerAction(period=7., actions=[navigation_2])])

    # Static TFs for map merging
    static_tf_robot_1 = Node(
        package="tf2_ros", executable="static_transform_publisher", name="static_tf_pub_robot_1",
        arguments=["--x", "0.0", "--y", "0.0", "--z", "0.0", "--yaw", "0.0", "--pitch", "0.0", "--roll", "0.0", "--frame-id", "map", "--child-frame-id", "robot_1/map"]
    )
    static_tf_robot_2 = Node(
        package="tf2_ros", executable="static_transform_publisher", name="static_tf_pub_robot_2",
        arguments=["--x", "-1.0", "--y", "0.0", "--z", "0.0", "--yaw", "0.0", "--pitch", "0.0", "--roll", "0.0", "--frame-id", "map", "--child-frame-id", "robot_2/map"]
    )

    return LaunchDescription([
        rviz,
        map_merge,
        robot_1_nodes,
        robot_2_nodes,
        static_tf_robot_1,
        static_tf_robot_2
    ])

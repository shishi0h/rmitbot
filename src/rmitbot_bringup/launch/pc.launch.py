import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, TimerAction, RegisterEventHandler
from ament_index_python.packages import get_package_share_directory
from launch.event_handlers import OnProcessExit
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import PushRosNamespace

# Launch the file
# ros2 launch rmitbot_bringup pc.launch.py

def generate_launch_description():
    
    namespace = LaunchConfiguration('namespace')
    namespace_arg = DeclareLaunchArgument('namespace', default_value='')
    
    use_advanced_merge = LaunchConfiguration('use_advanced_merge')
    use_advanced_merge_arg = DeclareLaunchArgument(
        'use_advanced_merge', 
        default_value='false',
        description='Set to true to use the official multirobot_map_merge package for feature-matching map alignment (requires package installation)'
    )

    # Launch rviz
    rviz = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_description"),
            "launch", "rviz.launch.py"
        ),
    )
    
    # Launch the twistmux instead of keyboard node only
    twistmux = IncludeLaunchDescription(
        os.path.join(get_package_share_directory("rmitbot_navigation"),
            "launch","twistmux.launch.py"
        ),
    )
    
    navigation = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_navigation"),
            "launch","nav.launch.py"
        ),
        launch_arguments={'namespace': namespace}.items()
    )
    
    # Delay the navigation node, to make sure that a map is available
    navigation_delayed = TimerAction(
        period = 5., 
        actions=[navigation]
    )
    

    # Custom basic Map merge (Tape-on-floor method)
    custom_map_merge = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_map_merge"),
            "launch", "map_merge.launch.py"
        ),
        condition=UnlessCondition(use_advanced_merge)
    )

    # Official Advanced Map merge (Auto-discovery method)
    advanced_map_merge = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("multirobot_map_merge"),
            "launch", "map_merge.launch.py"
        ),
        condition=IfCondition(use_advanced_merge)
    )

    # PC launches rviz, twistmux, and nav2
    namespaced_nodes = GroupAction([
        PushRosNamespace(namespace),
        rviz, 
        twistmux, 
        navigation_delayed, 
    ])
    
    # Static transform publishers to link the global map to individual robot maps (Only used for the custom script)
    static_tf_robot_1 = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_tf_pub_robot_1",
        output="screen",
        arguments=[
            "--x", "0.0", "--y", "0.0", "--z", "0.0", 
            "--yaw", "0.0", "--pitch", "0.0", "--roll", "0.0",
            "--frame-id", "map", "--child-frame-id", "robot_1/map"
        ],
        condition=UnlessCondition(use_advanced_merge)
    )

    static_tf_robot_2 = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_tf_pub_robot_2",
        output="screen",
        arguments=[
            "--x", "-1.0", "--y", "0.0", "--z", "0.0", 
            "--yaw", "0.0", "--pitch", "0.0", "--roll", "0.0",
            "--frame-id", "map", "--child-frame-id", "robot_2/map"
        ],
        condition=UnlessCondition(use_advanced_merge)
    )

    return LaunchDescription([
        namespace_arg,
        use_advanced_merge_arg,
        namespaced_nodes,
        custom_map_merge,
        advanced_map_merge,
        static_tf_robot_1,
        static_tf_robot_2
    ])
    
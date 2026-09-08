import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription

from launch.actions import (
    DeclareLaunchArgument,
    EmitEvent,
    LogInfo,
    RegisterEventHandler,
)

from launch.conditions import IfCondition

from launch.events import matches_action

from launch.substitutions import (
    AndSubstitution,
    LaunchConfiguration,
    NotSubstitution,
)

from launch_ros.actions import LifecycleNode, Node

from launch_ros.event_handlers import OnStateTransition

from launch_ros.events.lifecycle import ChangeState

from lifecycle_msgs.msg import Transition

# ros2 launch rmitbot_mapping slam.launch.py use_sim_time:=true
# ros2 launch rmitbot_mapping slam.launch.py use_sim_time:=false
# Command line
# ros2 launch slam_toolbox online_async_launch.py params_file:=./scr/rmitbot_mapping/config/slam.yaml use_sim_time:=true

# pkg_path_slam_toolbox = get_package_share_directory("slam_toolbox")
# pkg_path_mapping = get_package_share_directory("rmitbot_mapping")
# config_mapping =   os.path.join(pkg_path_mapping, 'config', 'slam.yaml')

# def generate_launch_description():
    
#     slam_mapping = IncludeLaunchDescription(
#         os.path.join(pkg_path_slam_toolbox,"launch","online_async_launch.py"),
#         launch_arguments={
#             'params_file': config_mapping,             
#             'use_sim_time': "true", 
#             }.items()
#     )
    
#     return LaunchDescription([
#         slam_mapping,
#     ])

def generate_launch_description():

    pkg_path_mapping = get_package_share_directory(
        "rmitbot_mapping"
    )

    config_mapping = os.path.join(
        pkg_path_mapping,
        "config",
        "slam.yaml"
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    autostart = LaunchConfiguration("autostart")

    robot_names = [
        "robot_0",
        "robot_1",
    ]

    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation clock"
    )

    declare_autostart = DeclareLaunchArgument(
        "autostart",
        default_value="true",
        description="Automatically configure and activate SLAM Toolbox"
    )

    nodes = []

    # -------------------------------------------------------
    # Launch one SLAM Toolbox node for each robot
    # -------------------------------------------------------



    for i in range(2):
        ns = robot_names[i]

        slam = LifecycleNode(
            package="slam_toolbox",
            executable="async_slam_toolbox_node",
            namespace=ns,
            name="slam_toolbox",
            output="screen",

            parameters=[
                config_mapping,
                {
                    "use_sim_time": use_sim_time,

                    "odom_frame": f"{ns}/odom",
                    "base_frame": f"{ns}/base_footprint",
                    "map_frame": f"{ns}/map",

                    "scan_topic": "scan",
                }
            ],

            # We will verify these remappings after testing.
            # If they work, each robot publishes its own map.
            remappings=[
                ("/map", f"/{ns}/map"),
                ("/map_metadata", f"/{ns}/map_metadata"),
            ],
        )

        nodes.append(slam)


        configure_event = EmitEvent(
            event=ChangeState(
                lifecycle_node_matcher=matches_action(slam),
                transition_id=Transition.TRANSITION_CONFIGURE,
            ),
            condition=IfCondition(autostart),
        )

        activate_event = RegisterEventHandler(
            OnStateTransition(
                target_lifecycle_node=slam,
                start_state="configuring",
                goal_state="inactive",
                entities=[
                    LogInfo(msg=f"{ns}: activating SLAM Toolbox"),
                    EmitEvent(
                        event=ChangeState(
                            lifecycle_node_matcher=matches_action(slam),
                            transition_id=Transition.TRANSITION_ACTIVATE,
                        )
                    ),
                ],
            )
        )

        nodes.append(activate_event)
        nodes.append(configure_event)
        

   
    return LaunchDescription([
    declare_use_sim_time,
    declare_autostart,
    *nodes,
])
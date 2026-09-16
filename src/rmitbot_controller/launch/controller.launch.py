import os
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PythonExpression

# ros2 launch rmitbot_controller controller.launch.py

def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    namespace_arg = DeclareLaunchArgument('namespace', default_value='')

    base_frame_id = PythonExpression(["'", namespace, "/base_footprint' if '", namespace, "' else 'base_footprint'"])
    odom_frame_id = PythonExpression(["'", namespace, "/odom' if '", namespace, "' else 'odom'"])
    controller_manager_name = PythonExpression(["'/", namespace, "/controller_manager' if '", namespace, "' else '/controller_manager'"])
    
    # Path to the controller config file
    pkg_path_description =  get_package_share_directory("rmitbot_description")
    pkg_path_controller =   get_package_share_directory("rmitbot_controller")

    urdf_path =      os.path.join(pkg_path_description, 'urdf', 'rmitbot.urdf.xacro')
    ctrl_config =    os.path.join(pkg_path_controller, 'config', 'rmitbot_controller.yaml')
    
    robot_description = ParameterValue(Command(['xacro ', urdf_path]), value_type=str)
    
    # controller manager node
    controller_manager = Node(
        package=    "controller_manager",
        executable= "ros2_control_node",
        parameters=[
            ctrl_config, 
            {
                "robot_description": robot_description,
                "use_sim_time": False,
                "diff_drive_controller.base_frame_id": base_frame_id,
                "diff_drive_controller.odom_frame_id": odom_frame_id,
            }
        ],
    )

    # joint_state_broadcaster (jsb): position, velocity from the robot hardware
    jsb_spawner = Node(
        package=    'controller_manager',
        executable= 'spawner',
        arguments=['joint_state_broadcaster', '-c', controller_manager_name],
    )
    
    # controller: IK from Cartesian speed to motor speed command
    controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_drive_controller",
            "-c", controller_manager_name,
            "--param-file",
            ctrl_config,
        ],
    )
    
    # controller must be spawned after the jsb
    controller_spawner_delayed = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=jsb_spawner,
            on_exit=[controller_spawner],
            )
        )
    
    imu_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            'imu_sensor_broadcaster',
            '-c', controller_manager_name,
            '--param-file',
            ctrl_config,
        ],
    )
    
    imu_broadcaster_delayed = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=controller_spawner,
            on_exit=[imu_broadcaster],
            )
        )

    return LaunchDescription(
        [
            namespace_arg,
            controller_manager, 
            jsb_spawner,
            controller_spawner_delayed,
            imu_broadcaster_delayed, 
        ]
    )
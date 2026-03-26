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

# ros2 launch rmitbot_controller controller.launch.py

def generate_launch_description():
    
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
        parameters=[{   "robot_description": robot_description,
                        "use_sim_time": False},
                        ctrl_config, 
        ],
    )

    # joint_state_broadcaster (jsb): position, velocity from the robot hardware
    jsb_spawner = Node(
        package=    'controller_manager',
        executable= 'spawner',
        arguments=['joint_state_broadcaster'],
    )
    
    # controller: IK from Cartesian speed to motor speed command
    controller_spawner = Node(
        package=    "controller_manager",
        executable= "spawner",
        arguments=[
            'mecanum_drive_controller','--param-file',ctrl_config,
            '--controller-ros-args','-r /mecanum_drive_controller/tf_odometry:=/tf',
            '--controller-ros-args','-r /mecanum_drive_controller/reference:=/rmitbot_controller/cmd_vel',
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
            controller_manager, 
            jsb_spawner,
            controller_spawner_delayed,
            imu_broadcaster_delayed, 
        ]
    )
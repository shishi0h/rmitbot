import os
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.actions import RegisterEventHandler
from launch.conditions import UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

# ros2 launch rmitbot_controller controller.launch.py

def generate_launch_description():
    
    use_sim = LaunchConfiguration('use_sim')
    
    declare_use_sim = DeclareLaunchArgument(
        'use_sim',
        default_value='true',
        description='Use simulation (Gazebo)'
    )
    
    controllers = [declare_use_sim]

    for i in range(2):

        ns = f"robot_{i}"


        # Path to the controller config file
        pkg_path_controller = get_package_share_directory("rmitbot_controller")
        config_controller = os.path.join(pkg_path_controller, 'config', 'rmitbot_controller.yaml')

        # Path to the package
        pkg_path_description = get_package_share_directory("rmitbot_description")
        urdf_path = os.path.join(pkg_path_description, 'urdf', 'rmitbot.urdf.xacro')
        robot_description = ParameterValue(
        Command([
            "xacro ",
            urdf_path,
            f" prefix:={ns}_"
        ]),
        value_type=str
        )
        
    
        # Publish the robot static TF from the urdf
        robot_state_publisher = Node(
            package=    'robot_state_publisher',
            executable= 'robot_state_publisher',
            namespace=  ns,
            parameters=[{"robot_description": robot_description}],
            condition=  UnlessCondition(use_sim)
            )
        
        # joint_state_broadcaster (jsb): dynamic TF of the motor joints 
        joint_state_broadcaster_spawner = Node(
            package=    'controller_manager',
            executable= 'spawner',
            namespace= ns,
            arguments=[ 'joint_state_broadcaster', '-c', f'/{ns}/controller_manager'],
        )
        
        # controller: IK from Cartesian speed to motor speed command
        # controller_spawner = Node(
        #     package="controller_manager",
        #     executable="spawner",
        #     namespace= ns,
        #     arguments=[
        #         'mecanum_drive_controller','--param-file', config_controller,
        #         '--controller-ros-args', '-r mecanum_drive_controller/tf_odometry:=tf',
        #         '--controller-ros-args', '-r mecanum_drive_controller/reference:=cmd_vel',
        #         '--controller-ros-args', '-r mecanum_drive_controller/odometry:=odom',
        #         '--controller-ros-args', '-r mecanum_drive_controller/controller_state:=controller_state',
        #     ],
        # )

        diff_drive_controller = Node(
            package="controller_manager",
            executable="spawner",
            namespace=ns,
            arguments=[
            "diff_drive_controller",
            "-c",
            f"/{ns}/controller_manager"
            ],
        )
        
        # controller must be spawned after the jsb
        controller_spawner_after_jsb = RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[diff_drive_controller],
                )
        )

        controllers.append(joint_state_broadcaster_spawner)
        controllers.append(controller_spawner_after_jsb)


    return LaunchDescription(controllers)
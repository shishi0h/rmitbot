import os
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue
from launch import LaunchDescription
from launch.actions import RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command

from launch_ros.actions import Node

def generate_launch_description():
    controllers = []

    for i in range(2):
        ns = f"robot_{i+1}"

        # Path to the controller config file for this specific robot
        pkg_path_controller = get_package_share_directory("rmitbot_controller")
        config_controller = os.path.join(pkg_path_controller, 'config', f'{ns}_controller.yaml')

        # Path to the package
        pkg_path_description = get_package_share_directory("rmitbot_description")
        urdf_path = os.path.join(pkg_path_description, 'urdf', 'rmitbot.urdf.xacro')
        
        # Compile xacro with prefix and mock hardware enabled
        robot_description = ParameterValue(
            Command([
                "xacro ",
                urdf_path,
                f" prefix:={ns}_ use_mock_hardware:=true"
            ]),
            value_type=str
        )
        
        # Publish the robot static TF from the urdf
        robot_state_publisher = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            namespace=ns,
            parameters=[{"robot_description": robot_description, "use_sim_time": False}]
        )
        
        # Run the controller manager using the mock hardware
        ros2_control_node = Node(
            package="controller_manager",
            executable="ros2_control_node",
            namespace=ns,
            parameters=[{"robot_description": robot_description}, config_controller],
            output="screen",
            remappings=[
                ("~/robot_description", f"/{ns}/robot_description"),
            ]
        )

        # joint_state_broadcaster
        joint_state_broadcaster_spawner = Node(
            package='controller_manager',
            executable='spawner',
            namespace=ns,
            arguments=['joint_state_broadcaster', '-c', f'/{ns}/controller_manager'],
        )

        # diff_drive_controller
        diff_drive_controller_spawner = Node(
            package='controller_manager',
            executable='spawner',
            namespace=ns,
            arguments=['diff_drive_controller', '-c', f'/{ns}/controller_manager'],
        )
        
        # Spawners must wait for the controller manager to be ready, but without 
        # a dedicated event for manager ready, we just launch them. 
        # However, it's safer to chain them:
        controller_spawner_after_jsb = RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[diff_drive_controller_spawner],
            )
        )

        # Broadcast the initial spawn pose to the TF tree
        static_tf_publisher = Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name=f"static_tf_pub_{ns}",
            output="screen",
            arguments=[
                "--x", str(i * 1.5), # offset them physically
                "--y", "0.0",
                "--z", "0.0", 
                "--yaw", "0.0",
                "--pitch", "0.0",
                "--roll", "0.0",
                "--frame-id", "map",
                "--child-frame-id", f"{ns}/odom"
            ]
        )

        controllers.append(robot_state_publisher)
        controllers.append(static_tf_publisher)
        controllers.append(ros2_control_node)

        # To prevent race conditions and spawner timeouts when launching multiple 
        # controller managers concurrently, we delay all spawners to give controller_managers
        # time to parse the URDF and initialize the mock hardware.
        delayed_controllers = TimerAction(
            period=3.0 + (3.0 * i),
            actions=[
                joint_state_broadcaster_spawner,
                controller_spawner_after_jsb
            ]
        )
        controllers.append(delayed_controllers)

    return LaunchDescription(controllers)

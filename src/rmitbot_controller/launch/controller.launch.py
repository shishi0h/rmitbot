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

def launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace').perform(context)
    robot_type = LaunchConfiguration('robot_type').perform(context)
    
    base_frame_id = f"{namespace}/base_footprint" if namespace else "base_footprint"
    odom_frame_id = f"{namespace}/odom" if namespace else "odom"
    imu_frame_id = f"{namespace}/imu_link" if namespace else "imu_link"
    controller_manager_name = f"/{namespace}/controller_manager" if namespace else "/controller_manager"
    
    controller_serial_port = LaunchConfiguration('controller_serial_port').perform(context)
    
    pkg_path_description = get_package_share_directory("rmitbot_description")
    pkg_path_controller = get_package_share_directory("rmitbot_controller")
    
    if robot_type == 'smallbot':
        urdf_file = 'smallbot.urdf.xacro'
        wheel_separation = '0.36'
        wheel_radius = '0.13'
    elif robot_type == 'bigbot':
        urdf_file = 'bigbot.urdf.xacro'
        wheel_separation = '0.61'
        wheel_radius = '0.25'
    else:
        urdf_file = 'rmitbot.urdf.xacro'
        wheel_separation = '0.40'
        wheel_radius = '0.05'
        
    urdf_path = os.path.join(pkg_path_description, 'urdf', urdf_file)
    ctrl_config = os.path.join(pkg_path_controller, 'config', 'rmitbot_controller.yaml')
    
    robot_description = ParameterValue(Command(['xacro ', urdf_path, ' controller_serial_port:=', controller_serial_port]), value_type=str)
    
    import tempfile
    with open(ctrl_config, 'r') as f:
        config_text = f.read()
    
    config_text = config_text.replace('base_frame_id: base_footprint', f'base_frame_id: {base_frame_id}')
    config_text = config_text.replace('odom_frame_id: odom', f'odom_frame_id: {odom_frame_id}')
    config_text = config_text.replace('frame_id:  "imu_link"', f'frame_id: "{imu_frame_id}"')
    
    # Inject dynamic physical dimensions for diff drive odometry
    config_text = config_text.replace('wheel_separation: 0.40', f'wheel_separation: {wheel_separation}')
    config_text = config_text.replace('wheel_radius: 0.05', f'wheel_radius: {wheel_radius}')
    
    temp_yaml = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
    temp_yaml.write(config_text)
    temp_yaml.close()
    
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            temp_yaml.name, 
            {
                "robot_description": robot_description,
                "use_sim_time": False,
            }
        ],
    )

    jsb_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '-c', controller_manager_name],
    )
    
    controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_drive_controller",
            "-c", controller_manager_name,
            "--param-file", temp_yaml.name,
        ],
    )
    
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
            "--param-file", temp_yaml.name,
        ],
    )
    
    imu_broadcaster_delayed = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=controller_spawner,
            on_exit=[imu_broadcaster],
        )
    )

    return [
        controller_manager, 
        jsb_spawner,
        controller_spawner_delayed,
        imu_broadcaster_delayed, 
    ]

def generate_launch_description():
    from launch.actions import OpaqueFunction
    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value=''),
        DeclareLaunchArgument('robot_type', default_value='smallbot', description='Type of robot: smallbot or bigbot'),
        DeclareLaunchArgument('controller_serial_port', default_value='/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0'),
        OpaqueFunction(function=launch_setup)
    ])
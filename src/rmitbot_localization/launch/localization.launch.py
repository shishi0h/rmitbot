from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import UnlessCondition, IfCondition
import os

def launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace').perform(context)
    
    prefix = f"{namespace}/" if namespace else ""
    base_frame_id = f"{prefix}base_footprint"
    odom_frame_id = f"{prefix}odom"
    map_frame_id = f"{prefix}map"

    ekf_config_path = os.path.join(get_package_share_directory("rmitbot_localization"), "config", "ekf.yaml")
    import tempfile
    with open(ekf_config_path, 'r') as f:
        config_text = f.read()

    config_text = config_text.replace('map_frame: map', f'map_frame: {map_frame_id}')
    config_text = config_text.replace('odom_frame: odom', f'odom_frame: {odom_frame_id}')
    config_text = config_text.replace('base_link_frame: base_footprint', f'base_link_frame: {base_frame_id}')
    config_text = config_text.replace('world_frame: odom', f'world_frame: {odom_frame_id}')

    temp_yaml = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
    temp_yaml.write(config_text)
    temp_yaml.close()

    robot_localization = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        output="screen",
        parameters=[temp_yaml.name],
    )

    return [robot_localization]

def generate_launch_description():
    from launch.actions import OpaqueFunction
    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value=''),
        OpaqueFunction(function=launch_setup)
    ])
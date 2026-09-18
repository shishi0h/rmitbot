import os
import tempfile
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument, EmitEvent, RegisterEventHandler, OpaqueFunction
from launch_ros.events.lifecycle import ChangeState
from launch_ros.event_handlers import OnStateTransition
from launch.event_handlers import OnProcessStart
from lifecycle_msgs.msg import Transition
import launch

def launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace').perform(context)
    use_sim_time = LaunchConfiguration('use_sim_time').perform(context)
    
    # Base paths
    slam_params_path = os.path.join(get_package_share_directory("rmitbot_mapping"), "config", "slam.yaml")
    
    # Prepare the frame prefixes
    prefix = namespace + '/' if namespace else ''
    base_frame = prefix + 'base_footprint'
    odom_frame = prefix + 'odom'
    map_frame = prefix + 'map'
    
    # Read the YAML
    with open(slam_params_path, 'r') as f:
        config_text = f.read()
        
    # Replace the frames dynamically
    config_text = config_text.replace('base_frame: base_footprint', f'base_frame: {base_frame}')
    config_text = config_text.replace('odom_frame: odom', f'odom_frame: {odom_frame}')
    config_text = config_text.replace('map_frame: map', f'map_frame: {map_frame}')
    
    # Write to temp file
    temp_yaml = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
    temp_yaml.write(config_text)
    temp_yaml.close()

    remappings = []
    if namespace:
        remappings = [
            ('/map', f'/{namespace}/map'),
            ('/map_metadata', f'/{namespace}/map_metadata')
        ]

    # Launch the SLAM Toolbox node directly to avoid hardcoded namespace='' in its default launch file
    slam_toolbox_node = Node(
        parameters=[
          temp_yaml.name,
          {'use_sim_time': use_sim_time.lower() == 'true'}
        ],
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        remappings=remappings
    )

    return [slam_toolbox_node]


def generate_launch_description():
    namespace_arg = DeclareLaunchArgument('namespace', default_value='')
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='false')

    return LaunchDescription([
        namespace_arg,
        use_sim_time_arg,
        OpaqueFunction(function=launch_setup)
    ])
import os
import tempfile
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.actions import OpaqueFunction

def launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace').perform(context)
    
    # Base paths
    nav2_params_path = os.path.join(get_package_share_directory('rmitbot_navigation'), 'config', 'nav2_params.yaml')
    
    # Prepare the frame prefixes
    prefix = namespace + '/' if namespace else ''
    base_frame = prefix + 'base_footprint'
    odom_frame = prefix + 'odom'
    
    # Read the YAML
    with open(nav2_params_path, 'r') as f:
        config_text = f.read()
        
    # Replace the frames dynamically
    config_text = config_text.replace('robot_base_frame: base_footprint', f'robot_base_frame: {base_frame}')
    config_text = config_text.replace('robot_base_frame: "base_footprint"', f'robot_base_frame: "{base_frame}"')
    
    config_text = config_text.replace('global_frame: odom', f'global_frame: {odom_frame}')
    config_text = config_text.replace('local_frame: odom', f'local_frame: {odom_frame}')
    config_text = config_text.replace('fixed_frame: "odom"', f'fixed_frame: "{odom_frame}"')
    config_text = config_text.replace('odom_frame_id: "odom"', f'odom_frame_id: "{odom_frame}"')
    config_text = config_text.replace('base_frame_id: "base_footprint"', f'base_frame_id: "{base_frame}"')
    config_text = config_text.replace('base_frame: "base_footprint"', f'base_frame: "{base_frame}"')

    # Write to temp file
    temp_yaml = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
    temp_yaml.write(config_text)
    temp_yaml.close()

    # --- DYNAMICALLY PATCH navigation_launch.py ---
    # nav2_bringup hardcodes remappings to local tf. We MUST remove this to use global tf.
    nav2_bringup_launch_path = os.path.join(get_package_share_directory('nav2_bringup'), 'launch', 'navigation_launch.py')
    with open(nav2_bringup_launch_path, 'r') as f:
        nav2_launch_code = f.read()
    
    # Replace the local tf remapping with global tf remapping
    nav2_launch_code = nav2_launch_code.replace("('/tf', 'tf')", "('/tf', '/tf')")
    nav2_launch_code = nav2_launch_code.replace("('/tf_static', 'tf_static')", "('/tf_static', '/tf_static')")
    
    temp_launch = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_navigation_launch.py')
    temp_launch.write(nav2_launch_code)
    temp_launch.close()

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(temp_launch.name),
        launch_arguments={
            'use_sim_time': 'false',
            'use_collision_monitor': 'false',
            'namespace': namespace,
            'params_file': temp_yaml.name,
        }.items(), 
    )

    return [nav2_launch]

def generate_launch_description():
    namespace_arg = DeclareLaunchArgument('namespace', default_value='')

    return LaunchDescription([
        namespace_arg, 
        OpaqueFunction(function=launch_setup)
    ])  
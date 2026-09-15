import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from nav2_common.launch import RewrittenYaml

def generate_launch_description():
    
    namespace = LaunchConfiguration('namespace')
    use_sim_time = LaunchConfiguration('use_sim_time')
    
    namespace_arg = DeclareLaunchArgument('namespace', default_value='')
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='false')
    
    nav_pkg_path = get_package_share_directory('rmitbot_navigation')
    params_file = os.path.join(nav_pkg_path, 'config', 'nav2_params.yaml')
    
    param_substitutions = {
        'robot_base_frame': [namespace, '/base_footprint'],
        'global_frame': 'map', # Or [namespace, '/odom'] depending on map merge strategy
    }

    configured_params = RewrittenYaml(
        source_file=params_file,
        root_key=namespace,
        param_rewrites=param_substitutions,
        convert_types=True)

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('nav2_bringup'),
                'launch',
                'navigation_launch.py'
            ])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'use_collision_monitor': 'false',
            'params_file': configured_params,
            'namespace': namespace,
        }.items(), 
    )

    return LaunchDescription([
        namespace_arg,
        use_sim_time_arg,
        nav2_launch
    ])
import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from nav2_common.launch import RewrittenYaml

# ros2 launch rmitbot_mapping slam.launch.py use_sim_time:=true
# ros2 launch rmitbot_mapping slam.launch.py use_sim_time:=false

def generate_launch_description():
    
    prefix = LaunchConfiguration('prefix')
    prefix_arg = DeclareLaunchArgument('prefix', default_value='')

    slam_config_file = os.path.join(get_package_share_directory("rmitbot_mapping"), "config", "slam.yaml")

    param_substitutions = {
        'odom_frame': [prefix, 'odom'],
        'base_frame': [prefix, 'base_footprint'],
    }

    configured_params = RewrittenYaml(
        source_file=slam_config_file,
        root_key='',
        param_rewrites=param_substitutions,
        convert_types=True)

    slam_launch = IncludeLaunchDescription(
        os.path.join(get_package_share_directory("slam_toolbox"),"launch","online_async_launch.py"),
        launch_arguments={
            'params_file': configured_params,
            'use_sim_time': "False",
            }.items()
    )

    return LaunchDescription([
        prefix_arg,
        slam_launch,
    ])
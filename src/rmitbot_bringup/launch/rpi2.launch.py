import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    namespace = 'robot_2'
    prefix = namespace + '_'

    # We just include the main rpi.launch.py but pass the namespace down
    rpi_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('rmitbot_bringup'), 'launch', 'rpi.launch.py')]),
        launch_arguments={
            'namespace': namespace,
            'prefix': prefix
        }.items(),
    )

    return LaunchDescription([
        rpi_launch
    ])

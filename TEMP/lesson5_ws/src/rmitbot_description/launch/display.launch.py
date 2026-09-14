import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, LaunchConfiguration

# Launch the file
# ros2 launch rmitbot_description display.launch.py

def generate_launch_description():
    # Path to the package
    pkg_path_description = get_package_share_directory("rmitbot_description")
    # Path to the rviz config file
    rviz_path = os.path.join(pkg_path_description, 'rviz', 'display.rviz')
    
    # RViz instance for Robot 0
    rviz_robot_0 = Node(
        package=    'rviz2',
        executable= 'rviz2',
        name=       'rviz2_robot_0',
        namespace=  '/robot_0',
        output=     'screen',
        arguments=[ '-d', rviz_path, '-t', 'Robot 0 Navigation'],
        parameters=[{'use_sim_time': True}],
    )
    
    # RViz instance for Robot 1
    rviz_robot_1 = Node(
        package=    'rviz2',
        executable= 'rviz2',
        name=       'rviz2_robot_1',
        namespace=  '/robot_1',
        output=     'screen',
        arguments=[ '-d', rviz_path, '-t', 'Robot 1 Navigation'],
        parameters=[{'use_sim_time': True}],
    )
    
    return LaunchDescription([
        rviz_robot_0, 
        rviz_robot_1
    ])
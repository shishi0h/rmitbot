import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

# ros2 launch rmitbot_description rviz.launch.py

def generate_launch_description():
    # Path to the package
    pkg_path_description = get_package_share_directory("rmitbot_description")
    
    # Path to the rviz config file
    rviz_path = os.path.join(pkg_path_description, 'rviz', 'display.rviz')

    # RViz instance for Robot 1
    rviz_robot1 = Node(
        package=    'rviz2',
        executable= 'rviz2',
        name=       'rviz2_robot1',
        namespace=  '/robot1',
        output=     'screen',
        arguments=[ '-d', rviz_path, '-t', 'Robot 1 Navigation'],
        parameters=[{'use_sim_time': False}],
    )

    # RViz instance for Robot 2
    rviz_robot2 = Node(
        package=    'rviz2',
        executable= 'rviz2',
        name=       'rviz2_robot2',
        namespace=  '/robot2',
        output=     'screen',
        arguments=[ '-d', rviz_path, '-t', 'Robot 2 Navigation'],
        parameters=[{'use_sim_time': False}],
    )

    return LaunchDescription([
        rviz_robot1,
        rviz_robot2
    ])
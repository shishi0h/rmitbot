
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, GroupAction, LogInfo
from launch_ros.actions import Node, PushRosNamespace, SetRemap

def generate_launch_description():
    node = Node(
        package='tf2_ros',
        executable='tf2_echo',
        name='test_node',
        arguments=['map', 'odom'],
        remappings=[('/tf', 'tf')] # Simulate nav2 inner remapping
    )
    return LaunchDescription([
        GroupAction([
            PushRosNamespace('robot_1'),
            SetRemap(src='tf', dst='/tf'),
            node
        ])
    ])

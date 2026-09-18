
from launch import LaunchDescription
from launch.actions import GroupAction
from launch_ros.actions import Node, PushRosNamespace, SetRemap

def generate_launch_description():
    node = Node(
        package='demo_nodes_cpp',
        executable='talker',
        name='my_talker',
        remappings=[('/chatter', 'chatter')]
    )
    return LaunchDescription([
        GroupAction([
            PushRosNamespace('robot_1'),
            SetRemap(src='chatter', dst='/global_chatter'),
            node
        ])
    ])

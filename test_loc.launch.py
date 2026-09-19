
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, GroupAction
from launch_ros.actions import PushRosNamespace
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    localization = IncludeLaunchDescription(
        os.path.join(get_package_share_directory('rmitbot_localization'), 'launch', 'localization.launch.py'),
        launch_arguments={'namespace': 'robot_1'}.items()
    )
    return LaunchDescription([
        GroupAction([PushRosNamespace('robot_1'), localization])
    ])

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import PushRosNamespace

def generate_launch_description():
    
    namespace = LaunchConfiguration('namespace')
    namespace_arg = DeclareLaunchArgument('namespace', default_value='')

    # Launch robot state publisher (rsp)
    rsp = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_description"),
            "launch", "rsp.launch.py"
        ),
        launch_arguments={'namespace': namespace}.items()
    )
    
    # Launch the controller manager spawner
    controller = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_controller"),
            "launch", "controller.launch.py"
        ),
        launch_arguments={'namespace': namespace}.items()
    )
    
    localization = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_localization"),
            "launch",
            "localization.launch.py"
        ),
        launch_arguments={'namespace': namespace}.items()
    )
    
    # Launch the rplidar hardware
    rplidar = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_mapping"),
            "launch", "rplidar.launch.py"
        ),
        launch_arguments={"use_sim_time": "False"}.items()
    )
    
    # Launch the slamtoolbox 
    slamtoolbox = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_mapping"),
            "launch", "slam.launch.py"
        ),
        launch_arguments={"use_sim_time": "False", 'namespace': namespace}.items()
    )

    # Launch cliff sensors
    cliff_sensor = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_cliff_sensor"),
            "launch", "cliff.launch.py"
        ),
        launch_arguments={'namespace': namespace, 'bypass_cliff_sensor': 'false'}.items()
    )
    
    # Launch vision (Camera IS included in small bot)
    vision = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_vision"),
            "launch", "vision.launch.py"
        ),
    )
    
    # Group all nodes under the namespace
    namespaced_nodes = GroupAction([
        PushRosNamespace(namespace),
        rsp, 
        controller,
        localization,
        rplidar, 
        cliff_sensor,
        vision,
        slamtoolbox, 
    ])
    
    return LaunchDescription([
        namespace_arg,
        namespaced_nodes
    ])

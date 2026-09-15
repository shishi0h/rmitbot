import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, RegisterEventHandler, DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import PushRosNamespace
from ament_index_python.packages import get_package_share_directory
from launch.event_handlers import OnProcessExit

# Launch the file
# ros2 launch rmitbot_bringup rpi.launch.py namespace:=robot1 prefix:=robot1/ has_cliff_sensor:=true

def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    prefix = LaunchConfiguration('prefix')
    has_cliff_sensor = LaunchConfiguration('has_cliff_sensor')
    
    namespace_arg = DeclareLaunchArgument('namespace', default_value='')
    prefix_arg = DeclareLaunchArgument('prefix', default_value='')
    has_cliff_sensor_arg = DeclareLaunchArgument('has_cliff_sensor', default_value='true')
    
    # Launch rviz
    display = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_description"),
            "launch", "display.launch.py"
        ),
    )
    
    # Launch the controller manager spawner
    controller = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_controller"),
            "launch", "controller.launch.py"
        ),
        launch_arguments={
            'prefix': prefix,
            'has_cliff_sensor': has_cliff_sensor
        }.items()
    )
    
    # Launch the teleop keyboard node
    teleopkeyboard = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_controller"),
            "launch", "teleopkeyboard.launch.py"
        ),
        launch_arguments={
            "use_sim_time": "False"
        }.items()
    )
    
    localization = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_localization"),
            "launch",
            "localization.launch.py"
        ),
        launch_arguments={
            'prefix': prefix
        }.items()
    )
    
    # Launch the rplidar hardware
    rplidar = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_mapping"),
            "launch", "rplidar.launch.py"
        ),
        launch_arguments={
            'prefix': prefix,
            "use_sim_time": "False"
        }.items()
    )
    
    # Launch the slamtoolbox 
    slamtoolbox = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_mapping"),
            "launch", "slam.launch.py"
        ),
        launch_arguments={
            'prefix': prefix,
            "use_sim_time": "False"
        }.items()
    )
    
    # Launch the twistmux instead of keyboard node only
    twistmux = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_navigation"),
            "launch",
            "twistmux.launch.py"
        ),
    )
    
    navigation = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_navigation"),
            "launch",
            "nav.launch.py"
        ),
    )
    
    # Launch the navigation 10s after slamtoolbox, to make sure that a map is available
    navigation_delayed = TimerAction(
        period = 5., 
        actions=[navigation]
    )

    # Launch robot state publisher (rsp)
    rsp = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_description"),
            "launch", "rsp.launch.py"
        ),
        launch_arguments={
            'prefix': prefix,
            'has_cliff_sensor': has_cliff_sensor
        }.items()
    )
    
    # Launch cliff sensors
    cliff_sensor = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_cliff_sensor"),
            "launch", "cliff.launch.py"
        ),
        launch_arguments={'namespace': namespace}.items()
    )
    
    # Launch vision
    vision = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("rmitbot_vision"),
            "launch", "vision.launch.py"
        ),
    )
    
    # RPI launches rsp, controller, sensors inside the namespace
    group = GroupAction([
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
        prefix_arg,
        has_cliff_sensor_arg,
        group
    ])
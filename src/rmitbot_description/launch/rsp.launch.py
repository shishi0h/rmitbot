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
    pkg_path = get_package_share_directory("rmitbot_description")
    
    # Path to the urdf file
    urdf_path = os.path.join(pkg_path, 'urdf', 'rmitbot.urdf.xacro')
    
    prefix = LaunchConfiguration('prefix')
    has_cliff_sensor = LaunchConfiguration('has_cliff_sensor')
    
    prefix_arg = DeclareLaunchArgument('prefix', default_value='')
    has_cliff_sensor_arg = DeclareLaunchArgument('has_cliff_sensor', default_value='true')
    
    # Compile the xacro file to urdf
    robot_description = ParameterValue(Command(['xacro ', urdf_path, ' prefix:=', prefix, ' has_cliff_sensor:=', has_cliff_sensor]), value_type=str)
    
    # Publish the robot static TF from the urdf
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"use_sim_time": False, 
                     "robot_description": robot_description}],
        )
    
    # Publish the joint state TF - Not needed with a controller
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
    )
    
    return LaunchDescription([
        prefix_arg,
        has_cliff_sensor_arg,
        robot_state_publisher, 
        # joint_state_publisher_gui,
    ])
import os
from pathlib import Path
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node, SetParameter
from launch_ros.parameter_descriptions import ParameterValue

# Launch the file
# ros2 launch rmitbot_description gazebo.launch.py

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    set_use_sim_time_cmd = SetParameter(
        name='use_sim_time',
        value=use_sim_time
    )

    # Path to the package
    pkg_path = get_package_share_directory("rmitbot_description")
    
    # Path to the urdf file
    urdf_path = os.path.join(pkg_path, 
                             'urdf', 
                             'rmitbot.urdf.xacro')
    
    # Resource path for gazebo. Required while using stl (robot CAD), and sdf (world)
    gz_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=[str(Path(pkg_path).parent.resolve())]
    )

    # Compile the xacro to urdf
    robot_description = ParameterValue(Command(['xacro ', urdf_path, ' use_sim:=true']), value_type=str)
    
    # Publish the robot static TF from the urdf
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description,
                     "use_sim_time": True}]
    )
    
    # Launch Gazebo 
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [os.path.join(get_package_share_directory("ros_gz_sim"), "launch"), "/gz_sim.launch.py"]),
        launch_arguments=[("gz_args", [" -v 4", " -r", " empty.sdf", " --render-engine", " ogre"])]
    )
    
    # Spawn the robot in Gazebo
    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=["-topic", "robot_description", "-name", "rmitbot", "-world", "empty"],
    )

    # Bridge between ROS2 and Gazebo
    gz_ros2_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/sensors/cliff/cliff_fl@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/sensors/cliff/cliff_fr@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan"
        ], 
    )

    # Launch RViz2
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_path, 'rviz', 'display.rviz')],
    )

    return LaunchDescription([
        declare_use_sim_time_cmd,
        set_use_sim_time_cmd,
        gz_resource_path,
        robot_state_publisher,
        gazebo,
        gz_spawn_entity,
        gz_ros2_bridge,
        rviz,
    ])
import os
from pathlib import Path
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

# Launch the file
# ros2 launch rmitbot_description gazebo.launch.py

def generate_launch_description():
    # Path to the package
    pkg_path_description = get_package_share_directory("rmitbot_description")
    # Path to the world file
    world_path = os.path.join(pkg_path_description, 'world', 'mi_craft_field.sdf')
    
    # Resource path for gazebo. Required while using stl (robot CAD), and sdf (world)
    gz_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value=[str(Path(pkg_path_description).parent.resolve())]
    )

    # Launch Gazebo 
    gz_sim = IncludeLaunchDescription(PythonLaunchDescriptionSource(
        [os.path.join(get_package_share_directory("ros_gz_sim"), "launch"), "/gz_sim.launch.py"]),
        launch_arguments={"gz_args": f"-r -v 4 {world_path}"}.items()
    )
    
    # # Spawn the robot in Gazebo
    # robot1 = Node(
    #     package=    "ros_gz_sim",
    #     executable= "create",
    #     output=     "screen",
    #     arguments=  ["-topic", "robot_description","-name", "rmitbot1"],
    # )

    # # robot2 = Node(
    # #     package=    "ros_gz_sim",
    # #     executable= "create",
    # #     output=     "screen",
    # #     arguments=  ["-topic", "robot_description","-name", "rmitbot2",
    # #     ],
    # # )


    robots = []

    robots_config = [
        {"gazebo_x": 0.0, "gazebo_y": 0.0, "tf_x": 0.0, "tf_y": 0.0},
        {"gazebo_x": -1.0, "gazebo_y": 0.0, "tf_x": 0.0, "tf_y": -1.0}
    ]

    for i, config in enumerate(robots_config):

        ns = f"robot_{i}"
        
        z = 0.51

        # Robot State Publisher
        robot_state_publisher = Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            namespace=ns,
            output="screen",
            parameters=[
            {
                "robot_description": ParameterValue(
                    Command([
                        "xacro ",
                        os.path.join(
                            pkg_path_description,
                            "urdf",
                            "rmitbot.urdf.xacro"
                        ),
                        f" prefix:={ns}/"
                    ]),
                    value_type=str
                ),
                "use_sim_time": True
            }
                    ]           
        )

        # Spawn robot in Gazebo
        spawn_robot = Node(
            package="ros_gz_sim",
            executable="create",
            namespace=ns,
            output="screen",
            arguments=[
                "-topic", f"/{ns}/robot_description",
                "-name", ns,
                "-x", str(config["gazebo_x"]),
                "-y", str(config["gazebo_y"]),
                "-z", str(z),
                "-Y", "4.71"
            ]
        )

        # Broadcast the initial spawn pose to the TF tree
        static_tf_publisher = Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name=f"static_tf_pub_{ns}",
            output="screen",
            arguments=[
                "--x", str(config["tf_x"]),
                "--y", str(config["tf_y"]),
                "--z", "0.0", 
                "--yaw", "0.0", # Matches your Gazebo spawn yaw
                "--pitch", "0.0",
                "--roll", "0.0",
                "--frame-id", "map",
                "--child-frame-id", f"{ns}/map"
            ]
        )


        robots.append(robot_state_publisher)
        robots.append(spawn_robot)
        robots.append(static_tf_publisher)
    




    # Bridge between ROS2 and Gazebo
    gz_ros2_bridge = Node(
        package=    "ros_gz_bridge",
        executable= "parameter_bridge",
        arguments=[ "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock", 
                    "/robot_0_scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
    "/robot_1_scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",

    "/robot_0_imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
    "/robot_1_imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
    ],
        remappings=[
            ('/robot_0_scan', '/robot_0/scan'),
            ('/robot_1_scan', '/robot_1/scan'),
            ('/robot_0_imu', '/robot_0/imu'),
            ('/robot_1_imu', '/robot_1/imu'),
        ]
    )

    return LaunchDescription([
        gz_resource_path,
        gz_sim,
        gz_ros2_bridge,
        *robots
    ])
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node

# ros2 launch rmitbot_controller twistmux.launch.py

def generate_launch_description():

    twistmux_params = os.path.join(
        get_package_share_directory("rmitbot_navigation"),
        "config",
        "twistmux.yaml"
    )

    nodes = []

    for i in range(2):

        ns = f"robot_{i}"

        # ----------------------------
        # Teleop Keyboard
        # ----------------------------
        teleop_keyboard = Node(
            package='teleop_twist_keyboard',
            executable='teleop_twist_keyboard',
            namespace=ns,
            name=f'teleop_robot{i}',
            output='screen',
            prefix=f'xterm -T "Robot {i} Teleop" -e',
            parameters=[
                {"use_sim_time": True},
            ],
            remappings=[
                ('cmd_vel', 'cmd_vel_keyboard_unstamped'),
            ],
        )

        keyboard_stamper = Node(
            package='twist_stamper',
            executable='twist_stamper',
            namespace=ns,
            name='keyboard_stamper',
            parameters=[
                {"use_sim_time": True},
                {"frame_id": f"{ns}/base_footprint"},
            ],
            remappings=[
                ('cmd_vel_in', 'cmd_vel_keyboard_unstamped'),
                ('cmd_vel_out', 'cmd_vel_keyboard'),
            ],
        )

        # ----------------------------
        # Twist Stamper
        # ----------------------------
        twist_stamper = Node(
            package='twist_stamper',
            executable='twist_stamper',
            namespace=ns,
            name='twist_stamper',
            parameters=[
                {"use_sim_time": True},
                {"frame_id": f"{ns}/base_footprint"},
            ],
            remappings=[
                ('cmd_vel_in', 'cmd_vel_navigation_unstamped'),
                ('cmd_vel_out', 'cmd_vel_navigation'),
            ],
        )

        # ----------------------------
        # Twist Mux
        # ----------------------------
        twist_mux = Node(
            package='twist_mux',
            executable='twist_mux',
            namespace=ns,
            name='twist_mux_node',
            output='screen',
            parameters=[
                twistmux_params,
                {"use_sim_time": True},
            ],
            remappings=[
                (
                    'cmd_vel_out',
                    f'/{ns}/diff_drive_controller/cmd_vel'
                ),
                (
                    'cmd_vel',
                    f'/{ns}/diff_drive_controller/cmd_vel'
                ),
            ],
        )

        nodes.append(teleop_keyboard)
        nodes.append(keyboard_stamper)
        nodes.append(twist_stamper)
        nodes.append(twist_mux)

    return LaunchDescription(nodes)
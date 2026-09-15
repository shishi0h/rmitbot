import os 
from ament_index_python.packages import get_package_share_directory 
from launch import LaunchDescription 
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node 
from launch.substitutions import LaunchConfiguration 
from launch.conditions import IfCondition

# ros2 launch rmitbot_controller twistmux.launch.py 

def generate_launch_description(): 
    prefix = LaunchConfiguration('prefix')
    use_joy = LaunchConfiguration('use_joy')
    use_keyboard = LaunchConfiguration('use_keyboard')
    
    prefix_arg = DeclareLaunchArgument('prefix', default_value='')
    use_joy_arg = DeclareLaunchArgument('use_joy', default_value='true')
    use_keyboard_arg = DeclareLaunchArgument('use_keyboard', default_value='true')

    #Joy
    joy_node = Node(
        condition=IfCondition(use_joy),
        package='joy',
        executable='joy_node',
        name='joy_node',
        output='screen',
        prefix='xterm -e', 
        parameters=[
            {"use_sim_time": False},
        ],
    )
    
    
    teleop_joy = Node(
        condition=IfCondition(use_joy),
        package='teleop_twist_joy',
        executable='teleop_node',
        name='teleop_twist_joy',
        output='screen',
        prefix='xterm -e', 
        parameters=[
            os.path.join(
                get_package_share_directory("rmitbot_navigation"),
                "config",
                "teleop_twist_joy.yaml"
            ),
            {"use_sim_time": False},
        ],
        remappings=[
            ('cmd_vel', 'cmd_vel_joystick'),
        ],
    )
    
    
    # teleop_keyboard
    teleop_keyboard = Node( 
        condition=IfCondition(use_keyboard),
        package='teleop_twist_keyboard', 
        executable='teleop_twist_keyboard', 
        name='teleop_twist_keyboard', 
        output='screen', 
        prefix='xterm -e', 
        parameters=[ 
            {"use_sim_time": False}, 
            {'stamped': True},  
            {'frame_id': [prefix, 'base_footprint']},],  
        remappings=[('cmd_vel', 'cmd_vel_keyboard')],  
    ) 

    # twist_stamper_node: navigation does not have time stamped
    twist_stamper_node = Node( 
        package='twist_stamper', 
        executable='twist_stamper', 
        name='twist_stamper', 
        parameters=[ 
            {'frame_id': [prefix, 'base_footprint']},  
            {"use_sim_time": False}, ],  
        remappings=[ 
            ('cmd_vel_in', 'cmd_vel'), 
            ('cmd_vel_out', 'cmd_vel_navigation'), ],  
    ) 

    # twist_mux_node: mixing keyboard and navigation
    twistmux_params = os.path.join(get_package_share_directory("rmitbot_navigation"), "config", "twistmux.yaml") 
    twistmux_node = Node( 
        package='twist_mux', 
        executable='twist_mux', 
        name='twist_mux_node', 
        output='screen', 
        parameters=[
            twistmux_params,  
            {"use_sim_time": False},
        ], 
        remappings=[ 
            ('cmd_vel_out', 'diff_drive_controller/cmd_vel')], 
    ) 

    joystick_twist_stamper = Node(
        condition=IfCondition(use_joy),
        package='twist_stamper',
        executable='twist_stamper',
        name='joystick_twist_stamper',
        parameters=[
            {'frame_id': [prefix, 'base_footprint']},
            {"use_sim_time": False},
        ],
        remappings=[
            ('cmd_vel_in', 'cmd_vel_joystick'),
            ('cmd_vel_out', 'cmd_vel_joystick_stamped'),
        ],
    )

    return LaunchDescription([ 
        prefix_arg,
        use_joy_arg,
        use_keyboard_arg,
        joy_node,
        teleop_joy,
        teleop_keyboard,
        twist_stamper_node,
        joystick_twist_stamper,
        twistmux_node,
    ]) 
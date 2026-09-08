import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.actions import IncludeLaunchDescription, ExecuteProcess, TimerAction, GroupAction
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node 
from nav2_common.launch import RewrittenYaml

def generate_launch_description():
    
    nav_pkg_path = get_package_share_directory("rmitbot_navigation")
    nav_config_file = os.path.join(nav_pkg_path, 'config', 'nav2_params.yaml')

    nodes = []
    
    robot_names = ["robot_0", "robot_1"]
    
    for ns in robot_names:
        
        param_substitutions = {
            'robot_base_frame': f'{ns}/base_footprint',
            'global_frame': f'{ns}/odom',
            'odom_topic': f'/{ns}/odom',
        }
        
        configured_params = RewrittenYaml(
            source_file=nav_config_file,
            root_key=ns,
            param_rewrites=param_substitutions,
            convert_types=True)

        nav2_planner = Node(
            package=    'nav2_planner',
            executable= 'planner_server',
            name=       'planner_server',
            namespace=  ns,
            output=     'screen',
            parameters=[{'use_sim_time': True}, configured_params]
        )
        
        nav2_controller = Node(
            package=    'nav2_controller',
            executable= 'controller_server',
            name=       'controller_server',
            namespace=  ns,
            output=     'screen',
            parameters=[{'use_sim_time': True}, configured_params], 
            remappings=[('cmd_vel', 'cmd_vel_navigation_unstamped')]
            )
            
        nav2_bt_navigator = Node(
            package=    'nav2_bt_navigator',
            executable= 'bt_navigator',
            name=       'bt_navigator',
            namespace=  ns,
            output=     'screen',
            parameters=[{'use_sim_time': True}, configured_params]
            )
        
        nav2_behavior_server = Node(
            package=    'nav2_behaviors',
            executable= 'behavior_server',
            name=       'behavior_server',
            namespace=  ns,
            output=     'screen',
            parameters=[{'use_sim_time': True}, configured_params], 
            remappings=[('cmd_vel', 'cmd_vel_bt_server')]
            )
        
        nav2_smoother_server = Node(
            package=    'nav2_smoother',
            executable= 'smoother_server',
            name=       'smoother_server',
            namespace=  ns,
            output=     'screen',
            parameters=[{'use_sim_time': True}, configured_params]
        )
        
        nav2_lifecycle_manager = Node(
            package=    'nav2_lifecycle_manager',
            executable= 'lifecycle_manager',
            name=       'lifecycle_manager_navigation',
            namespace=  ns,
            output=     'screen',
            parameters=[{'use_sim_time': True}, configured_params]
            )
        
        nodes.extend([
            nav2_planner, 
            nav2_controller,
            nav2_bt_navigator, 
            nav2_behavior_server,
            nav2_smoother_server, 
            nav2_lifecycle_manager
        ])
    
    return LaunchDescription(nodes)
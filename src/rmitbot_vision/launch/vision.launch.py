import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

# check connected camera: v4l2-ctl --list-devices
# ros2 launch rmitbot_vision vision.launch.py

def generate_launch_description():
    # 1. Path to your calibration file
    # Ensure ost.yaml is in your package's config folder
    pkg_share = get_package_share_directory('rmitbot_vision')
    # calib_file_path = 'file://' + os.path.join(pkg_share, 'config', 'ost.yaml')
    # calib_file_path = os.path.join(pkg_share, 'config', 'ost.yaml')
    calib_file_path = 'file://' + os.path.join(pkg_share, 'config', 'ostwebcam.yaml')
    camera_param = os.path.join(pkg_share, 'config', 'camera_param.yaml')
    
    
    
    camera_node = Node( 
        package='usb_cam', 
        executable='usb_cam_node_exe', 
        name='usb_cam_node_exe', 
        output='screen', 
        parameters=[camera_param, 
            {
            'camera_info_url': calib_file_path,
            # 'video_device': '/dev/video0',
        }], 
    ) 
    

    tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='camera_tf_publisher',
        arguments=['--x', '0', '--y', '0', '--z', '0.2', '--roll', '3.14159', '--pitch', '0', '--yaw', '0', '--frame-id', 'base_link', '--child-frame-id', 'camera']
    )

    return LaunchDescription([
        camera_node, 
        tf_node,
    ])
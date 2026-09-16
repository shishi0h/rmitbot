import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, LaunchConfiguration

# Launch the file
# ros2 launch rmitbot_description display.launch.py

def launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace').perform(context)
    prefix = f"{namespace}/" if namespace else ""
    
    pkg_path = get_package_share_directory("rmitbot_description")
    urdf_path = os.path.join(pkg_path, 'urdf', 'rmitbot.urdf.xacro')
    
    import subprocess
    import xml.etree.ElementTree as ET
    
    xacro_cmd = ['xacro', urdf_path]
    urdf_str = subprocess.check_output(xacro_cmd).decode('utf-8')
    
    if prefix:
        root = ET.fromstring(urdf_str)
        for link in root.findall('.//link'):
            if 'name' in link.attrib:
                link.attrib['name'] = prefix + link.attrib['name']
        for joint in root.findall('.//joint'):
            parent = joint.find('parent')
            if parent is not None and 'link' in parent.attrib:
                parent.attrib['link'] = prefix + parent.attrib['link']
            child = joint.find('child')
            if child is not None and 'link' in child.attrib:
                child.attrib['link'] = prefix + child.attrib['link']
        for plugin in root.findall('.//plugin'):
            for frame in plugin.findall('.//frame_name'):
                if frame.text:
                    frame.text = prefix + frame.text
            for frame in plugin.findall('.//bodyName'):
                if frame.text:
                    frame.text = prefix + frame.text
        urdf_str = ET.tostring(root, encoding='unicode')
        
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"use_sim_time": False, "robot_description": urdf_str}],
    )
    
    return [robot_state_publisher]

def generate_launch_description():
    from launch.actions import OpaqueFunction
    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value=''),
        OpaqueFunction(function=launch_setup)
    ])
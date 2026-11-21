"""P4 — map_server + AMCL con el mapa propio y config/amcl.yaml.

  ros2 launch dif_bot localization.launch.py
  ros2 launch dif_bot localization.launch.py map:=/ruta/otro_mapa.yaml
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('dif_bot')
    nav2 = get_package_share_directory('nav2_bringup')
    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=os.path.join(pkg, 'maps', 'mi_mapa.yaml')),
        DeclareLaunchArgument('rviz', default_value='true'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(nav2, 'launch', 'localization_launch.py')),
            launch_arguments={'map': LaunchConfiguration('map'),
                              'params_file': os.path.join(pkg, 'config', 'amcl.yaml'),
                              'use_sim_time': 'true', 'autostart': 'true',
                              'use_composition': 'False'}.items()),
        Node(package='rviz2', executable='rviz2', output='screen',
             arguments=['-d', os.path.join(pkg, 'rviz', 'nav2.rviz')],
             parameters=[{'use_sim_time': True}], condition=IfCondition(LaunchConfiguration('rviz'))),
    ])

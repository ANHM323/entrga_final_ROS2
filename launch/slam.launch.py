"""P3 — SLAM Toolbox (online async) con config/slam_params.yaml.

  ros2 launch dif_bot slam.launch.py
  # guardar:  ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/src/rbtc_proyecto_final/maps/mi_mapa
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
    slam = get_package_share_directory('slam_toolbox')
    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(slam, 'launch', 'online_async_launch.py')),
            launch_arguments={'use_sim_time': 'true', 'use_lifecycle_manager': 'true',
                              'slam_params_file': os.path.join(pkg, 'config', 'slam_params.yaml')}.items()),
        # Activa slam_toolbox (lifecycle) de forma robusta
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
             name='lifecycle_manager_slam', output='screen',
             parameters=[{'use_sim_time': True, 'autostart': True,
                          'node_names': ['slam_toolbox'], 'bond_timeout': 0.0}]),
        Node(package='rviz2', executable='rviz2', output='screen',
             arguments=['-d', os.path.join(pkg, 'rviz', 'nav2.rviz')],
             parameters=[{'use_sim_time': True}], condition=IfCondition(LaunchConfiguration('rviz'))),
    ])

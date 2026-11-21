"""Proyecto final — orquestación completa: Gazebo (warehouse) + EKF + Nav2 + RViz + nodo de misión.

  ros2 launch dif_bot mision.launch.py
  ros2 service call /iniciar_mision std_srvs/srv/Trigger
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('dif_bot')

    def inc(name, args):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg, 'launch', name)),
            launch_arguments=args.items())

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='warehouse'),
        DeclareLaunchArgument('map', default_value=os.path.join(pkg, 'maps', 'mi_mapa.yaml')),
        DeclareLaunchArgument('headless', default_value='false'),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('waypoints', default_value=os.path.join(pkg, 'config', 'waypoints.yaml')),
        inc('sim.launch.py', {'world': LaunchConfiguration('world'), 'publish_odom_tf': 'false',
                                'headless': LaunchConfiguration('headless')}),
        TimerAction(period=5.0, actions=[inc('ekf.launch.py', {})]),
        TimerAction(period=8.0, actions=[inc('navigation.launch.py', {'map': LaunchConfiguration('map'),
                                                                     'rviz': LaunchConfiguration('rviz')})]),
        TimerAction(period=12.0, actions=[Node(
            package='dif_bot', executable='mision.py', output='screen',
            parameters=[{'use_sim_time': True, 'waypoints_file': LaunchConfiguration('waypoints')}])]),
    ])

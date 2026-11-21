"""EKF de robot_localization. Requiere sim.launch.py con publish_odom_tf:=false.

  ros2 launch dif_bot ekf.launch.py              # odom + IMU
  ros2 launch dif_bot ekf.launch.py use_imu:=false
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    cfg = os.path.join(get_package_share_directory('dif_bot'), 'config')
    use_imu = LaunchConfiguration('use_imu')

    def ekf(params_file, condition):
        return Node(package='robot_localization', executable='ekf_node', name='ekf_filter_node',
                    output='screen', parameters=[params_file],
                    remappings=[('odometry/filtered', '/odom_filtered')], condition=condition)

    return LaunchDescription([
        DeclareLaunchArgument('use_imu', default_value='true'),
        ekf(os.path.join(cfg, 'ekf.yaml'), IfCondition(use_imu)),
        ekf(os.path.join(cfg, 'ekf_sin_imu.yaml'), UnlessCondition(use_imu)),
    ])

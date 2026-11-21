"""Simulación del dif_bot en Gazebo Sim.

  ros2 launch dif_bot sim.launch.py use_ros2_control:=false   # plugin DiffDrive de Gazebo
  ros2 launch dif_bot sim.launch.py use_ros2_control:=true    # ros2_control
  ros2 launch dif_bot sim.launch.py world:=warehouse publish_odom_tf:=false   # P2+ con EKF
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument,
                            IncludeLaunchDescription, OpaqueFunction, TimerAction)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# Pose de aparición por mundo: (x, y, z, yaw)
WORLDS = {
    'my_world': (os.path.join(get_package_share_directory('dif_bot'), 'worlds', 'my_world.sdf'),
                 (0.0, 0.0, 0.2, 0.0)),
    'warehouse': (os.path.join(get_package_share_directory('nav2_minimal_tb4_sim'), 'worlds', 'warehouse.sdf'),
                  (2.12, -21.3, 0.2, 1.57)),
    'depot': (os.path.join(get_package_share_directory('nav2_minimal_tb4_sim'), 'worlds', 'depot.sdf'),
              (0.0, 0.0, 0.2, 0.0)),
}


def as_bool(context, name):
    return LaunchConfiguration(name).perform(context).lower() in ('true', '1')


def launch_setup(context):
    pkg = get_package_share_directory('dif_bot')
    use_rc = as_bool(context, 'use_ros2_control')
    odom_tf = as_bool(context, 'publish_odom_tf')
    world = LaunchConfiguration('world').perform(context)
    world_file, (x, y, z, yaw) = WORLDS.get(world, (world, (0.0, 0.0, 0.2, 0.0)))

    import xacro
    robot_description = xacro.process_file(
        os.path.join(pkg, 'urdf', 'robot.urdf.xacro'),
        mappings={'use_ros2_control': str(use_rc).lower(),
                  'publish_odom_tf': str(odom_tf).lower()}).toxml()

    actions = [
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'robot_description': robot_description, 'use_sim_time': True}],
             output='screen'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(
                get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
            launch_arguments={'gz_args': f'-r {world_file}' + (' -s' if as_bool(context, 'headless') else ''), 'on_exit_shutdown': 'true'}.items()),
        TimerAction(period=3.0, actions=[Node(
            package='ros_gz_sim', executable='create', output='screen',
            arguments=['-topic', '/robot_description', '-name', 'dif_bot',
                       '-x', str(x), '-y', str(y), '-z', str(z), '-Y', str(yaw)])]),
    ]

    bridge = ['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
              '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
              '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU']
    if not use_rc:
        bridge += ['/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                   '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                   '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
                   '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V']
    actions.append(Node(package='ros_gz_bridge', executable='parameter_bridge',
                        arguments=bridge, parameters=[{'use_sim_time': True}], output='screen'))

    if use_rc:
        # teleop/Nav2 publican Twist en /cmd_vel; diff_drive_controller espera TwistStamped
        actions.append(Node(package='dif_bot', executable='cmd_vel_to_stamped.py',
                            parameters=[{'use_sim_time': True}], output='screen'))
        if as_bool(context, 'spawn_controllers'):
            actions.append(TimerAction(period=6.0, actions=[
                Node(package='controller_manager', executable='spawner',
                     arguments=['joint_state_broadcaster', 'diff_drive_controller'],
                     output='screen')]))

    if as_bool(context, 'rviz'):
        actions.append(Node(package='rviz2', executable='rviz2', output='screen',
                            arguments=['-d', os.path.join(pkg, 'rviz', 'nav2.rviz')],
                            parameters=[{'use_sim_time': True}]))
    return actions


def generate_launch_description():
    tb4_worlds = os.path.join(get_package_share_directory('nav2_minimal_tb4_sim'), 'worlds')
    return LaunchDescription([
        DeclareLaunchArgument('use_ros2_control', default_value='false'),
        DeclareLaunchArgument('publish_odom_tf', default_value='true',
                              description='false cuando el EKF publica odom->base_link'),
        DeclareLaunchArgument('spawn_controllers', default_value='false',
                              description='true para activar los controladores automáticamente'),
        DeclareLaunchArgument('world', default_value='my_world',
                              description='my_world | warehouse | depot | ruta a .sdf'),
        DeclareLaunchArgument('rviz', default_value='false'),
        DeclareLaunchArgument('headless', default_value='false', description='Gazebo sin GUI'),
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', tb4_worlds),
        OpaqueFunction(function=launch_setup),
    ])

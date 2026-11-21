# Proyecto Final — Robótica Móvil Autónoma (`dif_bot`)

Robot diferencial en **ROS 2 Jazzy + Gazebo Sim (Harmonic)**: control (Gazebo DiffDrive / `ros2_control`), fusión EKF, SLAM Toolbox, AMCL, Nav2 y misiones con `nav2_simple_commander`.

Escuela Colombiana de Ingeniería Julio Garavito — Robótica, 2026.

## Instalación
```bash
cd ~/ros2_ws/src && git clone <este-repo> rbtc_proyecto_final
sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-bringup ros-jazzy-slam-toolbox \
  ros-jazzy-robot-localization ros-jazzy-nav2-minimal-tb4-sim ros-jazzy-gz-ros2-control \
  ros-jazzy-ros2-controllers ros-jazzy-teleop-twist-keyboard
cd ~/ros2_ws && colcon build --symlink-install && source install/setup.bash
```
> El mundo `warehouse` descarga modelos de Gazebo Fuel la primera vez (requiere internet).

## Estructura
```
config/   controllers.yaml ekf.yaml ekf_sin_imu.yaml slam_params.yaml amcl.yaml nav2_params.yaml waypoints.yaml
launch/   sim  ekf  slam  localization  navigation  mision
urdf/     robot.urdf.xacro (condicional use_ros2_control) robot_core sensors gz_control ros2_control gz_physics
scripts/  mision.py  cmd_vel_to_stamped.py
maps/  docs/  results/  video/  worlds/  rviz/
```

Argumentos de `sim.launch.py`: `use_ros2_control` (false), `publish_odom_tf` (true), `spawn_controllers` (false), `world` (`my_world` | `warehouse` | `depot` | ruta .sdf), `rviz`, `headless`.

## Práctica 1 — Control y odometría
```bash
# A) Plugin DiffDrive de Gazebo
ros2 launch dif_bot sim.launch.py use_ros2_control:=false
# B) ros2_control
ros2 launch dif_bot sim.launch.py use_ros2_control:=true
ros2 control load_controller --set-state active joint_state_broadcaster
ros2 control load_controller --set-state active diff_drive_controller

# Teleop y mediciones (ambos casos)
ros2 run teleop_twist_keyboard teleop_twist_keyboard
timeout 30 ros2 topic hz /odom    | tee results/p1_hz_delay_gz.txt      # o _ros2control.txt
timeout 30 ros2 topic delay /odom | tee -a results/p1_hz_delay_gz.txt
```
En ambos modos la interfaz es la misma: `/cmd_vel` (Twist) y `/odom`. En modo `ros2_control`, `cmd_vel_to_stamped.py` convierte a `TwistStamped` para `diff_drive_controller`.

## Práctica 2 — EKF (`robot_localization`)
```bash
ros2 launch dif_bot sim.launch.py world:=warehouse publish_odom_tf:=false
ros2 launch dif_bot ekf.launch.py                  # odom + IMU  -> /odom_filtered
ros2 launch dif_bot ekf.launch.py use_imu:=false   # comparación sin IMU
ros2 run tf2_tools view_frames -o docs/tf_frames
```
`publish_odom_tf:=false` desactiva la TF `odom→base_link` del plugin de Gazebo para que la publique el EKF.
> ⚠️ P2–P6 se ejecutan en modo Gazebo DiffDrive (por defecto). En modo `ros2_control` el TF lo publica `diff_drive_controller` (`enable_odom_tf: true` en `config/controllers.yaml`); para usarlo con el EKF hay que ponerlo en `false`, si no habrá dos TF `odom→base_link`.

## Práctica 3 — SLAM
```bash
ros2 launch dif_bot sim.launch.py world:=warehouse publish_odom_tf:=false rviz:=false
ros2 launch dif_bot ekf.launch.py
ros2 launch dif_bot slam.launch.py
ros2 run teleop_twist_keyboard teleop_twist_keyboard
ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/src/rbtc_proyecto_final/maps/mi_mapa
```

## Práctica 4 — AMCL
```bash
ros2 launch dif_bot sim.launch.py world:=warehouse publish_odom_tf:=false
ros2 launch dif_bot ekf.launch.py
ros2 launch dif_bot localization.launch.py     # usa maps/mi_mapa.yaml + config/amcl.yaml
```
En RViz: *2D Pose Estimate* para fijar/alterar la pose inicial; observar `/particle_cloud`.

## Práctica 5 — Nav2
```bash
ros2 launch dif_bot sim.launch.py world:=warehouse publish_odom_tf:=false
ros2 launch dif_bot ekf.launch.py
ros2 launch dif_bot navigation.launch.py       # config/nav2_params.yaml
```
En RViz: *Nav2 Goal*.

## Proyecto final — Misión autónoma
```bash
ros2 launch dif_bot mision.launch.py           # Gazebo + EKF + Nav2 + RViz + nodo mision
ros2 service call /iniciar_mision std_srvs/srv/Trigger
ros2 service call /cancelar_mision std_srvs/srv/Trigger
ros2 topic echo /estado_mision
```
Los waypoints están en `config/waypoints.yaml` (frame `map`). Ajústalos a tu mapa con *Publish Point* en RViz (`ros2 topic echo /clicked_point`).

Video: `video/mision_demo.mp4` (o enlace).

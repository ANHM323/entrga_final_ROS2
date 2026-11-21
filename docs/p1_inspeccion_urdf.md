# P1 — Inspección del URDF

**Archivos:** `urdf/robot.urdf.xacro` (raíz, condicional `use_ros2_control`), `robot_core.xacro`, `sensors.xacro`, `gz_physics.xacro`, `gz_control.xacro`, `ros2_control.xacro`.

## Joints
| Joint | Tipo | Padre → Hijo | Notas |
|---|---|---|---|
| `drivewhl_l_joint` | continuous | base_link → drivewhl_l_link | eje Y, motriz izquierda |
| `drivewhl_r_joint` | continuous | base_link → drivewhl_r_link | eje Y, motriz derecha |
| `caster_joint` | fixed | base_link → front_caster | rueda loca (esfera, fricción ≈ 0) |
| `base_joint` | fixed | base_link → base_footprint | proyección en el suelo (z = −0.15 m) |
| `imu_joint` | fixed | base_link → imu_link | z = 0.05 m |
| `lidar_joint` | fixed | base_link → lidar_link | z = 0.12 m |
| `camera_joint` | fixed | base_link → camera_link | x = 0.20 m |
| `camera_depth_joint` | fixed | camera_link → camera_depth_frame | frame óptico (rpy −90°, 0, −90°) |

## Sensores
| Sensor | Tipo Gazebo | Tópico ROS | Frecuencia | Frame |
|---|---|---|---|---|
| IMU | `imu` | `/imu` | 50 Hz | imu_link |
| Lidar 2D | `gpu_lidar` 360 muestras, 0.12–10 m | `/scan` | 10 Hz | lidar_link |
| Cámara de profundidad | `depth_camera` 320×240 | (no puenteada) | 15 Hz | camera_depth_frame |

## Parámetros cinemáticos
- Radio de rueda r = 0.10 m; separación entre ruedas = 0.31 + 2·0.025 = **0.36 m**.
- Chasis 0.42 × 0.31 × 0.18 m, 15 kg.

## Frames / árbol TF
`odom → base_link → {base_footprint, drivewhl_l_link, drivewhl_r_link, front_caster, imu_link, lidar_link, camera_link → camera_depth_frame}`; con Nav2: `map → odom` (AMCL o SLAM).

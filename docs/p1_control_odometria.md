# P1 — Control y odometría: comparación

| | Gazebo DiffDrive (`use_ros2_control:=false`) | `ros2_control` (`use_ros2_control:=true`) |
|---|---|---|
| Plugin | `gz-sim-diff-drive-system` | `gz_ros2_control` + `diff_drive_controller` |
| Comando | `/cmd_vel` (Twist) vía ros_gz_bridge | `/cmd_vel` → relay → TwistStamped |
| Odometría | `/odom` vía bridge | `/diff_drive_controller/odom` (remap a `/odom`) |
| TF odom→base_link | plugin Gazebo (gz `/tf` → bridge) | `diff_drive_controller` |
| joint_states | `gz-sim-joint-state-publisher-system` | `joint_state_broadcaster` |
| Publicador de `/odom` | `ros_gz_bridge` | `diff_drive_controller` |
| `/odom` (sim time, en movimiento) | 50.000 Hz, σ = 0.00000 s | 50.000 Hz, σ = 0.00007 s |
| `ros2 topic delay -s /odom` | ≈ 0.000 s (máx 0.003 s) | ≈ 0.000 s (máx 0.001 s) |

Mediciones: `results/p1_hz_delay_gz.txt`, `results/p1_hz_delay_ros2control.txt`.

## 1. ¿Qué controlador genera la odometría en cada caso?
- **`use_ros2_control:=false`**: el plugin `gz::sim::systems::DiffDrive` de Gazebo integra las velocidades de las ruedas dentro del simulador y publica la odometría en el tópico Gazebo `/odom` y la TF en `/tf`; `ros_gz_bridge` las convierte a ROS (`ros2 topic info -v /odom` → nodo `ros_gz_bridge`).
- **`use_ros2_control:=true`**: el `diff_drive_controller` (cargado en el `controller_manager` de `gz_ros2_control`) lee los *state interfaces* de posición/velocidad de las ruedas y calcula la odometría en ROS; publica `/diff_drive_controller/odom` (remapeado a `/odom`) y la TF `odom→base_link` (nodo `diff_drive_controller`).

## 2. ¿Qué diferencias se observan en estabilidad y latencia?
Medido con el robot en movimiento (`results/p1_hz_delay_*.txt`):
- Ambos publican a **50 Hz**. El plugin de Gazebo muestra período constante (σ ≈ 0); `ros2_control` tiene un jitter mínimo (σ ≈ 0.07 ms) porque corre en el lazo del `controller_manager` (`update_rate: 50`).
- La latencia en tiempo de simulación es ≈ 0 en ambos (< 3 ms): en simulación no hay diferencia práctica.
- `ros2_control` limita velocidad y **aceleración** (`linear.x.max_acceleration`, etc.), por lo que el arranque/frenado es más suave y estable; el plugin DiffDrive aplica la velocidad casi instantáneamente.
- `ros2_control` necesita pasos extra (cargar/activar controladores) y convertir `Twist` → `TwistStamped`.

## 3. ¿Cuál enfoque es más adecuado para un robot real?
**`ros2_control`**. El mismo `diff_drive_controller` y `controllers.yaml` sirven para el robot real cambiando solo el plugin de hardware (`gz_ros2_control/GazeboSimSystem` → driver de los motores). El plugin de Gazebo solo existe en simulación; es útil para prototipar rápido, pero no se transfiere al hardware.

# P2 — Fusión sensorial (EKF, `robot_localization`)

Configuración: `config/ekf.yaml` (con IMU) y `config/ekf_sin_imu.yaml`. Lanzamiento: `launch/ekf.launch.py` (remap `odometry/filtered → /odom_filtered`). Árbol TF: `docs/tf_frames.pdf`.

## 1. ¿Qué sensores se fusionan?
- **Odometría de ruedas** (`/odom`): velocidades `vx`, `vy` y `vyaw`. `vy` se fusiona como 0: en un robot diferencial es una restricción real (no hay deslizamiento lateral), y ayuda al filtro.
- **IMU** (`/imu`, 50 Hz): velocidad angular `vyaw` (giroscopio) y aceleración `ax`.
- Se usan **velocidades**, no posiciones, para que las dos fuentes no se contradigan; `two_d_mode: true` ignora z, roll y pitch.

## 2. ¿Qué frame publica el EKF?
Publica la TF **`odom → base_link`** (`world_frame: odom`, `base_link_frame: base_link`, `publish_tf: true`) y el tópico `/odom_filtered` con `frame_id: odom`, `child_frame_id: base_link`. Por eso el simulador se lanza con `publish_odom_tf:=false`: solo debe haber un publicador de esa TF (ver `docs/tf_frames.pdf`: `odom → base_link` lo publica `ekf_filter_node`).

## 3. ¿Qué ocurre si se desactiva la IMU?
El EKF solo integra la odometría de ruedas: `/odom_filtered` prácticamente coincide con `/odom` (diferencia final de **0.005 m**) y el yaw depende solo de las ruedas, sin corrección cuando patinan. Con la IMU el yaw combina las dos fuentes.

## 4. Comparación `/odom` vs `/odom_filtered`
Prueba: cuadrado de 2 m en lazo abierto (`scripts/comparar_odom.py`).

| Caso | Pose final `/odom` | Pose final `/odom_filtered` | Diferencia |
|---|---|---|---|
| Con IMU | (0.017, −0.016, −0.043 rad) | (−0.055, 0.099, −0.175 rad) | 0.136 m |
| Sin IMU | (0.017, 0.034, −0.037 rad) | (0.018, 0.039, −0.062 rad) | 0.005 m |

Gráficas: `results/p2_odom_vs_filtered_imu.png`, `results/p2_odom_vs_filtered_sin_imu.png`.

**Análisis:** en simulación las ruedas no patinan, así que la odometría de ruedas ya es muy buena. La IMU aporta ruido del giroscopio y en cada giro el EKF acumula un pequeño error de yaw (~0.03 rad por giro), lo que deforma el cuadrado. En un robot real ocurre lo contrario: las ruedas patinan al girar y la IMU es la que corrige el yaw. Ajustar las covarianzas (`process_noise_covariance` y la covarianza de cada sensor) define cuánto confía el filtro en cada fuente.

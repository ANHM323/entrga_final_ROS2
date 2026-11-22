# P5 — Navegación con Nav2

Configuración: `config/nav2_params.yaml` (basada en la de `nav2_bringup` para Jazzy, adaptada al robot: `base_link`, `robot_radius: 0.30`, láser de 25 m, odometría `/odom_filtered`). Lanzamiento: `launch/navigation.launch.py`. Capturas: `results/p5_metas_rviz_*.png`.

| Componente | Plugin |
|---|---|
| Planner (`GridBased`) | `nav2_navfn_planner::NavfnPlanner` (Dijkstra/A* sobre el costmap global) |
| Controller (`FollowPath`) | `nav2_mppi_controller::MPPIController` |
| Smoother | `nav2_smoother::SimpleSmoother` |
| Behaviors | `spin`, `backup`, `drive_on_heading`, `assisted_teleop`, `wait` |
| BT | `navigate_to_pose_w_replanning_and_recovery.xml` (por defecto) |

## 1. ¿Qué planner se usa por defecto?
**NavFn** (`nav2_navfn_planner::NavfnPlanner`, `use_astar: false`, es decir, Dijkstra) sobre el costmap global. El BT replanifica a 1 Hz (`RateController`). El seguimiento de la ruta lo hace el controlador **MPPI**.

## 2. ¿Qué comportamiento de recuperación se ejecuta?
El BT `navigate_to_pose_w_replanning_and_recovery` tiene dos niveles:
1. **Recuperación local:** si falla el planner o el controller, primero **limpia el costmap** correspondiente (`ClearGlobalCostmap-Context` / `ClearLocalCostmap-Context`) y reintenta.
2. **Recuperación global** (`RoundRobin`, hasta 6 reintentos): **limpiar ambos costmaps → Spin (1.57 rad) → Wait (5 s) → BackUp (0.30 m a 0.15 m/s)**, alternándolos en ese orden.

Evidencia: `results/p5_metas_rviz_1_trayecto.png` y `_2_llegada.png`: meta a 12 m alcanzada en 28 s, 0 recuperaciones. Una meta fuera del mapa (+60,+60) fue rechazada de inmediato por el planner (FAILED, 0 recuperaciones): el BT no recupera metas fuera del costmap. Para ver spin/backup hay que bloquear la ruta con un obstáculo en Gazebo.

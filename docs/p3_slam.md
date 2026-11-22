# P3 — Mapeo (SLAM Toolbox)

Mundo: **warehouse** (`nav2_minimal_tb4_sim`). Configuración: `config/slam_params.yaml` (online async). Mapa: `maps/mi_mapa.yaml` + `maps/mi_mapa.pgm`. Captura: `results/p3_mapa_rviz.png`.

## 1. ¿Qué resolución tiene el mapa?
**0.05 m/píxel** (5 cm por celda): `resolution: 0.05` en `slam_params.yaml`, y aparece así en `maps/mi_mapa.yaml`. Rango del láser usado: 0.12–25 m.

## 2. ¿Qué errores se observan?
Observados en `maps/mi_mapa.pgm` (ver `results/p3_mapa.png`):
- **Abanico de celdas libres** hacia afuera por una puerta abierta del lado izquierdo: el láser sale del edificio y no encuentra pared.
- **Zonas grises sin explorar** detrás de las estanterías (sombras del láser).
- Con el rango original de 10 m, en los pasillos largos casi todos los rayos daban `inf` y SLAM los descarta: el *scan matching* perdía referencia longitudinal. Se amplió el lidar a **25 m** (`sensors.xacro`, `slam_params.yaml`).
- Bordes con ruido leve (σ = 1 cm) y obstáculos fuera del plano del láser que no aparecen.

## 3. ¿Cómo afecta la velocidad del robot al SLAM?
A mayor velocidad (sobre todo **angular**), los scans consecutivos se solapan menos y el *scan matching* falla con más facilidad: aparecen paredes duplicadas, giros mal estimados y el mapa se "tuerce". SLAM Toolbox solo procesa un scan cada `minimum_travel_distance` (0.5 m) / `minimum_travel_heading` (0.5 rad). Explorando a ≈ 0.2 m/s y giros ≤ 0.5 rad/s se obtuvo un mapa consistente.

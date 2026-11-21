# P3 — Mapeo (SLAM Toolbox)

Mundo: **warehouse** (`nav2_minimal_tb4_sim`). Configuración: `config/slam_params.yaml` (online async). Mapa: `maps/mi_mapa.yaml` + `maps/mi_mapa.pgm`. Captura: `results/p3_mapa_rviz.png`.

## 1. ¿Qué resolución tiene el mapa?
**0.05 m/píxel** (5 cm por celda): `resolution: 0.05` en `slam_params.yaml`, y aparece así en `maps/mi_mapa.yaml`. Rango del láser usado: 0.12–10 m.

## 2. ¿Qué errores se observan?
_COMPLETAR con lo que viste en tu mapa._ Errores típicos a buscar:
- paredes **dobles o desplazadas** cuando el robot vuelve a una zona ya vista (deriva de odometría antes de cerrar el lazo);
- zonas **grises sin explorar** detrás de las estanterías (sombras del láser);
- obstáculos más **bajos o más altos** que el plano del láser (z ≈ 0.27 m) no aparecen;
- ruido en bordes por el ruido del láser (σ = 1 cm).

## 3. ¿Cómo afecta la velocidad del robot al SLAM?
A mayor velocidad (sobre todo **angular**), los scans consecutivos se solapan menos y el *scan matching* falla con más facilidad: aparecen paredes duplicadas, giros mal estimados y el mapa se "tuerce". SLAM Toolbox solo procesa un scan cada `minimum_travel_distance` (0.5 m) / `minimum_travel_heading` (0.5 rad); a velocidades bajas (≈ 0.2 m/s, giros ≤ 0.5 rad/s) el mapa queda más consistente. _Agrega tu observación: compara un recorrido lento y uno rápido._

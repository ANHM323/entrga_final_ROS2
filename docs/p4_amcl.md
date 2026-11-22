# P4 — Localización con AMCL

Configuración: `config/amcl.yaml` (500–2000 partículas, `likelihood_field`, `DifferentialMotionModel`). Lanzamiento: `launch/localization.launch.py`. Capturas: `results/p4_convergencia_*.png`.

## 1. ¿Qué ocurre si el robot inicia en una pose incorrecta?
AMCL distribuye las partículas alrededor de la pose inicial dada. Si es incorrecta, el láser no coincide con el mapa: las partículas no encuentran buena correspondencia, el scan se ve desalineado en RViz y el robot queda "perdido" (las metas de Nav2 fallan o chocan). Con errores pequeños (< ~0.5 m, < ~30°) AMCL converge al mover el robot unos metros. Con errores grandes no se recupera solo, porque `recovery_alpha_slow/fast = 0.0` desactiva la reinyección de partículas aleatorias. Hay que corregirlo con **2D Pose Estimate** o con localización global (`ros2 service call /reinitialize_global_localization std_srvs/srv/Empty`).
**Observado** (`results/p4_pose_incorrecta*.png`): con una pose desplazada 2 m y 0.6 rad el scan queda desalineado. Al mover el robot, las paredes laterales corrigen rápido el error lateral y de yaw, pero el error **longitudinal** a lo largo del pasillo persiste. Con la pose correcta (`results/p4_convergencia_*.png`) la nube se contrae al moverse, aunque queda alargada en la dirección del pasillo.

## 2. ¿Cómo afecta el ruido del láser?
Más ruido hace que cada scan encaje peor con el mapa, así que los pesos de las partículas se parecen más entre sí. La nube converge **más lento**, queda **más dispersa** y la pose estimada "tiembla". AMCL lo modela con `sigma_hit` (0.2 m) y con las mezclas `z_hit`/`z_rand`: si el ruido real supera lo que modela `sigma_hit`, la localización se degrada o salta.
Para probarlo: subir `laser_noise_std` en `urdf/sensors.xacro` (0.01 → 0.1) y recompilar.

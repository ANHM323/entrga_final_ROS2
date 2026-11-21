#!/usr/bin/env python3
"""Nodo de misión autónoma (proyecto final).

- Lee waypoints desde un YAML (parámetro waypoints_file).
- Servicios:
    /iniciar_mision   std_srvs/Trigger  -> ejecuta la secuencia con nav2_simple_commander
    /cancelar_mision  std_srvs/Trigger  -> cancela la misión en curso
- Publica el estado en /estado_mision (std_msgs/String).
"""
import math
import threading

import rclpy
import yaml
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from std_msgs.msg import String
from std_srvs.srv import Trigger


def make_pose(nav, frame, x, y, yaw, latest=False):
    p = PoseStamped()
    p.header.frame_id = frame
    # latest=True: sello 0 = usar la TF más reciente (evita error de extrapolación en AMCL)
    if not latest:
        p.header.stamp = nav.get_clock().now().to_msg()
    p.pose.position.x = float(x)
    p.pose.position.y = float(y)
    p.pose.orientation.z = math.sin(yaw / 2.0)
    p.pose.orientation.w = math.cos(yaw / 2.0)
    return p


class Mision(Node):
    def __init__(self):
        super().__init__('mision')
        self.declare_parameter('waypoints_file', '')
        self.nav = BasicNavigator(node_name='mision_navigator')
        # explícito: el navegador debe usar el reloj de Gazebo
        self.nav.set_parameters([Parameter('use_sim_time', Parameter.Type.BOOL, True)])
        self.cancelar_flag = threading.Event()
        self.thread = None
        self.estado_pub = self.create_publisher(String, 'estado_mision', 10)
        self.create_service(Trigger, 'iniciar_mision', self.iniciar)
        self.create_service(Trigger, 'cancelar_mision', self.cancelar)
        self.estado('Listo. Llame a /iniciar_mision')

    def estado(self, txt):
        self.get_logger().info(txt)
        self.estado_pub.publish(String(data=txt))

    def cargar(self):
        path = self.get_parameter('waypoints_file').value
        with open(path) as f:
            return yaml.safe_load(f)['mision']

    def iniciar(self, _req, res):
        if self.thread and self.thread.is_alive():
            res.success, res.message = False, 'Ya hay una misión en curso'
            return res
        try:
            cfg = self.cargar()
        except Exception as e:  # noqa: BLE001
            res.success, res.message = False, f'Error leyendo waypoints: {e}'
            return res
        self.cancelar_flag.clear()
        self.thread = threading.Thread(target=self.ejecutar, args=(cfg,), daemon=True)
        self.thread.start()
        res.success, res.message = True, f'Misión iniciada con {len(cfg["waypoints"])} waypoints'
        return res

    def cancelar(self, _req, res):
        if self.thread and self.thread.is_alive():
            # cancelTask() se llama desde el hilo de la misión (un solo hilo usa self.nav)
            self.cancelar_flag.set()
            res.success, res.message = True, 'Cancelación solicitada'
        else:
            res.success, res.message = False, 'No hay misión en curso'
        return res

    def ejecutar(self, cfg):
        frame = cfg.get('frame_id', 'map')
        ip = cfg.get('initial_pose')
        if ip:
            self.nav.setInitialPose(make_pose(self.nav, frame, ip['x'], ip['y'], ip.get('yaw', 0.0), latest=True))
        self.estado('Esperando a que Nav2 esté activo...')
        self.nav.waitUntilNav2Active()

        while True:
            wps = cfg['waypoints']
            poses = [make_pose(self.nav, frame, w['x'], w['y'], w.get('yaw', 0.0)) for w in wps]
            self.estado(f'Siguiendo {len(poses)} waypoints')
            self.nav.followWaypoints(poses)
            last = -1
            while not self.nav.isTaskComplete():
                if self.cancelar_flag.is_set():
                    self.nav.cancelTask()
                    self.cancelar_flag.clear()
                fb = self.nav.getFeedback()
                if fb and fb.current_waypoint != last:
                    last = fb.current_waypoint
                    self.estado(f'Rumbo a {wps[last].get("name", last)} ({last + 1}/{len(wps)})')

            result = self.nav.getResult()
            if result == TaskResult.SUCCEEDED:
                self.estado('Misión completada')
            elif result == TaskResult.CANCELED:
                self.estado('Misión cancelada')
                return
            else:
                self.estado('Misión fallida')
                return
            if not cfg.get('loop', False):
                return


def main():
    rclpy.init()
    node = Mision()
    # Executor propio para los servicios: el executor global lo usa BasicNavigator
    # (spin_until_future_complete) desde el hilo de la misión.
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.nav.destroy_node()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

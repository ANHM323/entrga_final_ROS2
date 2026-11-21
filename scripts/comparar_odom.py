#!/usr/bin/env python3
"""P2 — Mueve el robot en lazo abierto y registra /odom vs /odom_filtered.

  ros2 run dif_bot comparar_odom.py --ros-args -p use_sim_time:=true -p salida:=results/p2_imu
Genera <salida>.csv y <salida>.png (trayectorias x-y y yaw en el tiempo).
"""
import csv
import math

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node

# (duración s, v m/s, w rad/s): avance, giro, avance, giro, ... ~un cuadrado de 2 m
PLAN = [(6.7, 0.3, 0.0), (3.14, 0.0, 0.5)] * 4


def yaw(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


class Comparar(Node):
    def __init__(self):
        super().__init__('comparar_odom')
        self.salida = self.declare_parameter('salida', 'p2_odom').value
        self.last = {'odom': None, 'filt': None}
        self.rows = []
        self.create_subscription(Odometry, '/odom', lambda m: self.last.__setitem__('odom', m), 10)
        self.create_subscription(Odometry, '/odom_filtered', lambda m: self.last.__setitem__('filt', m), 10)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.t0 = None
        self.create_timer(0.05, self.tick)
        self.done = False

    def tick(self):
        now = self.get_clock().now().nanoseconds * 1e-9
        if self.t0 is None:
            if self.last['odom'] and self.last['filt'] and now > 0:
                self.t0 = now
            return
        t = now - self.t0
        acc, cmd = 0.0, Twist()
        for d, v, w in PLAN:
            if t < acc + d:
                cmd.linear.x, cmd.angular.z = v, w
                break
            acc += d
        else:
            self.pub.publish(Twist())
            if t > acc + 2.0:
                self.done = True
            return
        self.pub.publish(cmd)
        o, f = self.last['odom'].pose.pose, self.last['filt'].pose.pose
        self.rows.append([round(t, 3), o.position.x, o.position.y, yaw(o.orientation),
                          f.position.x, f.position.y, yaw(f.orientation)])

    def guardar(self):
        with open(self.salida + '.csv', 'w', newline='') as fh:
            w = csv.writer(fh)
            w.writerow(['t', 'odom_x', 'odom_y', 'odom_yaw', 'filt_x', 'filt_y', 'filt_yaw'])
            w.writerows(self.rows)
        r = self.rows[-1]
        d = math.hypot(r[1] - r[4], r[2] - r[5])
        self.get_logger().info(f'Final odom=({r[1]:.3f},{r[2]:.3f},{r[3]:.3f}) '
                               f'filtered=({r[4]:.3f},{r[5]:.3f},{r[6]:.3f}) diferencia={d:.3f} m')
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            c = list(zip(*self.rows))
            fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
            ax[0].plot(c[1], c[2], label='/odom')
            ax[0].plot(c[4], c[5], '--', label='/odom_filtered')
            ax[0].set(xlabel='x [m]', ylabel='y [m]', title='Trayectoria'); ax[0].axis('equal')
            ax[1].plot(c[0], c[3], label='/odom'); ax[1].plot(c[0], c[6], '--', label='/odom_filtered')
            ax[1].set(xlabel='t [s]', ylabel='yaw [rad]', title='Orientación')
            for a in ax:
                a.legend(); a.grid(alpha=.3)
            fig.tight_layout(); fig.savefig(self.salida + '.png', dpi=120)
        except ImportError:
            self.get_logger().warn('matplotlib no disponible: solo CSV')


def main():
    rclpy.init()
    n = Comparar()
    while rclpy.ok() and not n.done:
        rclpy.spin_once(n, timeout_sec=0.1)
    n.guardar()
    n.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Relay /cmd_vel (Twist) -> /cmd_vel_stamped (TwistStamped) para diff_drive_controller."""
import rclpy
from geometry_msgs.msg import Twist, TwistStamped
from rclpy.node import Node


class Relay(Node):
    def __init__(self):
        super().__init__('cmd_vel_to_stamped')
        self.pub = self.create_publisher(TwistStamped, '/cmd_vel_stamped', 10)
        self.create_subscription(Twist, '/cmd_vel', self.cb, 10)

    def cb(self, msg):
        out = TwistStamped()
        out.header.stamp = self.get_clock().now().to_msg()
        out.header.frame_id = 'base_link'
        out.twist = msg
        self.pub.publish(out)


def main():
    rclpy.init()
    rclpy.spin(Relay())


if __name__ == '__main__':
    main()

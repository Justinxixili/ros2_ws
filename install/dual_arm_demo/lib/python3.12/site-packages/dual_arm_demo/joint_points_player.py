#!/usr/bin/env python3
import math
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class JointPointsPlayer(Node):
    def __init__(self, file_path: str):
        super().__init__('joint_points_player')
        self.pub = self.create_publisher(JointState, 'left_arm/joint_command', 10)

        self.points_deg = self.load_points(file_path)
        self.get_logger().info(f'共加载 {len(self.points_deg)} 个点位')

        self.idx = 0
        self.timer = self.create_timer(0.1, self.timer_callback)  # 每 0.1s 走一个点

    def load_points(self, path):
        pts = []
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.replace(',', ' ').split()
                if len(parts) < 7:
                    continue
                vals = [float(x) for x in parts[:7]]  # 角度
                pts.append(vals)
        return pts

    def timer_callback(self):
        if self.idx >= len(self.points_deg):
            self.get_logger().info('点位播放结束')
            return

        degs = self.points_deg[self.idx]

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.position = degs  # 这里仍然用“度”，由 DualArmPublisher 去转弧度

        self.pub.publish(msg)

        self.get_logger().info(f'发送点 {self.idx}: {degs}')
        self.idx += 1


def main(args=None):
    import sys
    rclpy.init(args=args)

    if len(sys.argv) < 2:
        print('用法: ros2 run dual_arm_demo joint_points_player -- points_jdeg.txt')
        return

    node = JointPointsPlayer(sys.argv[1])
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

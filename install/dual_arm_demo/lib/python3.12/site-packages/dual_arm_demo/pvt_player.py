#!/usr/bin/env python3
import time
import logging

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

# ros2 run dual_arm_demo pvt_player -- /home/look/ros2_ws/src/dual_arm_demo/python/testkj.txt
class PVTPlayer(Node):
    def __init__(self, file_path: str):
        super().__init__('pvt_player')
        # 这里的 topic 还是发到 left_arm/joint_command
        self.pub = self.create_publisher(JointState, 'left_arm/joint_command', 10)

        # 只解析关节点，不再解析时间 t
        self.points = self.load_traj(file_path)  # 每项: [7]，顺序 X,Y,Z,A,B,C,U
        self.get_logger().info(f'共加载 {len(self.points)} 个点')

        self.idx = 0

        # 每 5ms 发一个点，相当于 200Hz
        self.timer = self.create_timer(0.005, self.timer_callback)

    def load_traj(self, file_path):
        """
        按你之前 Python 代码的方式解析：
        每行格式类似：
        X 9.999985$Y 19.999975$Z 30.000014$A 40.000026$B 50.000009$C 59.999994$U 69.999995$
        """
        order = ["X", "Y", "Z", "A", "B", "C", "U"]
        points = []

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "$" not in line:
                    continue

                segs = line.split("$")
                vals = {}
                for s in segs:
                    s = s.strip()
                    if not s:
                        continue
                    arr = s.split()
                    if len(arr) == 2:
                        key, val = arr[0], arr[1]
                        try:
                            vals[key] = float(val)
                        except ValueError:
                            # 这一段就算有乱七八糟的字符串也直接跳过
                            pass

                # 按固定顺序取 X,Y,Z,A,B,C,U，没有的补 0.0
                joint = [vals.get(k, 0.0) for k in order]
                points.append(joint)

        return points

    def timer_callback(self):
        # 播完就不再发
        if self.idx >= len(self.points):
            return

        now = self.get_clock().now()

        degs = self.points[self.idx]

        msg = JointState()
        msg.header.stamp = now.to_msg()
        # 这里仍然直接用“度”，由 DualArmPublisher 里统一转弧度
        msg.position = degs

        self.pub.publish(msg)

        # 可选：开 DEBUG 看看播了多少
        # self.get_logger().debug(f'发送点 {self.idx}, deg={degs}')

        self.idx += 1


def main(args=None):
    import sys
    rclpy.init(args=args)

    if len(sys.argv) < 2:
        print('用法: ros2 run dual_arm_demo pvt_player -- test.txt')
        return

    node = PVTPlayer(sys.argv[1])
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

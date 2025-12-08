#!/usr/bin/env python3
import math
from typing import List

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class DualArmPublisher(Node):
    def __init__(self):
        super().__init__('dual_arm_publisher')

        self.left_joint_names: List[str] = [
            'Joint1_L', 'Joint2_L', 'Joint3_L',
            'Joint4_L', 'Joint5_L', 'Joint6_L', 'Joint7_L'
        ]

        self.right_joint_names: List[str] = [
            'Joint1_R', 'Joint2_R', 'Joint3_R',
            'Joint4_R', 'Joint5_R', 'Joint6_R', 'Joint7_R'
        ]

        # 发布给 RViz / robot_state_publisher 的
        self.left_pub = self.create_publisher(JointState, 'left_arm/joint_states', 10)
        self.right_pub = self.create_publisher(JointState, 'right_arm/joint_states', 10)

        # 订阅外部关节“命令角度”（单位：度）
        self.left_cmd_sub = self.create_subscription(
            JointState,
            'left_arm/joint_command',          # 只给左臂做示例
            self.left_command_callback,
            10
        )

        # 当前“目标关节角（单位：度）”
        self.current_left_deg = [-26.908 ,-91.109, 74.502 ,-88.083, -93.599 ,17.151, -13.602]
        self.current_right_deg = [-90.0, -90.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        self.timer = self.create_timer(0.02, self.timer_callback)  # 50Hz
        self.get_logger().info('DualArmPublisher 节点已启动')

    def left_command_callback(self, msg: JointState):
        """接收外部发来的 7 个关节角（度），更新缓存"""
        if len(msg.position) < 7:
            self.get_logger().warn('收到的关节角数量不足 7 个，丢弃')
            return

        self.current_left_deg = list(msg.position[:7])
        self.get_logger().debug(f'更新左臂目标关节角(度): {self.current_left_deg}')

    def timer_callback(self):
        now = self.get_clock().now().to_msg()

        # ✅ 在这里把“度 -> 弧度”
        left_rad = [math.radians(a) for a in self.current_left_deg]
        right_rad = [math.radians(a) for a in self.current_right_deg]

        msg_left = JointState()
        msg_left.header.stamp = now
        msg_left.name = self.left_joint_names
        msg_left.position = left_rad

        msg_right = JointState()
        msg_right.header.stamp = now
        msg_right.name = self.right_joint_names
        msg_right.position = right_rad

        self.left_pub.publish(msg_left)
        self.right_pub.publish(msg_right)


def main(args=None):
    rclpy.init(args=args)
    node = DualArmPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

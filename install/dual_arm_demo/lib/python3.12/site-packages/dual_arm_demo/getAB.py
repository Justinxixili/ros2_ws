#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class GetABJoint(Node):
    def __init__(self):
        super().__init__('get_ab_joint')

        # 左/右臂关节名字，要和 URDF 里的一样
        self.left_joint_names = [
            'Joint1_L', 'Joint2_L', 'Joint3_L',
            'Joint4_L', 'Joint5_L', 'Joint6_L', 'Joint7_L'
        ]
        self.right_joint_names = [
            'Joint1_R', 'Joint2_R', 'Joint3_R',
            'Joint4_R', 'Joint5_R', 'Joint6_R', 'Joint7_R'
        ]

        # 订阅统一的 /joint_states
        self.sub_all = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_callback,
            10
        )

        # 再订阅 left_arm / right_arm
        self.sub_left = self.create_subscription(
            JointState,
            'left_arm/joint_states',
            self.joint_callback,
            10
        )
        self.sub_right = self.create_subscription(
            JointState,
            'right_arm/joint_states',
            self.joint_callback,
            10
        )

        # 记录最新关节角
        self.joint_pos_map = {}   # name -> position(rad)

        # 标记：是否至少收过一次消息
        self.got_any_msg = False
        # 标记：是否已经打印过一次
        self.printed_once = False

        # 每 0.5 s 检查一次是否需要打印
        self.timer = self.create_timer(0.5, self.print_ab_joint)

        self.get_logger().info(
            'getAB started, listening /joint_states & left_arm/right_arm/joint_states'
        )

    def joint_callback(self, msg: JointState):
        # 第一次收到任何 JointState 时提示一下
        if not self.got_any_msg:
            self.got_any_msg = True
            self.get_logger().info(
                f'第一次收到 JointState, joints={list(msg.name)}'
            )

        for name, pos in zip(msg.name, msg.position):
            self.joint_pos_map[name] = pos

    def _get_arm_deg(self, names):
        """按 names 顺序拿该臂的关节角（度），没有就返回 None"""
        deg_list = []
        for n in names:
            if n in self.joint_pos_map:
                rad = self.joint_pos_map[n]
                deg_list.append(math.degrees(rad))
            else:
                deg_list.append(None)
        return deg_list

    def print_ab_joint(self):
        # 已经打印过一次就直接返回，不再打印
        if self.printed_once:
            return

        if not self.got_any_msg:
            # 一个 JointState 都没收过，直接返回
            return

        left_deg = self._get_arm_deg(self.left_joint_names)
        right_deg = self._get_arm_deg(self.right_joint_names)

        # 左右 14 个关节如果全是 None，也不打
        if all(v is None for v in left_deg + right_deg):
            return

        def fmt(lst):
            return ' '.join(
                ('{:8.3f}'.format(v) if v is not None else '   None ')
                for v in lst
            )

 
        self.get_logger().info('Left  (deg): ' + fmt(left_deg))
        self.get_logger().info('Right (deg): ' + fmt(right_deg))

        # 打印完标记一下，以后不再打印
        self.printed_once = True


def main(args=None):
    rclpy.init(args=args)
    node = GetABJoint()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

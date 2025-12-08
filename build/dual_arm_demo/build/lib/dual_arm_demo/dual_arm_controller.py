# dual_arm_controller.py
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class DualArmController(Node):
    def __init__(self):
        super().__init__('dual_arm_controller')

        # 发布 joint_states 话题，RViz 里的 robot_state_publisher 就订阅这个
        self.publisher = self.create_publisher(JointState, 'joint_states', 10)

        # 定时器，100Hz 更新（按需调）
        self.timer = self.create_timer(0.01, self.timer_callback)
        self.t = 0.0

        # TODO: 这里的关节名字要改成你 URDF 里实际的 <joint name="xxx"> 名字
        # 现在先随便举例子，你自己打开 marvin_m6_l.urdf / marvin_m6_r.urdf 对应修改
        self.joint_names = [
            'L_joint1', 'L_joint2', 'L_joint3', 'L_joint4', 'L_joint5', 'L_joint6', 'L_joint7',
            'R_joint1', 'R_joint2', 'R_joint3', 'R_joint4', 'R_joint5', 'R_joint6', 'R_joint7',
        ]

    def timer_callback(self):
        self.t += 0.01
        q = 0.5 * math.sin(self.t)  # 一个简单正弦

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names

        # 左右臂第一个关节做个简单摆动，其他先 0
        positions = [0.0] * len(self.joint_names)
        positions[0] = q       # 左1关节
        positions[7] = -q      # 右1关节
        msg.position = positions

        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = DualArmController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

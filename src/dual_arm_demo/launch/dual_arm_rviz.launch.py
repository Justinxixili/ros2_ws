from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def load_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def generate_launch_description():
    # 找到本包的 share 目录
    pkg_share = get_package_share_directory("dual_arm_demo")

    # ====== 左右臂 URDF 路径 ======
    left_urdf_path = os.path.join(pkg_share, "urdf", "marvin_m6_l.urdf")
    right_urdf_path = os.path.join(pkg_share, "urdf", "marvin_m6_r.urdf")

    left_urdf = load_file(left_urdf_path)
    right_urdf = load_file(right_urdf_path)

    # ====== 左臂 robot_state_publisher ======
    # 放在 left_arm 命名空间里，对应：
    #   /left_arm/robot_description
    #   /left_arm/joint_states
    left_rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        namespace="left_arm",
        name="left_robot_state_publisher",
        parameters=[{"robot_description": left_urdf}],
        output="screen",
    )

    # ====== 右臂 robot_state_publisher ======
    right_rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        namespace="right_arm",
        name="right_robot_state_publisher",
        parameters=[{"robot_description": right_urdf}],
        output="screen",
    )

    # ====== 建一个 world 基座，并把两只手挂上去 ======
    # static_transform_publisher x y z yaw pitch roll frame_id child_frame_id

    left_static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="world_to_left_base",
        arguments=[
            "-0.05", "0.0", "1.5",
            "1.57079632679", "0", "-1.57079632679",
            "world", "Base_L",
        ],
    )



    right_static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="world_to_right_base",
        arguments=[
            "0.05", "0.0", "1.5",
            "1.57079632679", "-0", "1.57079632679",
            "world", "Base_R",
        ],
    )


    # ====== RViz2，附带 LD_PRELOAD 解决 pthread 冲突 ======
    rviz_config_path = os.path.join(pkg_share, "rviz", "dual_arm.rviz")
    rviz_args = []
    if os.path.exists(rviz_config_path):
        rviz_args = ["-d", rviz_config_path]

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=rviz_args,
        additional_env={
            "LD_PRELOAD": "/usr/lib/x86_64-linux-gnu/libpthread.so.0",
            "DISPLAY": os.environ.get("DISPLAY", ":0"),
        },
    )

    return LaunchDescription(
        [
            left_rsp,
            right_rsp,
            left_static_tf,
            right_static_tf,
            rviz_node,
        ]
    )

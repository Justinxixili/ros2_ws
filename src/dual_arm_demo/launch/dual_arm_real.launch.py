from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def load_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def generate_launch_description():
    pkg_share = get_package_share_directory("dual_arm_demo")

    left_urdf_path = os.path.join(pkg_share, "urdf", "marvin_m6_l.urdf")
    right_urdf_path = os.path.join(pkg_share, "urdf", "marvin_m6_r.urdf")

    left_urdf = load_file(left_urdf_path)
    right_urdf = load_file(right_urdf_path)

    use_rviz = LaunchConfiguration("use_rviz")

    left_rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        namespace="left_arm",
        name="left_robot_state_publisher",
        parameters=[{"robot_description": left_urdf}],
        output="screen",
    )

    right_rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        namespace="right_arm",
        name="right_robot_state_publisher",
        parameters=[{"robot_description": right_urdf}],
        output="screen",
    )

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
        condition=IfCondition(use_rviz),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_rviz",
                default_value="true",
                description="Whether to launch RViz2",
            ),
            left_rsp,
            right_rsp,
            left_static_tf,
            right_static_tf,
            rviz_node,
        ]
    )

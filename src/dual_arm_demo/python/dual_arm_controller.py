#!/usr/bin/env python3
import os
import time
import logging
from fx_kine import Marvin_Kine

logging.basicConfig(format='%(message)s')
logger = logging.getLogger('debug_printer')
logger.setLevel(logging.INFO)

# ========= 路径定位（避免 FileNotFoundError） =========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_PATH = os.path.join(SCRIPT_DIR, "figure_eight_path.txt")
OUT_PATH = os.path.join(SCRIPT_DIR, "traj_figure8_point.txt")

# ========= 工具函数 =========
def load_figure_eight(path):
    pts = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            u, v = map(float, line.split())
            pts.append((u, v))
    return pts


def format_point(x, y, z, a, b, c, u=0.0, v=0.0, w=0.0):
    return (
        f"X {x:.6f}$"
        f"Y {y:.6f}$"
        f"Z {z:.6f}$"
        f"A {a:.6f}$"
        f"B {b:.6f}$"
        f"C {c:.6f}$"
        f"U {u:.6f}$"
        f"V {v:.6f}$"
        f"W {w:.6f}$"
    )


# ========= 主流程 =========
def main():
    kk = Marvin_Kine()

    ini = kk.load_config(
        "/home/look/文档/TJ_FX_ROBOT_CONTRL_SDK-master/"
        "TJ_FX_ROBOT_CONTRL_SDK-master/demo_linux_win/python/ccs_m6.MvKDCfg"
    )
    time.sleep(0.2)

    assert kk.initial_kine(
        robot_serial=0,
        robot_type=ini["TYPE"][0],
        dh=ini["DH"][0],
        pnva=ini["PNVA"][0],
        j67=ini["BD"][0],
    ), "initial_kine 失败"

    # ===== 起始关节 =====
    ref_joints = [
        -5.918, -35.767, 49.494,
        -68.112, -90.699, 49.211, -23.995
    ]

    # 正解得到基准位姿
    fk_mat = kk.fk(robot_serial=0, joints=ref_joints)
    base_pose = kk.mat4x4_to_xyzabc(fk_mat)

    logger.info(f"Base pose XYZABC = {base_pose}")

    # ===== 8字路径 =====
    path = load_figure_eight(FIG_PATH)
    logger.info(f"Loaded {len(path)} points")

    scale = 50.0   # XY 放大比例（mm）
    points = []

    for u, v in path:
        pose = base_pose.copy()
        pose[0] += u * scale
        pose[1] += v * scale

        # 转回 4x4 姿态
        pose_mat = kk.xyzabc_to_mat4x4(pose)

        ik = kk.ik(
            robot_serial=0,
            pose_mat=pose_mat,
            ref_joints=ref_joints
        )
        if not ik:
            logger.warning("IK failed, skip one point")
            continue

        # 用这一步的解作为下一步参考，防跳解
        ref_joints = ik.m_Output_RetJoint.to_list()

        # 姿态直接用 XYZABC
        x, y, z, a, b, c = pose
        points.append((x, y, z, a, b, c))

    # ===== 写文件 =====
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(f"PoinType=9@{len(points)}\n")
        for p in points:
            f.write(format_point(*p) + "\n")

    logger.info(f"✅ 已生成点位文件: {OUT_PATH}")
    logger.info(f"✅ 点位数量: {len(points)}")


if __name__ == "__main__":
    main()

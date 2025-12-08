#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fx_kine import Marvin_Kine
import time
import logging
import copy


logging.basicConfig(format='%(message)s')
logger = logging.getLogger('debug_printer')
logger.setLevel(logging.INFO)   

CFG_PATH = "/home/look/文档/TJ_FX_ROBOT_CONTRL_SDK-master/TJ_FX_ROBOT_CONTRL_SDK-master/demo_linux_win/python/ccs_m6.MvKDCfg"


DELTA_FILE = "/home/look/ros2_ws/src/dual_arm_demo/python/figure_eight_path.txt"

OUTPUT_FILE = "/home/look/ros2_ws/src/dual_arm_demo/python/figure_eight_joint_pvt.txt"

START_JOINTS = [-26.908 ,-91.109, 74.502 ,-88.083, -93.599 ,17.151, -13.602]


ALLOW_DGR = [0.05, 0.05]




def load_xy_increments(path):
    """从文件中读取 XY 增量，每行: dx dy"""
    deltas = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            dx = float(parts[0])
            dy = float(parts[1])
            deltas.append((dx, dy))
    return deltas


def joints_to_line(joints):

    j1, j2, j3, j4, j5, j6, j7 = joints
    line = (
        f"X {j1:.6f}$Y {j2:.6f}$Z {j3:.6f}$"
        f"A {j4:.6f}$B {j5:.6f}$C {j6:.6f}$"
        f"U {j7:.6f}$V 0.000000$W 0.000000$"
    )
    return line




def main():

    kk = Marvin_Kine()
    ini_result = kk.load_config(CFG_PATH)
    time.sleep(0.1)

    initial_kine_tag = kk.initial_kine(
        robot_serial=0,
        robot_type=ini_result['TYPE'][0],
        dh=ini_result['DH'][0],
        pnva=ini_result['PNVA'][0],
        j67=ini_result['BD'][0]
    )
    time.sleep(0.1)


    tool = [[1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]]
    kk.set_tool_kine(robot_serial=0, tool_mat=tool)

    time.sleep(0.1)

    fk_mat = kk.fk(robot_serial=0, joints=START_JOINTS)
    base_xyzabc = kk.mat4x4_to_xyzabc(fk_mat) 
    print("基准 XYZABC:", base_xyzabc)


    deltas = load_xy_increments(DELTA_FILE)
    print(f"共读取增量点: {len(deltas)}")


    out_lines = []
    last_joints = copy.deepcopy(START_JOINTS)

    for idx, (dx, dy) in enumerate(deltas):
  
        target_xyzabc = base_xyzabc.copy()
        target_xyzabc[0] += dx*1000 
        target_xyzabc[2] += dy*1000  
    


        target_mat = kk.xyzabc_to_mat4x4(target_xyzabc)

  
        ik_res = kk.ik(
            robot_serial=0,
            pose_mat=target_mat,
            ref_joints=[-26.908 ,-91.109, 74.502 ,-88.083, -93.599 ,17.151, -13.602]
        )

        use_res = None

        def ik_ok(res):
    
            if not res:
                return False
            if res.m_Output_IsOutRange:
                return False
            if res.m_Output_IsJntExd:
                return False
            return True

        if ik_ok(ik_res):
            use_res = ik_res
        else:
 
            ik_nsp_res = kk.ik_nsp(
                robot_serial=0,
                pose_mat=target_mat,
                ref_joints=[-26.908 ,-91.109, 74.502 ,-88.083, -93.599 ,17.151, -13.602],
                zsp_type=0,          
                zsp_para=[0, 0, 0, 0, 0, 0],
                zsp_angle=0.0,        
                dgr=ALLOW_DGR
            )
            if ik_ok(ik_nsp_res):
                use_res = ik_nsp_res

   
        if not use_res:
            print(f"[跳过] idx={idx}, dx={dx:.6f}, dy={dy:.6f} 逆解失败或超限")
            continue

        joints = use_res.m_Output_RetJoint.to_list()
        last_joints = joints

        line = joints_to_line(joints)
        out_lines.append(line)

 
    with open(OUTPUT_FILE, "w") as f:
        f.write(f"PoinType=9@{len(out_lines)}\n")
        for line in out_lines:
            f.write(line + "\n")

    print(f"生成完成：{OUTPUT_FILE}")
    print(f"有效点数量: {len(out_lines)}")


if __name__ == "__main__":
    main()

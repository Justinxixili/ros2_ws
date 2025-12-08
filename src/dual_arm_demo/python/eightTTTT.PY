import math

def generate_figure8_deltas(
    A=50.0,          # X 方向幅值
    B=50.0,          # Y 方向幅值
    n_points=5000  # ✅ 已加密（原来 200）
):
    """生成一条 8 字形轨迹的 Δx, Δy 增量列表"""
    points = []

    # 1) 生成绝对坐标 (x, y)
    for i in range(n_points):
        t = 2 * math.pi * i / (n_points - 1)
        x = A * math.sin(t)
        y = B * math.sin(2 * t)
        points.append((x, y))

    # 2) 转成增量坐标 Δx, Δy
    deltas = []
    prev_x, prev_y = points[0]
    deltas.append((0.0, 0.0))

    for i in range(1, n_points):
        x, y = points[i]
        dx = x - prev_x
        dy = y - prev_y
        deltas.append((dx, dy))
        prev_x, prev_y = x, y

    return deltas


if __name__ == "__main__":
    deltas = generate_figure8_deltas(A=50.0, B=50.0)

    with open("figure8_xy_delta.txt", "w") as f:
        for dx, dy in deltas:
            f.write(f"{dx:.6f} {dy:.6f}\n")

    print(f"已生成 {len(deltas)} 个 8 字形 XY 增量点（已加密）")

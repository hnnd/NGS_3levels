#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_geometric_stop_model.py — 生成 04_geometric_stop_model.svg（FIG-U07-04：几何分布随机终止模型）【data-plot】

方案：reviews/course/U07_FIGP_001.md §4.2 FIG-U07-04（P16，cols 一栏，viewBox 800×700）。
数据（与 demos 现跑一致，import 复算）：demos/ch09_orf_length.py --selftest：
p = 3/64 = 0.046875，含终止平均步数 1/p = 21.3，终止前非终止 (1−p)/p = 20.3
（教材 §9.4.2 L100–106、§9.10；两个均值相差恰为 1，不得混用）。
合成算例标注（图内灰字）。无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 04_geometric_stop_model.py
"""
from svghelp import *  # noqa: F401,F403
import ch09_orf_length as orfdemo


def main():
    p = orfdemo._P_STOP  # 3/64，与 demos 同一常量
    steps_incl = 1.0 / p          # 21.333…（含终止密码子本身）
    steps_before = (1.0 - p) / p  # 20.333…（终止前非终止个数）
    assert abs(p - 3.0 / 64.0) < 1e-12
    assert abs(steps_incl - 21.3333) < 0.01 and round(steps_incl, 1) == 21.3
    assert abs(steps_before - 20.3333) < 0.01 and round(steps_before, 1) == 20.3
    print(f"check: p={p:.6f} 1/p={steps_incl:.1f} (1-p)/p={steps_before:.1f}")

    s = SVG(800, 700)
    s.text(760, 48, "合成算例", 30, GRAY, "end")

    # 顶部公式条（深蓝）
    s.rect(170, 66, 460, 70, BLUE, rx=12)
    s.text(400, 112, "p = 3/64 = 0.046875", 36, WHITE, "middle", "bold")

    # 中部：密码子方格链，第 21 格为终止密码子（橙）
    X0, CW, CY = 40, 28, 300
    STOP_POS = 21
    for i in range(1, 25):
        x = X0 + (i - 1) * CW
        if i == STOP_POS:
            s.rect(x, CY, CW - 3, 56, ORANGE, rx=6)
        else:
            s.rect(x, CY, CW - 3, 56, BLUE_TINT, BLUE, 3, rx=6)
    s.arrow(8, CY + 28, 34, CY + 28, GRAY, 5, head=12)
    s.text(X0 + (STOP_POS - 1) * CW + 12, 276, "密码子是终止", 32, INK,
           "middle", "bold")
    s.text(X0 + (STOP_POS - 1) * CW + 12, 226, "21", 30, GRAY, "middle")

    # 上方刻度尺：含终止 1..21 格 = 21.3 步
    x21 = X0 + 21 * CW - 3
    s.line(X0, 420, x21, 420, BLUE, 5)
    s.line(X0, 420, X0, 434, BLUE, 5)
    s.line(x21, 420, x21, 434, BLUE, 5)
    s.text((X0 + x21) / 2, 470, "含终止平均步数 = 21.3", 32, BLUE, "middle",
           "bold")

    # 下方刻度尺：终止前 1..20 格 = 20.3 个（同为起点、短一格 → 差一）
    x20 = X0 + 20 * CW - 3
    s.line(X0, 530, x20, 530, GREEN, 5)
    s.line(X0, 530, X0, 516, GREEN, 5)
    s.line(x20, 530, x20, 516, GREEN, 5)
    s.text((X0 + x20) / 2, 580, "终止前非终止 = 20.3", 32, GREEN, "middle",
           "bold")

    # 底部红色辨析条（唯一红色）
    s.rect(190, 628, 420, 56, RED, rx=12)
    s.text(400, 668, "差一但含义不同", 32, WHITE, "middle", "bold")

    s.save("04_geometric_stop_model.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

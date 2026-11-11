#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_canu_olc_vs_flye_repeat.py — 生成 12_canu_olc_vs_flye_repeat.svg（FIG-U08-12：
Canu OLC 三步 vs Flye 重复图展开）

方案：reviews/course/U08_FIGP_001.md §4 FIG-U08-12（P38，cols 一栏，800×700）。
定性算法机制图，无数字（教材 §8.4.5 L216–222、讲义 ④ 4.1.2）：
上泳道 Canu OLC：Correct(纠错) → Trim(修剪) → Assemble(布局)，深蓝方块串联；
下泳道 Flye：disjointigs → 重复图（中央橙色共享重复块）→ 长读段红色定向
跨越弧解决分叉；底部双组装独立验证。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 12_canu_olc_vs_flye_repeat.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # —— 上泳道：Canu OLC ——
    s.text(60, 84, "Canu：纠错修剪布局", 34, BLUE, "start", "bold")
    y, bh, bw = 130, 96, 170
    for i, en in enumerate(("Correct", "Trim", "Assemble")):
        x = 60 + i * (bw + 56)
        s.rect(x, y, bw, bh, BLUE, rx=14)
        s.text(x + bw / 2, y + bh / 2 + 12, en, 32, WHITE, "middle", "bold")
        if i < 2:
            s.arrow(x + bw + 6, y + bh / 2, x + bw + 50, y + bh / 2, BLUE, 7)

    # —— 下泳道：Flye 重复图 ——
    s.text(60, 360, "Flye：重复图长读段定路径", 34, CYAN_DEEP, "start",
           "bold")
    y2 = 410
    s.rect(60, y2, 180, 84, WHITE, CYAN_DEEP, 4, rx=12)
    s.text(150, y2 + 52, "disjointigs", 30, CYAN_DEEP, "middle", "bold")
    s.arrow(246, y2 + 42, 296, y2 + 42, CYAN_DEEP, 6)

    # 重复图：三个节点 + 两条边，中央橙色共享重复块
    gx = 300
    n1, n2, n3 = (gx + 20, y2 + 42), (gx + 130, y2 + 42), (gx + 240, y2 + 42)
    s.line(n1[0], n1[1], n2[0], n2[1], GRAY, 5)
    s.line(n2[0], n2[1], n3[0], n3[1], GRAY, 5)
    s.rect(gx + 62, y2 + 22, 66, 40, ORANGE, rx=8)
    s.text(gx + 95, y2 + 112, "repeat", 30, GRAY, "middle")
    for n in (n1, n2, n3):
        s.circle(n[0], n[1], 16, CYAN_DEEP)
    # 长读段红色定向跨越弧（解决分叉的关键事件，唯一红）
    s.path(f"M {n1[0]} {n1[1] - 16} C {n1[0] + 60} {n1[1] - 96}, "
           f"{n3[0] - 60} {n3[1] - 96}, {n3[0]} {n3[1] - 16}", RED, 6)
    s.polygon([(n3[0] + 2, n3[1] - 30), (n3[0] - 14, n3[1] - 40),
               (n3[0] - 2, n3[1] - 12)], RED)
    s.text(466, 376, "long read span", 30, RED, "start", "bold")
    s.arrow(560, y2 + 42, 610, y2 + 42, CYAN_DEEP, 6)
    s.circle(650, y2 + 42, 26, GREEN)
    s.text(650, y2 + 52, "asm", 30, WHITE, "middle", "bold")

    # 底部结论
    s.rect(160, 580, 480, 62, BLUE, rx=12)
    s.text(400, 623, "双组装互为独立验证", 36, WHITE, "middle", "bold")

    s.save("12_canu_olc_vs_flye_repeat.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

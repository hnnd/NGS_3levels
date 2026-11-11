#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_design_decision_flow.py — 生成 01_design_decision_flow.svg
（FIG-M01-01：实验设计三问与不可逆决策流）

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-01（P9，cols 一栏，800×700）。
依据：教材 §13.1 L22–28；讲义 ③3.1。无数字、无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 01_design_decision_flow.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    steps = [
        (80, "① 测什么：平台与文库"),
        (270, "② 要多少：重复与深度"),
        (460, "③ 怎么排：批次元数据"),
    ]
    for y, t in steps:
        s.rect(110, y, 460, 118, BLUE, rx=16)
        s.text(340, y + 74, t, 38, WHITE, "middle", "bold")

    s.arrow(340, 204, 340, 262, CYAN, 8)
    s.arrow(340, 394, 340, 452, CYAN, 8)

    # 右侧红色反向弧线：顺序不可倒（全图唯一红色）
    s.path("M 586 519 C 726 486, 726 172, 586 139", RED, 6)
    ang = -math.pi / 2
    x2, y2 = 586, 139
    s.polygon([
        (x2, y2),
        (x2 - 20 * math.cos(ang - 0.42), y2 - 20 * math.sin(ang - 0.42)),
        (x2 - 20 * math.cos(ang + 0.42), y2 - 20 * math.sin(ang + 0.42)),
    ], RED)
    s.text(684, 340, "顺序不可倒", 34, RED, "middle", "bold", rotate=90)

    s.save("01_design_decision_flow.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

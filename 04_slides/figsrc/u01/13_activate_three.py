#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_activate_three.py — 生成 13_activate_three.svg
（FIG-U01-13：激活做三件事——PATH 前插 / activate.d / 环境变量）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-13（P32，cols 一栏，800×700）。
数据：无数字。
依据：教材 §2.4.3 L150–152（三件事定义）、L163 callout（提示符里的环境名是字符串）。
边界：①PATH 前插的视觉承载在 P30 工具箱图，本图窄条带过（同概念一张图）。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 13_activate_three.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 标题
    s.text(400, 56, "激活做三件事", 40, BLUE, "middle", "bold")

    # 竖排三块（①窄条带过：视觉承载在 P30 工具箱图）
    blocks = [
        (96, "① PATH 前插", BLUE, BLUE_TINT, 84),
        (256, "② activate.d", ORANGE, ORANGE_TINT, 130),
        (462, "③ 环境变量", PURPLE, PURPLE_TINT, 100),
    ]
    bx, bw = 90, 470
    for by, label, col, tint, h in blocks:
        s.rect(bx, by, bw, h, tint, col, 4, rx=12)
        s.text(bx + 24, by + h / 2 + 12, label, 34, col, weight="bold")

    # 右侧绿色勾列：三件都可观察
    s.rect(600, 256, 150, 306, GREEN_TINT, GREEN, 4, rx=12)
    for yy in (330, 415, 500):
        s.line(636, yy, 650, yy + 12, GREEN, 7, cap="round")
        s.line(650, yy + 12, 676, yy - 18, GREEN, 7, cap="round")
    s.text(675, 600, "三件都可观察", 30, GREEN, "middle", "bold")

    # 底部红色横幅
    s.rect(120, 610, 560, 62, RED_TINT, RED, 4, rx=12)
    s.text(400, 652, "提示符变了≠环境对了", 34, RED, "middle", "bold")

    s.save("13_activate_three.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

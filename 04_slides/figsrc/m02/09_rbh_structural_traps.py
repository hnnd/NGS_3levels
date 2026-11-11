#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_rbh_structural_traps.py — 09_rbh_structural_traps.svg
（FIG-M02-13，P31，cols）：双向最佳命中（RBH）双重结构性陷阱【new-svg】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-13（FT11-03 题材）。
依据：教材 §11.4.1；Emms & Kelly 2019。无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 09_rbh_structural_traps.py
"""
from svghelp import (BLUE, CYAN, GRAY, INK, PANEL, RED, SVG, WHITE)


def cross(s, cx, cy, r, color, sw=7):
    s.line(cx - r, cy - r, cx + r, cy + r, color, sw, cap="round")
    s.line(cx - r, cy + r, cx + r, cy - r, color, sw, cap="round")


def main():
    s = SVG(800, 700)

    # 左面板：协同直系一对二被砍断（A 复制为 A1/A2，B 单拷贝）
    s.rect(30, 70, 355, 470, WHITE, PANEL, 3, rx=14)
    s.text(70, 130, "species A", 30, GRAY, "middle")
    s.text(70, 400, "species B", 30, GRAY, "middle")
    s.circle(150, 190, 22, BLUE)
    s.text(150, 201, "A1", 30, WHITE, "middle", "bold")
    s.circle(310, 190, 22, BLUE)
    s.text(310, 201, "A2", 30, WHITE, "middle", "bold")
    s.circle(230, 420, 22, BLUE)
    s.text(230, 431, "B", 30, WHITE, "middle", "bold")
    # B↔A1 双向最佳命中（青蓝实线双向箭头）
    s.darrow(218, 398, 158, 214, CYAN, 6)
    # B−A2 真协同直系被贪心砍断（红色虚线 + 叉）
    s.line(242, 398, 298, 214, RED, 5, dash="14 10")
    cross(s, 270, 306, 18, RED)
    s.text(207, 500, "协同直系一对二被砍断", 30, RED, "middle", "bold")

    # 右面板：真直系丢失，回搜落入旁系
    s.rect(415, 70, 355, 470, WHITE, PANEL, 3, rx=14)
    s.text(455, 130, "species A", 30, GRAY, "middle")
    s.text(455, 400, "species B", 30, GRAY, "middle")
    # 真直系已丢失（虚线灰影）
    s.circle(500, 190, 22, WHITE, GRAY, 5, dash="12 9")
    s.text(500, 201, "lost", 30, GRAY, "middle", "bold")
    # 旁系同源基因 P
    s.circle(680, 190, 22, BLUE)
    s.text(680, 201, "P", 30, WHITE, "middle", "bold")
    s.circle(560, 420, 22, BLUE)
    s.text(560, 431, "B", 30, WHITE, "middle", "bold")
    # B 误选旁系 P（红色交叉线）
    s.line(572, 398, 668, 214, RED, 5)
    cross(s, 620, 306, 18, RED)
    s.text(592, 500, "真直系丢失误选旁系", 30, RED, "middle", "bold")

    # 底部总结
    s.text(400, 650, "结构性缺陷非随机噪声", 36, INK, "middle", "bold")

    s.save("09_rbh_structural_traps.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

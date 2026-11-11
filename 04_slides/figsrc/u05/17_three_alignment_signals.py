#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_three_alignment_signals.py — 生成 17_three_alignment_signals.svg（FIG-U05-17：三类比对信号）

方案：reviews/course/U05_FIGP_001.md §4 FIG-U05-17（P56，cols 一栏，viewBox 800×700）。
参考轴上三区：①局部深度异常（某区柱形 ≈2× 背景，角标＝竞争解释占位）
②分裂比对（一条读段拆两落，FLAG 2048）③软剪切聚集（S 簇同坐标）；
红条＝只是待解释的观测。依据教材 §7.6 L448（≈2× 为原文倍数关系）。
只画信号本身，不涉任何具体研究案例（hold_redraw F07-06 的 deck 级替代，Q7）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 17_three_alignment_signals.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 区间分隔（淡虚线）
    s.line(305, 110, 305, 520, PANEL, 3, dash="12 10")
    s.line(535, 110, 535, 520, PANEL, 3, dash="12 10")

    # ① 局部深度异常：小柱形图，中区凸起 ≈ 2× 背景
    s.text(182, 130, "深度翻倍", 32, INK, "middle", "bold")
    s.text(182, 170, "拷贝数？塌缩？", 30, INK, "middle", "bold")
    s.text(182, 206, "比对错误？", 30, INK, "middle", "bold")
    for bx, bh in ((126, 30), (152, 24)):
        s.rect(bx, 360 - bh, 20, bh, BLUE_TINT, rx=3)
    s.rect(178, 300, 20, 60, ORANGE, rx=3)   # 凸起 ≈ 2×
    for bx, bh in ((204, 26), (230, 30)):
        s.rect(bx, 360 - bh, 20, bh, BLUE_TINT, rx=3)

    # ② 分裂比对：一条读段拆两段、落两个坐标（虚线相连）
    s.text(420, 130, "分裂比对", 32, INK, "middle", "bold")
    s.text(420, 176, "FLAG 2048", 30, PURPLE, "middle", "bold")
    s.rect(330, 322, 80, 28, CYAN, rx=6)
    s.path("M 412 334 C 430 334, 432 274, 450 274", PURPLE, 4, dash="10 8")
    s.rect(450, 260, 60, 28, PURPLE, rx=6)

    # ③ 软剪切聚集：多条读段同坐标露出 S 段
    s.text(652, 130, "软剪切聚集", 32, INK, "middle", "bold")
    for y in (225, 270, 315):
        s.rect(560, y, 140, 28, CYAN, rx=6)
        s.rect(700, y, 30, 28, CYAN_DEEP, rx=6)
        s.text(715, y + 22, "S", 30, WHITE, "middle", "bold")

    # 参考轴（三区共用）
    s.line(60, 360, 740, 360, BLUE, 8)
    s.text(60, 400, "reference", 30, GRAY, "start", "bold")

    # 底部红条（唯一红）
    s.rect(60, 560, 680, 64, RED, rx=12)
    s.text(400, 603, "只是待解释的观测", 34, WHITE, "middle", "bold")

    s.save("17_three_alignment_signals.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

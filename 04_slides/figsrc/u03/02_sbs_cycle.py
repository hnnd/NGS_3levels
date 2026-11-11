#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_sbs_cycle.py — 生成 02_sbs_cycle.svg（FIG-U03-02：Illumina SBS 三步循环）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-02（P17，cols 一栏，800×700）。
教材依据：chapters/ch04/manuscript.qmd §4.4.2。
一轮循环：掺入（带荧光与 3′ 封闭基团的 dNTP）→ 成像 → 切除（恢复 3′-OH）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 02_sbs_cycle.py
"""
from svghelp import *  # noqa: F401,F403

BASE_COLORS = {"A": GREEN, "C": CYAN, "G": ORANGE, "T": PURPLE}


def main():
    s = SVG(800, 700)
    s.text(400, 52, "边合成边测序三步循环", 36, BLUE, "middle", "bold")

    # 三张步骤卡（横排）
    cards = [(60, "① 掺入"), (300, "② 成像"), (540, "③ 切除")]
    for x, label in cards:
        s.rect(x, 96, 200, 150, WHITE, PANEL, 3, rx=16)
        s.text(x + 100, 150, label, 34, INK, "middle", "bold")

    # ① 掺入：延伸链 + 接入的 dNTP（A/C/G/T 碱基色），3′ 端红色封闭基团
    s.polyline([(85, 210), (150, 210), (170, 190)], CYAN_DEEP, 7)
    for i, b in enumerate("ACG"):
        s.rect(88 + i * 26, 196, 22, 28, BASE_COLORS[b], rx=4)
        s.text(99 + i * 26, 218, b, 22, WHITE, "middle", "bold")
    s.rect(172, 186, 26, 38, RED, rx=4)
    s.text(185, 212, "T", 22, WHITE, "middle", "bold")
    # ② 成像：激发光点 + 相机光圈
    s.circle(400, 205, 30, ORANGE)
    s.circle(400, 205, 16, WHITE)
    s.circle(400, 205, 7, ORANGE)
    # ③ 切除：剪刀示意（两条交叉线）+ 游离荧光分子
    s.line(590, 180, 640, 230, GRAY, 6)
    s.line(640, 180, 590, 230, GRAY, 6)
    s.circle(680, 205, 12, CYAN)

    # 红色焦点：3′ 封闭基团徽章
    s.rect(250, 262, 160, 56, RED, rx=12)
    s.text(330, 300, "3′ 封闭基团", 30, WHITE, "middle", "bold")

    # 循环大箭头：③ → ①（下方圆弧回路）
    s.path("M 640 262 C 640 420, 160 420, 160 262", None, 0)
    s.path("M 640 268 C 640 430, 170 430, 166 274",
           CYAN_DEEP, 8, dash="2 16")
    s.polygon([(160, 262), (190, 268), (172, 292)], CYAN_DEEP)

    # 中央结论：一轮只读一个碱基
    s.circle(400, 520, 105, WHITE, BLUE, 6)
    s.text(400, 500, "1 轮循环", 34, BLUE, "middle", "bold")
    s.text(400, 545, "只读 1 个碱基", 34, BLUE, "middle", "bold")
    s.arrow(330, 330, 360, 420, CYAN_DEEP, 7)

    s.save("02_sbs_cycle.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_four_normal_red_lights.py — 生成 09_four_normal_red_lights.svg
（FIG-U04-09：四大无需处理的正常红灯，重绘 F06-03 合规版【判读/易错】）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-09（P23，cols 一栏，viewBox 800×700）。
2×2 卡片：转录组开头波动 / 转录组高表达重复 / 扩增子保守区 / 甲基化转化成功，
每张卡右下角绿色对勾印章（不动手/不去重/不修剪/不动手的处置由 deck 要点承载）。
依据：教材 §6.4.3 L84–112；W14 显式纠偏（报红 ≠ 实验成功，仍需对照核查）。
图内汉字 28，红色 0 处。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 09_four_normal_red_lights.py
"""
from svghelp import *


def card(s, x, y, title, icon):
    s.rect(x, y, 350, 280, PANEL, rx=16)
    s.rect(x, y, 350, 280, WHITE, stroke=PANEL, sw=2, rx=16)
    s.text(x + 175, y + 56, title, 30, BLUE, "middle", "bold")
    cx, cy = x + 175, y + 152
    if icon == "wobble":      # 转录组开头波动：5′ 整齐 → 波动
        for r in range(3):
            yy = cy - 40 + r * 36
            s.rect(cx - 110, yy, 26, 26, BLUE, rx=4)
            for k in range(6):
                wob = [0, 10, -6, 12, -10, 6][k]
                s.rect(cx - 76 + k * 38, yy + wob, 32, 26,
                       [GREEN, CYAN, ORANGE, PURPLE][(r + k) % 4], rx=4)
    elif icon == "stack":     # 高表达重复：大量相同序列堆叠
        for r in range(6):
            s.rect(cx - 120, cy - 60 + r * 22, 240, 16, CYAN if r % 2 else BLUE,
                   rx=6)
    elif icon == "identical":  # 扩增子保守区：两条完全相同
        for r in range(2):
            yy = cy - 34 + r * 52
            for k in range(8):
                s.rect(cx - 128 + k * 32, yy, 26, 26, GREEN, rx=4)
    elif icon == "conv":      # 甲基化转化：C → T
        s.rect(cx - 128, cy - 30, 60, 60, CYAN, rx=10)
        s.text(cx - 98, cy + 14, "C", 34, WHITE, "middle", "bold")
        s.arrow(cx - 52, cy, cx + 12, cy, GRAY, sw=6)
        s.rect(cx + 24, cy - 30, 60, 60, PURPLE, rx=10)
        s.text(cx + 54, cy + 14, "T", 34, WHITE, "middle", "bold")
    s.check(x + 292, y + 232, 32, GREEN)


def main():
    s = SVG(800, 700)
    card(s, 40, 60, "转录组开头波动", "wobble")
    card(s, 410, 60, "转录组高表达重复", "stack")
    card(s, 40, 370, "扩增子保守区", "identical")
    card(s, 410, 370, "甲基化转化成功", "conv")
    s.save("09_four_normal_red_lights.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

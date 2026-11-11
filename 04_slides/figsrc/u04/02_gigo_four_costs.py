#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_gigo_four_costs.py — 生成 02_gigo_four_costs.svg（FIG-U04-02：垃圾进垃圾出四项代价）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-02（P10，cols 一栏，viewBox 800×700）。
2×2 卡片：接头致软剪切（深蓝）、低 Q 制造假变异（红）、
错误碱基造假分支（橙）、过度修剪丢信号（红）。
依据：教材 §6.4.1 L60–64、§6.4.4 L138–140。图内汉字 28，红色 2 处。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 02_gigo_four_costs.py
"""
from svghelp import *


def card(s, x, y, color, title, sub, icon):
    s.rect(x, y, 340, 260, WHITE, stroke=color, sw=6, rx=16)
    s.rect(x, y, 340, 64, color, rx=16)
    s.rect(x, y + 32, 340, 32, color)  # 补平标题带下缘圆角
    s.text(x + 170, y + 44, title, 32, WHITE, "middle", "bold")
    cx, cy = x + 170, y + 150
    if icon == "scissors":  # 剪刀：两条交叉刃 + 轴点
        s.line(cx - 52, cy - 34, cx + 44, cy + 30, color, sw=9, cap="round")
        s.line(cx - 44, cy + 34, cx + 52, cy - 30, color, sw=9, cap="round")
        s.circle(cx - 58, cy - 40, 14, WHITE, stroke=color, sw=7)
        s.circle(cx - 58, cy + 40, 14, WHITE, stroke=color, sw=7)
    elif icon == "snp":  # 假变异：梯带上的爆点
        s.line(cx - 60, cy - 24, cx + 60, cy - 24, color, sw=6)
        s.line(cx - 60, cy + 24, cx + 60, cy + 24, color, sw=6)
        for dx in (-36, -12, 12, 36):
            s.line(cx + dx, cy - 24, cx + dx, cy + 24, color, sw=4)
        pts = []
        for k in range(16):
            ang = math.pi * k / 8
            r = 34 if k % 2 == 0 else 14
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        s.polygon(pts, color)
        s.circle(cx, cy, 9, WHITE)
    elif icon == "branch":  # de Bruijn 分叉泡
        s.polyline([(cx - 62, cy + 30), (cx - 18, cy + 30), (cx + 4, cy - 4)],
                   color, sw=8)
        s.polyline([(cx - 18, cy + 30), (cx + 4, cy + 34), (cx + 34, cy + 34)],
                   color, sw=8)
        s.polyline([(cx + 4, cy - 4), (cx + 34, cy - 4), (cx + 62, cy - 4)],
                   color, sw=8)
        s.polyline([(cx + 34, cy + 34), (cx + 62, cy + 34)], color, sw=8)
    elif icon == "cliff":  # 断崖缩水
        s.rect(cx - 60, cy - 40, 34, 90, color)
        s.rect(cx - 16, cy - 8, 34, 58, color)
        s.rect(cx + 28, cy + 24, 34, 26, color)
        s.polygon([(cx + 70, cy - 44), (cx + 88, cy - 44), (cx + 79, cy - 24)],
                  color)
    s.text(cx, y + 232, sub, 30, GRAY, "middle")


def main():
    s = SVG(800, 700)
    card(s, 40, 70, BLUE, "接头致软剪切", "soft clipping", "scissors")
    card(s, 420, 70, RED, "低 Q 制造假变异", "false SNP", "snp")
    card(s, 40, 370, ORANGE, "错误碱基造假分支", "false branch", "branch")
    card(s, 420, 370, RED, "过度修剪丢信号", "signal loss", "cliff")
    s.save("02_gigo_four_costs.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

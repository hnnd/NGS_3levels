#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-09 TPM 组成性闭合：防卫基因暴涨制造假全基因组下调。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-09；配色：spec.md §2。
依据：教材 §14.4.3，讲义 ④4.2。饼图份额为概念示意（总和恒 10^6）。"""
import math

from svghelp import *


def wedge(s, cx, cy, r, a1, a2, fill):
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(
        math.radians(a1))
    x2, y2 = cx + r * math.cos(math.radians(a2)), cy + r * math.sin(
        math.radians(a2))
    large = 1 if (a2 - a1) % 360 > 180 else 0
    s.path(f"M {cx} {cy} L {x1:.1f} {y1:.1f} A {r} {r} 0 {large} 1 "
           f"{x2:.1f} {y2:.1f} Z", None, fill=fill)
    s.circle(cx, cy, r, "none", PAPER, 3)


s = SVG()

s.label(400, 50, ["总和恒定闭合"], 32, BLUE, weight="bold")

# ---- 左：基线饼图 ----
cx1, cy1, r = 200, 280, 150
baseline = [(0, 50, BLUE), (50, 100, CYAN), (100, 150, GREEN),
            (150, 200, BLUE), (200, 245, CYAN), (245, 290, GREEN),
            (290, 360, BLUE_TINT)]
for a1, a2, c in baseline:
    wedge(s, cx1, cy1, r, a1, a2, c)
s.circle(cx1, cy1, 74, PAPER)
s.text(cx1, cy1 + 10, "Σ = 10^6", 32, INK, "middle", "bold")
s.text(cx1, 492, "基线", 30, GRAY, "middle")

s.arrow(390, 280, 450, 280, GRAY, 7, 18)

# ---- 右：防卫暴涨饼图 ----
cx2, cy2 = 600, 280
defense = [(0, 108, ORANGE), (108, 170, GREEN), (170, 225, BLUE),
           (225, 275, CYAN), (275, 320, BLUE), (320, 360, GREEN_TINT)]
for a1, a2, c in defense:
    wedge(s, cx2, cy2, r, a1, a2, c)
s.circle(cx2, cy2, 74, PAPER)
s.text(cx2, cy2 + 10, "Σ = 10^6", 32, INK, "middle", "bold")
s.text(cx2, 492, "侵染后", 30, GRAY, "middle")
s.text(775, 200, "防卫基因", 30, ORANGE, "end", "bold")
s.text(775, 236, "~30%", 32, ORANGE, "end", "bold")

# 标注
s.label(600, 556, ["少数防卫暴涨"], 30, INK)
s.label(200, 556, ["强行压低其余基因"], 30, INK)

# ---- 红色警示：假下调报告 ----
s.rect(90, 600, 620, 88, RED_TINT, RED, 6, rx=14)
s.text(400, 642, "假全基因组下调", 32, INK, "middle", "bold")
s.text(400, 674, "全基因组下调（假象）", 30, GRAY, "middle")

s.save("09_tpm_compositionality.svg")

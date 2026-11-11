#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-20 ORA 背景基因集 universe 分母虚高致 p 偏小。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-20；配色：spec.md §2。
依据：教材 §14.4.8。N=30000 / 18670 为合成算例设定（demos/ch14_ora_background.py）。"""
from svghelp import *

s = SVG()

# ---- 嵌套圈：错误背景 vs 正确背景 ----
cx, cy = 250, 340
s.circle(cx, cy, 200, BLUE_TINT, BLUE, 5)
s.circle(cx, cy, 128, GREEN_TINT, GREEN, 5)
s.text(cx, cy - 168, "全注释基因", 30, BLUE, "middle", "bold")
s.text(cx, cy - 136, "N = 30,000", 30, BLUE, "middle")
s.text(cx, cy - 10, "被检验基因", 30, GREEN, "middle", "bold")
s.text(cx, cy + 28, "N = 18,670", 30, GREEN, "middle")
# 命中点
import math
hits = [(cx - 40 + i * 36, cy + 66 + (i % 2) * 30) for i in range(4)]
for hx, hy in hits:
    s.circle(hx, hy, 11, ORANGE)
s.text(cx, cy + 150, "命中 k", 30, ORANGE, "middle", "bold")

# ---- 机制式 ----
s.rect(490, 120, 290, 120, WHITE, BLUE, 5, rx=12)
s.text(635, 166, "E[X] = n · K / N", 32, INK, "middle", "bold")
s.text(635, 214, "N ↑ → 期望命中 ↓", 30, GRAY, "middle")
s.arrow(455, 340, 485, 220, GRAY, 5, 13)

# ---- 结果 ----
s.rect(490, 300, 290, 120, RED_TINT, RED, 5, rx=12)
s.text(635, 346, "同一 k 显得更罕见", 30, INK, "middle", "bold")
s.text(635, 394, "p 值被压低", 30, GRAY, "middle")
s.text(620, 470, "BgRatio 0.2331 vs 0.3746", 30, INK, "middle", "bold")

# ---- 中文标注 ----
s.label(400, 60, ["全注释分母虚高"], 30, BLUE)
s.label(400, 596, ["检验有效真背景"], 30, GREEN)
s.label(400, 640, ["期望命中被压低"], 30, INK)
s.text(660, 640, "虚假富集", 30, RED, "middle", "bold")

s.save("20_ora_universe_bias.svg")

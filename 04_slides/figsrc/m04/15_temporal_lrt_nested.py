#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-15 时序 LRT 嵌套模型对比检验。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-15；配色：spec.md §2。
依据：教材 §14.4.6，讲义 ④4.3。"""
from svghelp import *

s = SVG()

# ---- 完整模型 ----
s.label(400, 52, ["完整模型全效应"], 30, BLUE, weight="bold")
s.rect(110, 84, 580, 128, BLUE_TINT, BLUE, 5, rx=14)
s.text(400, 126, "~ rep + time + treatment", 32, BLUE, "middle", "bold")
s.text(400, 172, "5 个系数 · 含处理动态", 30, GRAY, "middle")
# 时序轨迹
for i, c in enumerate((CYAN, CYAN_DEEP, GREEN)):
    pts = [(140 + j * 60, 268 + i * 22 - (j - 1.5) ** 2 * (8 + i * 6))
           for j in range(5)]
    s.polyline(pts, c, 5)

# ---- LRT 箭头 ----
s.arrow(400, 330, 400, 408, PURPLE, 8, 20)
s.text(430, 360, "LRT", 32, PURPLE, "start", "bold")
s.text(600, 380, "嵌套似然检验", 30, INK, "middle")

# ---- 简化模型 ----
s.label(400, 448, ["简化模型剔除处理"], 30, PURPLE, weight="bold")
s.rect(110, 478, 580, 100, PURPLE_TINT, PURPLE, 5, rx=14)
s.text(400, 520, "~ rep + time", 32, PURPLE, "middle", "bold")
s.text(400, 560, "4 个系数 · 仅时间与批次", 30, GRAY, "middle")

# ---- 检出 ----
s.rect(110, 600, 580, 84, GREEN_TINT, GREEN, 5, rx=14)
s.text(400, 638, "检出时序响应", 30, GREEN, "middle", "bold")
s.text(400, 672, "自由度 = 被剔除的列数", 30, GREEN, "middle")

s.save("15_temporal_lrt_nested.svg")

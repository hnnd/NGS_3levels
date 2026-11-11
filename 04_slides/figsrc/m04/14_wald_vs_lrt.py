#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-14 Wald 单系数检验 vs LRT 似然比检验。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-14；配色：spec.md §2。
依据：教材 §14.4.6，讲义 ④4.3。曲线为概念形态示意。"""
import math

from svghelp import *

s = SVG()

# ---- 左：Wald ----
s.label(200, 52, ["单变量系数显著性"], 30, BLUE, weight="bold")
s.rect(30, 84, 340, 420, WHITE, BLUE, 5, rx=14)
s.text(200, 132, "Wald 检验", 32, BLUE, "middle", "bold")
s.text(200, 176, "z = β / SE", 34, INK, "middle", "bold")
# 正态曲线
cx, base = 200, 400
pts = []
for i in range(81):
    x = i / 80 * 5 - 2.5
    y = math.exp(-x * x / 2)
    pts.append((cx + x * 52, base - y * 200))
s.curve(pts, CYAN, 6)
s.line(cx - 140, base, cx + 140, base, BLUE, 4)
s.line(cx, base, cx, base - 215, PANEL, 3, dash="8 8")
s.circle(cx + 1.4 * 52, base - math.exp(-0.98) * 200, 10, BLUE)
s.text(cx + 1.4 * 52, base + 40, "z", 30, BLUE, "middle", "bold")
s.text(200, 474, "单个系数 ≠ 0 ？", 30, GRAY, "middle")

# ---- 右：LRT ----
s.label(600, 52, ["似然比嵌套比较"], 30, PURPLE, weight="bold")
s.rect(430, 84, 340, 420, WHITE, PURPLE, 5, rx=14)
s.text(600, 132, "LRT", 32, PURPLE, "middle", "bold")
s.rect(470, 160, 260, 78, PURPLE_TINT, PURPLE, 4, rx=10)
s.text(600, 192, "完整模型", 30, PURPLE, "middle", "bold")
s.text(600, 226, "5 个系数", 30, INK, "middle")
s.rect(480, 266, 240, 70, WHITE, PURPLE, 4, rx=10)
s.text(600, 296, "简化模型", 30, PURPLE, "middle", "bold")
s.text(600, 326, "rep + time", 30, INK, "middle")
s.text(600, 388, "ΔDeviance ~ χ²", 34, INK, "middle", "bold")
s.text(600, 474, "被剔除的项重要吗？", 30, GRAY, "middle")

# ---- 底部分工 ----
s.label(230, 580, ["剔除多项检验"], 30, INK)
s.label(570, 580, ["时序整体响应"], 30, GREEN)
s.text(400, 652, "Wald：两组对比 · LRT：联合/时序", 30,
       GRAY, "middle")

s.save("14_wald_vs_lrt.svg")

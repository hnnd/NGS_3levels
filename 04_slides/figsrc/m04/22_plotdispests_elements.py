#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-22 plotDispEsts() 离散度收缩四图元判读。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-22；配色：spec.md §2。
依据：教材 §14.4.9，讲义 ⑥6.3。点云为概念形态示意（均值-离散度关系）。"""
import math

from svghelp import *

s = SVG()

# ---- 坐标系（双对数概念轴）----
x0, y0, w, h = 90, 110, 620, 420
s.rect(x0, y0, w, h, WHITE, BLUE, 5, rx=8)
s.text(x0 + w / 2, y0 + h + 56, "归一化计数均值（log）", 30, GRAY,
       "middle")
s.text(x0 + 6, y0 - 12, "离散度（log）", 30, GRAY, "start")

# 趋势线（红）：随均值下降
trend = [(x0 + 40 + i * 60, y0 + 90 + i * 22) for i in range(10)]
s.curve(trend, RED, 6)

# 单基因 MLE 黑点：低均值区极宽
pts_black = [(120, 180), (150, 300), (170, 230), (200, 360), (230, 260),
             (260, 410), (300, 300), (340, 200), (380, 170), (430, 160),
             (480, 150), (540, 145), (600, 140), (650, 138)]
for px, py in pts_black:
    s.circle(px, py, 8, INK)

# 收缩蓝点：向红线收拢
pts_cyan = [(120, 200), (150, 240), (170, 230), (200, 280), (230, 265),
            (260, 300), (300, 290), (340, 230), (380, 200), (430, 185),
            (480, 170), (540, 160), (600, 152), (650, 146)]
for px, py in pts_cyan:
    s.circle(px, py, 8, CYAN_DEEP)
# 收缩方向细箭头（取 3 个示例）
for (bx, by), (cx2, cy2) in zip(pts_black[:3], pts_cyan[:3]):
    s.arrow(bx + 10, by - 6, cx2 - 10, cy2 + 4, PANEL, 3, 9)

# 离群基因（橙圈，不收缩）
s.circle(430, 320, 15, "none", ORANGE, 6)
s.circle(430, 320, 8, INK)
s.text(478, 296, "离群 · 不收缩", 30, ORANGE, "start", "bold")

# 图例
s.circle(120, 612, 9, INK)
s.text(140, 622, "单基因估计点", 30, INK, "start")
s.line(340, 612, 390, 612, RED, 6)
s.text(402, 622, "拟合红色趋势线", 30, INK, "start")
s.circle(120, 658, 9, CYAN_DEEP)
s.text(140, 668, "经验贝叶斯收缩", 30, INK, "start")
s.circle(560, 658, 12, "none", ORANGE, 5)
s.text(582, 668, "离群基因不收缩", 30, INK, "start")

s.save("22_plotdispests_elements.svg")

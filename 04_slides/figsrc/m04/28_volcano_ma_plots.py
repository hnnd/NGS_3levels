#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-28 火山图与 MA 图判读双视角。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-28；配色：spec.md §2。
依据：教材 §14.4.9，讲义 ⑥6.4。散点为概念形态示意。"""
import math

from svghelp import *

s = SVG()

# ---- 左：火山图 ----
s.label(200, 52, ["火山图对称双翼"], 30, BLUE, weight="bold")
s.rect(40, 90, 320, 380, WHITE, BLUE, 5, rx=12)
# 对称双翼散点
pts_l = [(110, 380), (130, 350), (150, 330), (120, 310), (160, 300),
         (140, 280), (170, 260), (150, 240)]
pts_r = [(330 - x + 110, y) for x, y in pts_l]
for x, y in pts_l + pts_r:
    sig = y < 300
    s.circle(x, y, 7, GREEN if sig else CYAN)
s.line(200, 440, 200, 120, PANEL, 3, dash="8 8")
s.text(200, 506, "log2FC", 30, GRAY, "middle")
s.text(66, 130, "-log10(padj)", 30, GRAY, "start")
s.text(200, 548, "显著基因两翼展开", 30, INK, "middle", "bold")

# ---- 右：MA 图 ----
s.label(600, 52, ["高表达贴近零轴"], 30, BLUE, weight="bold")
s.rect(440, 90, 320, 380, WHITE, BLUE, 5, rx=12)
# 漏斗：离零轴越远（低表达）方差越大
for i in range(30):
    x = 470 + (i * 47 % 250)
    dev = (abs(x - 600) / 125) ** 1.3 * 120 + 18
    y = 255 + ((i * 61 % 100) / 100 * 2 - 1) * dev
    s.circle(x, y, 6, GREEN if abs(y - 255) < 35 else CYAN)
s.line(460, 255, 740, 255, PANEL, 3, dash="8 8")
s.text(600, 506, "log2(baseMean)", 30, GRAY, "middle")
s.text(466, 130, "log2FC", 30, GRAY, "start")
s.text(600, 548, "漏斗形方差收敛", 30, INK, "middle", "bold")

# 底部
s.text(400, 622, "火山图： 对称双翼 · MA： 高表达贴零轴", 30,
       GRAY, "middle")
s.text(400, 668, "单翼缺失 ／ 高表达偏移 → 查设计", 30,
       GRAY, "middle")

s.save("28_volcano_ma_plots.svg")

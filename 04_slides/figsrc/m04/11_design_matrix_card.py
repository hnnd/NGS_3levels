#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-11 PRJDB36269 2×3×2 设计网格与自由度账。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-11；配色：spec.md §2。
依据：教材 §14.1 / §14.4.5；12 样本、5 系数、残差自由度 7 为手算（1+1+2+1=5，12−5=7）。"""
from svghelp import *

s = SVG()

s.label(260, 50, ["十二样本设计网格"], 30, BLUE, weight="bold")
s.label(640, 50, ["兼作批次区组"], 30, PURPLE, weight="bold")

# ---- 设计网格：行 = 处理（K / N），列 = time 30/60/120 × rep A/B ----
x0, y0, cw, chh = 150, 96, 84, 80
for t, lab in enumerate(["30", "60", "120"]):
    s.text(x0 + t * 2 * cw + cw, y0 - 18, lab + " min", 30, GRAY, "middle")
s.text(x0 - 16, y0 + chh / 2 + 10, "K", 32, BLUE, "end", "bold")
s.text(x0 - 16, y0 + 3 * chh / 2 + 10, "N", 32, CYAN_DEEP, "end", "bold")
for r in range(2):
    for c in range(6):
        x = x0 + c * cw
        y = y0 + r * chh
        batch = c % 2                      # rep A / B 兼批次
        fill = BLUE_TINT if r == 0 else GREEN_TINT
        stroke = BLUE if batch == 0 else PURPLE
        s.rect(x + 5, y + 5, cw - 10, chh - 10, fill, stroke, 5, rx=10)
        s.text(x + cw / 2, y + chh / 2 + 11, "A" if batch == 0 else "B",
               32, stroke, "middle", "bold")
# rep 图例
s.rect(150, 296, 30, 30, WHITE, BLUE, 4, rx=6)
s.text(196, 322, "rep A ／批次 A", 30, GRAY, "start")
s.rect(470, 296, 30, 30, WHITE, PURPLE, 4, rx=6)
s.text(516, 322, "rep B ／批次 B", 30, GRAY, "start")

# ---- 待估系数账 ----
s.label(400, 388, ["待估参数五个"], 30, INK, weight="bold")
s.rect(60, 420, 330, 64, WHITE, BLUE, 4, rx=12)
s.text(225, 464, "1 + 1 + 2 + 1 = 5", 32, BLUE, "middle", "bold")
s.rect(410, 420, 340, 64, WHITE, BLUE, 4, rx=12)
s.text(580, 464, "β0 + rep + time + trt", 30, BLUE, "middle", "bold")

# ---- 残差自由度 ----
s.label(400, 542, ["残差自由度七"], 30, GREEN, weight="bold")
s.rect(60, 574, 690, 64, GREEN_TINT, GREEN, 5, rx=12)
s.text(400, 618, "12 − 5 = 7", 32, GREEN, "middle", "bold")
s.text(400, 668, "趋势可拟合 · 单基因仍噪 → 跨基因收缩", 30, GRAY, "middle")

s.save("11_design_matrix_card.svg")

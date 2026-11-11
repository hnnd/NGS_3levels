#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-10 DESeq2 中位数比值归一化 median-of-ratios。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-10；配色：spec.md §2。
依据：教材 §14.4.3，讲义 ④4.3。迷你矩阵数字为概念示意。"""
from svghelp import *

s = SVG()

# ---- ① 跨样本几何均值 → 伪参考 ----
s.label(190, 50, ["跨样本几何均值"], 30, BLUE, weight="bold")
s.text(330, 92, "伪参考", 30, BLUE, "middle", "bold")
counts = [[320, 640, 160, 80],
          [100, 50, 200, 400],
          [900, 450, 225, 112],
          [64, 128, 256, 512]]
x0, y0, cw, ch = 50, 116, 68, 44
for i, row in enumerate(counts):
    for j, v in enumerate(row):
        s.rect(x0 + j * cw, y0 + i * ch, cw, ch,
               WHITE if (i + j) % 2 == 0 else PAPER, BLUE, 2)
        s.text(x0 + j * cw + cw / 2, y0 + i * ch + 32, str(v), 30, INK,
               "middle")
s.text(x0 - 14, y0 + 2 * ch + 32, "K", 30, GRAY, "end")
s.arrow(x0 + 4 * cw + 8, y0 + 2 * ch, x0 + 4 * cw + 56, y0 + 2 * ch, GRAY, 5,
        13)
geo = [180, 80, 270, 128]
for i, v in enumerate(geo):
    s.rect(x0 + 4 * cw + 60, y0 + i * ch, 72, ch, BLUE_TINT, BLUE, 3)
    s.text(x0 + 4 * cw + 96, y0 + i * ch + 32, str(v), 30, BLUE, "middle",
           "bold")

# ---- ② 逐基因求比值 ----
s.label(600, 50, ["逐基因求比值"], 30, BLUE, weight="bold")
s.text(600, 92, "K / 几何均值", 30, GRAY, "middle")
ratios = [(500, 90, BLUE), (555, 200, CYAN), (610, 320, BLUE),
          (665, 110, CYAN), (528, 350, ORANGE), (638, 380, ORANGE)]
base_y = 560
for x, h, c in ratios:
    s.rect(x, base_y - h, 36, h, c, None)
s.line(450, base_y, 740, base_y, BLUE, 4)
s.text(600, 596, "逐基因比值", 30, GRAY, "middle")

# ---- ③ 中位数锁定 size factor ----
s.arrow(260, 610, 260, 648, GREEN, 6, 15)
s.rect(40, 630, 440, 60, GREEN_TINT, GREEN, 5, rx=12)
s.text(260, 672, "中位数锁定文库因子", 30, GREEN, "middle", "bold")
# 极端比值落在两端，被中位数天然过滤
s.rect(566, 640, 24, 24, ORANGE, None)
s.text(604, 664, "抵御极端波动", 30, INK, "start")

s.save("10_median_of_ratios.svg")

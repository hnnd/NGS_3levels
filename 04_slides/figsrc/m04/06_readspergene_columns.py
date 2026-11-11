#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-06 STAR ReadsPerGene.out.tab 四列结构与文库选列规则。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-06；配色：spec.md §2。
依据：教材 §14.4.2，讲义 ⑤5.3。表内数字为结构示意（schematic）。"""
from svghelp import *

s = SVG()

s.label(140, 56, ["四列结构"], 32, BLUE, weight="bold")
s.text(430, 56, "无链 · 正向 · 反向", 30, GRAY, "middle")

# ---- 核心表格：4 列 × 3 行 ----
x0, y0 = 90, 96
col_w = [220, 140, 140, 140]
headers = ["基因标识", "U", "ISF", "ISR"]
rows = [["gene_A", "512", "305", "198"],
        ["gene_B", "1220", "640", "702"],
        ["gene_C", "36", "18", "15"]]
tw = sum(col_w)
s.rect(x0, y0, tw, 64, BLUE_TINT, BLUE, 4)
xx = x0
for w, htxt in zip(col_w, headers):
    s.text(xx + w / 2, y0 + 43, htxt, 30, BLUE, "middle", "bold")
    xx += w
for r, row in enumerate(rows):
    yy = y0 + 64 + r * 60
    fill = WHITE if r % 2 == 0 else PAPER
    s.rect(x0, yy, tw, 60, fill, BLUE, 3)
    xx = x0
    for w, val in zip(col_w, row):
        s.text(xx + w / 2, yy + 41, val, 30, INK, "middle")
        xx += w
xx = x0
for w in col_w[:-1]:
    xx += w
    s.line(xx, y0, xx, y0 + 64 + 180, BLUE, 3)

# 第 4 列高亮（ISR = 本课 dUTP 链特异性常用列）
s.rect(x0 + col_w[0] + col_w[1] + col_w[2], y0 - 10,
       col_w[3], 64 + 180 + 20, "none", GREEN, 6)

# ---- 选列规则：箭头 + 交错高度标签 ----
col_c = [x0 + sum(col_w[:i]) + col_w[i] / 2 for i in range(4)]
s.arrow(col_c[1], 356, col_c[1], 406, GREEN, 5, 13)
s.text(col_c[1], 444, "无链选第二列", 30, INK, "middle")
s.arrow(col_c[2], 356, col_c[2], 470, GREEN, 5, 13)
s.text(col_c[2], 508, "正向选第三列", 30, INK, "middle")
s.arrow(col_c[3], 356, col_c[3], 534, GREEN, 5, 13)
s.text(col_c[3], 572, "反向选第四列", 30, INK, "middle")

# ---- 警示：选错列静默全错 ----
s.rect(70, 610, 660, 72, RED_TINT, RED, 6, rx=14)
s.path("M 94 626 L 118 650 M 118 626 L 94 650", RED, 6)
s.text(140, 642, "选错列 → 只剩反义噪声", 30, INK, "start")
s.text(140, 672, "表面正常 · 不报错", 30, INK, "start")

s.save("06_readspergene_columns.svg")

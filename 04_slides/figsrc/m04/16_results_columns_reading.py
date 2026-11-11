#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-16 results() 六列判读路径。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-16；配色：spec.md §2。
依据：教材 §14.4.6，讲义 ④4.4。六列顺序为 DESeq2 results() 输出结构。"""
from svghelp import *

s = SVG()

cols = ["baseMean", "pvalue", "padj", "log2FC", "lfcSE", "stat"]
cws = [150, 117, 117, 117, 117, 117]
x0, y0 = 20, 110
edges = [x0]
for w in cws:
    edges.append(edges[-1] + w)
# 表头
s.rect(x0, y0, edges[-1] - x0, 64, BLUE, None)
for i, name in enumerate(cols):
    s.text((edges[i] + edges[i + 1]) / 2, y0 + 43, name, 30, WHITE, "middle",
           "bold")
# 数据格（示意）
vals = [["312.5", "0.031", "0.104", "1.42", "0.31", "4.58"],
        ["58.0", "0.002", "0.014", "-2.10", "0.44", "-4.77"],
        ["1247.3", "0.640", "0.812", "0.08", "0.17", "0.47"]]
for r, row in enumerate(vals):
    for c, v in enumerate(row):
        fill = WHITE
        if c == 2:
            fill = GREEN_TINT
        elif c == 3:
            fill = ORANGE_TINT
        s.rect(edges[c] + 3, y0 + 70 + r * 62, cws[c] - 6, 56, fill,
               PANEL, 2)
        s.text((edges[c] + edges[c + 1]) / 2, y0 + 70 + r * 62 + 39, v, 30,
               INK, "middle")

# 判读顺序标注
padj_c = (edges[2] + edges[3]) / 2
lfc_c = (edges[3] + edges[4]) / 2
s.circle(padj_c, 460, 27, GREEN)
s.text(padj_c, 471, "1", 36, WHITE, "middle", "bold")
s.circle(lfc_c, 460, 27, ORANGE)
s.text(lfc_c, 471, "2", 36, WHITE, "middle", "bold")
s.arrow(padj_c + 32, 460, lfc_c - 32, 460, GRAY, 5, 12)

# 列注（两行交错防重叠）
s.text((edges[0] + edges[1]) / 2, 548, "基线丰度", 30, BLUE, "middle", "bold")
s.text(padj_c, 548, "校正第一判据", 30, GREEN, "middle", "bold")
s.text((edges[5] + edges[6]) / 2, 548, "统计量支撑", 30, BLUE, "middle",
       "bold")
s.text((edges[1] + edges[2]) / 2, 592, "原始检验", 30, BLUE, "middle", "bold")
s.text(lfc_c, 592, "效应量定方向", 30, ORANGE, "middle", "bold")

s.text(400, 668, "先看显著性 (padj)，再定方向 (log2FC)", 30,
       GRAY, "middle")

s.save("16_results_columns_reading.svg")

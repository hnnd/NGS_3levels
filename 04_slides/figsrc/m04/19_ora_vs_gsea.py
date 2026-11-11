#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-19 ORA 硬阈值超几何 vs GSEA 连续排序富集。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-19；配色：spec.md §2。
依据：教材 §14.4.8，讲义 ④4.5。曲线为概念形态示意。"""
from svghelp import *

s = SVG()

# ---- 左：ORA ----
s.label(200, 52, ["硬阈值切分名单"], 30, BLUE, weight="bold")
# 排序条形 + 阈值线
x0, y0 = 40, 110
for i in range(16):
    h = 40 + (i * 37 % 90)
    col = CYAN if i < 5 else PANEL
    s.rect(x0 + i * 21, y0 + 130 - h, 16, h, col, None)
s.line(x0 + 5 * 21 - 3, y0 + 20, x0 + 5 * 21 - 3, y0 + 140, ORANGE, 5,
       dash="10 8")
s.text(x0 + 5 * 21 - 3, y0 + 152, "阈值", 30, ORANGE, "middle")
s.text(200, 306, "前 5 个 → 差异名单", 30, GRAY, "middle")
# 超几何
s.rect(45, 340, 310, 110, BLUE_TINT, BLUE, 5, rx=12)
s.text(200, 386, "超几何检验", 30, BLUE, "middle", "bold")
s.text(200, 428, "过度代表分析", 30, GRAY, "middle")
s.text(200, 500, "未达标基因被丢弃", 30, GRAY, "middle")

# ---- 右：GSEA ----
s.label(600, 52, ["全基因连续排序"], 30, GREEN, weight="bold")
# 排序条形（连续）
for i in range(16):
    h = 40 + (i * 37 % 90)
    col = GREEN if i in (2, 3, 4, 11, 12) else CYAN
    s.rect(440 + i * 21, y0 + 130 - h, 16, h, col, None)
s.text(600, 296, "连续排序", 30, GRAY, "middle")
# ES 曲线
pts = [(445 + i * 22, 470 - v) for i, v in
       enumerate([0, 12, 30, 55, 70, 62, 50, 38, 30, 24, 20, 30, 48, 60, 52, 40])]
s.curve(pts, GREEN, 6)
s.line(440, 470, 790, 470, BLUE, 4)
s.text(600, 380, "ES 峰值", 30, GREEN, "middle", "bold")
s.text(200, 580, "ORA： 名单 → 超几何", 30, INK, "middle")
s.text(600, 580, "GSEA： 排序 → ES 曲线", 30, GREEN, "middle")
s.text(600, 640, "两端富集无截断", 30, GREEN, "middle", "bold")
s.text(200, 640, "超几何过度代表", 30, BLUE, "middle", "bold")

s.save("19_ora_vs_gsea.svg")

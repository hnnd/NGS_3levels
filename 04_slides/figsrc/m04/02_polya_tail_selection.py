#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-02 polyA 富集分流与降解样本 3' 偏倚。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-02；配色：spec.md §2。
依据：教材 §14.4.1，讲义 ④4.1。"""
from svghelp import *

s = SVG()

s.label(470, 52, ["捕获带尾转录本"], 32, BLUE, weight="bold")

# ---- 上部：oligo-dT 磁珠分流 ----
def rna(x, y, tail, lab, tail_color=GREEN):
    s.line(x, y, x + 100, y, CYAN_DEEP, 5, cap="round")
    if tail:
        s.text(x + 108, y + 10, tail, 30, tail_color, "start", "bold")
    s.text(x, y - 12, lab, 30, GRAY, "start")

rna(30, 110, "AAAA", "mRNA")
rna(30, 180, "AAAA", "lncRNA")

# 磁珠柱
for i in range(5):
    for j in range(2):
        s.circle(258 + j * 34, 96 + i * 46, 15, CYAN, BLUE, 4)
s.rect(238, 66, 74, 250, "none", BLUE, 4, rx=30)

# 带尾 RNA 穿过磁珠 → 保留
for yy in (110, 180):
    s.line(130, yy, 246, yy, GREEN, 5)
    s.line(312, yy, 396, yy, GREEN, 5)
    s.arrow(396, yy, 438, yy, GREEN, 5, 14)
# 保留管 + 标签
s.polygon([(438, 96), (534, 96), (516, 250), (456, 250)], GREEN_TINT, GREEN, 5)
s.text(596, 136, "polyA+", 30, GREEN, "middle", "bold")
s.text(596, 172, "保留", 30, GREEN, "middle", "bold")

# 无尾 RNA 被挡下 → 丢失
s.line(30, 300, 246, 300, ORANGE, 5, cap="round")
s.text(30, 238, "组蛋白 mRNA", 30, GRAY, "start")
s.text(30, 270, "原核 RNA", 30, GRAY, "start")
s.polyline([(246, 300), (300, 300), (300, 326)], ORANGE, 5)
s.arrow(300, 326, 300, 356, ORANGE, 5, 14)
s.polygon([(272, 360), (328, 360), (318, 404), (282, 404)], ORANGE_TINT, ORANGE, 5)
s.line(278, 372, 322, 372, ORANGE, 4)
s.line(280, 386, 320, 386, ORANGE, 4)
s.label(400, 384, ["丢失无尾分子"], 30, ORANGE, anchor="start")

# ---- 下部：降解样本 3' 偏倚 ----
s.label(400, 452, ["降解样本严重偏向末端"], 32, BLUE, weight="bold")
# 基因轴
s.line(50, 504, 750, 504, BLUE, 5)
for x0 in (150, 260, 370):
    s.rect(x0, 490, 60, 28, BLUE, None)
s.text(60, 484, "5'", 30, GRAY, "start", "bold")
s.text(726, 484, "3'", 30, GRAY, "end", "bold")
s.text(400, 548, "poly(A) 尾", 30, GRAY, "middle")
# 断裂片段：5' 端丢失（画 ✗ 不用字形）
for x in (90, 140, 190, 240):
    s.line(x, 591, x + 26, 591, PANEL, 8, cap="round")
    s.line(x + 8, 600, x + 18, 610, ORANGE, 4)
    s.line(x + 18, 600, x + 8, 610, ORANGE, 4)
# 3' 端片段被捕获
for x in (560, 610, 660, 700):
    s.line(x, 591, x + 30, 591, CYAN_DEEP, 8, cap="round")
s.text(676, 622, "AAAA", 30, GREEN, "middle", "bold")
# 覆盖度曲线（红）：向 3' 陡增
s.curve([(60, 668), (200, 664), (340, 654), (480, 630), (600, 592),
         (700, 556)], RED, 6)
s.polyline([(60, 668), (200, 664), (340, 654), (480, 630), (600, 592),
            (700, 556), (700, 668), (60, 668)], RED_TINT, 0, fill=RED_TINT)
s.text(48, 644, "覆盖度", 30, RED, "start")

s.save("02_polya_tail_selection.svg")

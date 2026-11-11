#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-35 两个收缩对比：离散度收缩（改检验）vs lfcShrink（不改 p）。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-35；配色：spec.md §2。
依据：教材 §14.4.6，讲义 ⑦-4。"""
from svghelp import *

s = SVG()

# ---- ① 离散度收缩 ----
s.rect(30, 80, 360, 400, WHITE, BLUE, 5, rx=14)
s.text(210, 126, "① 离散度收缩", 30, BLUE, "middle", "bold")
s.text(210, 174, "发生在建模阶段", 30, GRAY, "middle")
# α 收缩示意
s.text(210, 224, "逐基因 α → 收缩", 30, INK, "middle", "bold")
s.line(80, 260, 340, 260, BLUE, 4)
for px, py in ((110, 320), (150, 300), (190, 330), (230, 310), (270, 325)):
    s.circle(px, py, 9, INK)
    s.arrow(px, py - 10, px, 272, PANEL, 4, 10)
for px in (110, 150, 190, 230, 270):
    s.circle(px, 262, 7, CYAN_DEEP)
s.text(210, 380, "改变方差估计", 30, GRAY, "middle")
s.text(210, 424, "→ Wald 与 p 值改变", 30, BLUE, "middle", "bold")
s.label(210, 516, ["离散度收缩改方差"], 30, INK)
s.label(210, 580, ["直接改检验值"], 30, BLUE)

# ---- ② lfcShrink ----
s.rect(410, 80, 360, 400, WHITE, GREEN, 5, rx=14)
s.text(590, 126, "② lfcShrink (apeglm)", 30, GREEN, "middle", "bold")
s.text(590, 174, "发生在检验之后", 30, GRAY, "middle")
# log2FC 收缩示意
s.line(460, 260, 720, 260, GREEN, 4)
for px, py in ((490, 200), (535, 180), (580, 210), (625, 190), (670, 205)):
    s.circle(px, py, 9, INK)
    s.arrow(px, py + 10, px, 272, PANEL, 4, 10)
for px in (490, 535, 580, 625, 670):
    s.circle(px, 262, 7, GREEN)
s.text(590, 330, "只拉 log2FC 与 lfcSE", 30, GRAY, "middle")
s.text(590, 374, "压低信息不足 FC", 30, GRAY, "middle")
s.text(590, 424, "p 与 padj 不变", 30, GREEN, "middle", "bold")
s.label(590, 516, ["效应量收缩压假偏倚"], 30, INK)
s.label(590, 580, ["检验校正不变"], 30, GREEN)

# ---- 红色警示 ----
s.rect(40, 630, 720, 56, RED_TINT, RED, 5, rx=12)
s.text(400, 669, "混淆两者 → 结论颠倒", 30, RED, "middle",
       "bold")

s.save("35_two_shrinkages.svg")

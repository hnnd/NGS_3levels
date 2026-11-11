#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-04 STAR 剪接感知比对 vs Salmon 选择性准比对。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-04；配色：spec.md §2。
依据：教材 §14.4.2，讲义 ④4.2。"""
from svghelp import *

s = SVG()

# ---- 左：STAR ----
s.label(200, 50, ["跨外显子剪接比对"], 32, BLUE, weight="bold")
# 基因组轴 + 外显子
s.text(40, 92, "基因组", 30, GRAY, "start")
s.line(40, 120, 360, 120, BLUE, 5)
for x0, w in ((70, 60), (200, 60), (310, 40)):
    s.rect(x0, 106, w, 28, BLUE, None)
# 跨内含子读段：两段 + 剪接连线
s.rect(72, 172, 56, 22, CYAN, None)
s.rect(202, 172, 56, 22, CYAN, None)
s.path("M 128 183 C 160 152, 170 152, 202 183", CYAN, 5)
s.text(270, 192, "跨剪接读段", 30, CYAN_DEEP, "start")
# BAM 输出
s.rect(90, 292, 150, 92, WHITE, BLUE, 5, rx=10)
s.rect(80, 282, 150, 92, "none", BLUE, 3, rx=10)
s.text(175, 346, "BAM", 38, BLUE, "middle", "bold")
s.arrow(160, 204, 130, 276, BLUE, 6, 16)
s.label(200, 452, ["坐标输出"], 32, INK)
s.text(200, 504, "数十 GB 内存 · 较慢", 30, GRAY, "middle")

# ---- 右：Salmon ----
s.label(600, 50, ["准比对快速定量"], 32, GREEN, weight="bold")
s.text(440, 92, "转录本", 30, GRAY, "start")
s.line(440, 120, 760, 120, BLUE, 5)
for x0, w in ((470, 90), (600, 80)):
    s.rect(x0, 106, w, 28, BLUE, None)
# 读段 + k-mer 定位
s.rect(500, 162, 90, 22, GREEN, None)
for x in (505, 525, 545, 565):
    s.line(x, 162, x, 184, WHITE, 3)
s.label(665, 188, ["k-mer", "快速定位"], 30, GREEN)
s.arrow(545, 190, 545, 226, GREEN, 5, 13)
# 丰度表输出
s.rect(470, 236, 220, 150, WHITE, GREEN, 5, rx=10)
s.rect(470, 236, 220, 40, GREEN_TINT, None)
s.line(470, 276, 690, 276, GREEN, 4)
for yy in (314, 352):
    s.line(470, yy, 690, yy, PANEL, 4)
s.text(580, 265, "丰度", 30, GREEN, "middle", "bold")
for i, w in enumerate((130, 80, 150)):
    s.rect(490, 294 + i * 38, w, 14, CYAN, None)
s.label(600, 452, ["转录本丰度"], 32, INK)
s.text(600, 504, "内存轻量 · 快", 30, GRAY, "middle")

# ---- 底部提示卡 ----
s.rect(80, 580, 640, 88, WHITE, BLUE, 5, rx=14)
s.text(400, 616, "要基因组坐标 → STAR", 30, INK, "middle")
s.text(400, 652, "只做表达定量 → Salmon", 30, INK, "middle")

s.save("04_star_vs_salmon.svg")

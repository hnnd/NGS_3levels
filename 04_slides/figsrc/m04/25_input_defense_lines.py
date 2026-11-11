#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-25 R 管线三道输入防线。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-25；配色：spec.md §2。
依据：教材 §14.5.2，课程脚本 04_deseq2_analysis.R L32–45。"""
from svghelp import *

s = SVG()

# ---- 左上：counts 矩阵 ----
s.rect(40, 90, 200, 200, WHITE, BLUE, 5, rx=12)
s.text(140, 130, "cts 矩阵", 30, BLUE, "middle", "bold")
for i, name in enumerate(["s1", "s2", "s3"]):
    s.text(66 + i * 58, 152, name, 30, INK, "middle")
for r in range(3):
    for c in range(3):
        s.rect(44 + c * 58, 164 + r * 30, 50, 28, PANEL, None)
s.text(140, 278, "colnames", 30, GRAY, "middle")

# ---- 右上：coldata ----
s.rect(520, 90, 200, 200, WHITE, PURPLE, 5, rx=12)
s.text(620, 130, "coldata", 30, PURPLE, "middle", "bold")
for i, name in enumerate(["s1", "s2", "s3"]):
    s.text(546 + i * 58, 152, name, 30, INK, "middle")
for r, lab in enumerate(["K", "K", "N"]):
    s.rect(534, 164 + r * 30, 172, 28, PURPLE_TINT, None)
    s.text(620, 188 + r * 30, lab + " 组", 30, INK, "middle")
s.text(620, 278, "rownames", 30, GRAY, "middle")

# ---- 中上：错配警示 ----
s.rect(268, 120, 224, 150, RED_TINT, RED, 5, rx=12)
s.path("M 290 142 L 316 188 M 316 142 L 290 188", RED, 6)
s.text(380, 168, "顺序", 30, INK, "middle", "bold")
s.text(380, 208, "不一致", 30, INK, "middle", "bold")
s.text(380, 252, "静默 · 全错", 30, GRAY, "middle")

# ---- 三道防线 ----
lines = [
    ("1", "anyDuplicated()", "检查重复名称", ORANGE),
    ("2", "setdiff() 双向", "双侧集合比对", ORANGE),
    ("3", "coldata[colnames, ]", "显式强制重排", CYAN_DEEP),
]
for i, (num, code, cap, col) in enumerate(lines):
    y = 350 + i * 88
    s.rect(60, y, 420, 76, WHITE, col, 5, rx=12)
    s.circle(104, y + 38, 22, col)
    s.text(104, y + 48, num, 32, WHITE, "middle", "bold")
    s.text(320, y + 34, code, 30, INK, "middle", "bold")
    s.text(320, y + 66, cap, 30, INK, "middle")
    s.arrow(486, y + 38, 540, y + 38, GREEN, 5, 13)
    s.circle(572, y + 38, 24, GREEN)
    s.polyline([(560, y + 38), (569, y + 45), (586, y + 25)], WHITE, 6)

# 终极断言
s.rect(60, 628, 660, 62, GREEN_TINT, GREEN, 5, rx=12)
s.text(360, 671, "终极一致性断言", 30, GREEN, "middle", "bold")
s.text(620, 671, "stopifnot()", 30, GREEN, "middle", "bold")

s.save("25_input_defense_lines.svg")

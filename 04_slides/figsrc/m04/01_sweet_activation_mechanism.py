#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-01 应用案例：Xoo TAL effector → EBE → 转录组锁定 Os8N3 → 编辑抗病闭环。
图内文字与版式：reviews/course/M04_FIGP_001.md §4 FIG-M04-01；配色：spec.md §2。
依据：教材 §14.4.10，讲义 ③3.1。"""
from svghelp import *

s = SVG()

# 三栏顶部标签（方案给定文字，分两行防重叠）
s.label(133, 66, ["病原分泌", "效应因子"], 30, BLUE, weight="bold")
s.label(400, 66, ["转录组锁定", "感病基因"], 30, BLUE, weight="bold")
s.label(667, 66, ["靶向编辑", "获抗性"], 30, BLUE, weight="bold")

# ---- 栏 1：Xoo 侵染 ----
s.rect(55, 116, 160, 88, BLUE_TINT, BLUE, 5, rx=18)
s.text(135, 173, "Xoo", 40, BLUE, "middle", "bold")
for i, yy in enumerate((138, 168, 198)):
    s.arrow(215, yy, 258, 252 + (i - 1) * 34, ORANGE, 5, 13)
s.circle(133, 441, 92, WHITE, BLUE, 6)
s.line(63, 441, 203, 441, BLUE, 5)
s.rect(136, 417, 60, 48, CYAN, BLUE, 4)
s.text(166, 450, "EBE", 30, WHITE, "middle", "bold")
s.arrow(166, 467, 166, 508, GREEN, 5, 13)
s.text(182, 502, "Os8N3", 30, GREEN, "start", "bold")
s.label(133, 588, ["结合启动子"], 32, INK)

# ---- 栏间箭头 ----
s.arrow(252, 441, 292, 441, GRAY, 6, 16)
s.arrow(508, 441, 548, 441, GRAY, 6, 16)

# ---- 栏 2：转录组对比（对照 vs 处理）----
s.text(452, 128, "Os8N3", 30, ORANGE, "middle", "bold")
s.arrow(466, 136, 466, 206, ORANGE, 4, 12)

def bar_card(x0, tall_orange):
    s.rect(x0, 210, 96, 190, WHITE, BLUE, 4, rx=10)
    base = 382
    hs = [24, 33, 21, 27, 22]
    for i, hh in enumerate(hs):
        x = x0 + 12 + i * 16
        if tall_orange and i == 2:
            hh = 150
            s.rect(x, base - hh, 13, hh, ORANGE, None)
        else:
            s.rect(x, base - hh, 13, hh, CYAN, None)
    s.line(x0 + 6, base, x0 + 90, base, BLUE, 4)

bar_card(288, False)
bar_card(416, True)
s.text(336, 436, "对照", 30, GRAY, "middle")
s.text(464, 436, "感病", 30, GRAY, "middle")

# ---- 栏 3：编辑 EBE 获抗性 ----
s.line(563, 441, 763, 441, BLUE, 5)
s.rect(625, 417, 60, 48, CYAN, BLUE, 4)
s.text(655, 450, "EBE", 30, WHITE, "middle", "bold")
s.line(629, 421, 681, 465, RED, 7)   # 红色 ✗（全图唯一警示）
s.line(681, 421, 629, 465, RED, 7)
# 水稻植株（绿色）
s.line(680, 336, 680, 206, GREEN, 8, cap="round")
s.polygon([(680, 284), (640, 256), (676, 262)], GREEN)
s.polygon([(680, 262), (722, 232), (684, 242)], GREEN)
for dx, dy in ((0, 0), (-14, 14), (14, 14)):
    s.circle(680 + dx, 192 + dy, 7, GREEN)
s.circle(737, 144, 27, GREEN)
s.polyline([(724, 144), (733, 155), (751, 132)], WHITE, 6)

s.save("01_sweet_activation_mechanism.svg")

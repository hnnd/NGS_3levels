#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-12 因子水平字母序陷阱与三道闸防御。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-12；配色：spec.md §2。
依据：教材 §14.4.5 / §14.5.3；机制例（KO/WT 字母序）同 demos/ch14_reversed_reflevel.py Part 0。"""
from svghelp import *

s = SVG()

# ---- 上部：字母序陷阱 ----
s.label(400, 50, ["默认字母序反号"], 30, RED, weight="bold")
s.rect(50, 84, 320, 158, WHITE, BLUE, 4, rx=12)
s.text(80, 130, 'levels: c("KO", "WT")', 30, INK, "start")
s.text(80, 172, "按字母排序", 30, GRAY, "start")
s.text(80, 214, "默认： WT vs KO", 30, INK, "start", "bold")
s.arrow(380, 163, 446, 163, GRAY, 6, 15)
# log2FC 反号示例
s.rect(462, 84, 320, 158, RED_TINT, RED, 5, rx=12)
s.text(492, 130, "真实： KO 高表达", 30, INK, "start")
s.text(492, 172, "报告 log2FC < 0", 30, INK, "start", "bold")
s.rect(492, 190, 220, 16, ORANGE)
s.text(492, 228, "反号 · 不报错", 30, GRAY, "start")

# ---- 下部：三道闸 ----
s.text(400, 306, "相信符号之前先过三道闸", 30, GRAY, "middle")
gates = [("闸 1", "relevel()", "ref = WT"),
         ("闸 2", "contrast", "分子 / 分母"),
         ("闸 3", "print", "description")]
labels = ["显式指定对照", "显式指定分子分母", "打印描述核对"]
for i, ((g, code, sub), lab) in enumerate(zip(gates, labels)):
    x = 40 + i * 250
    s.rect(x, 336, 230, 230, WHITE, GREEN, 5, rx=14)
    s.text(x + 115, 378, g, 30, GREEN, "middle", "bold")
    s.text(x + 115, 434, code, 32, INK, "middle", "bold")
    s.text(x + 115, 476, sub, 30, GRAY, "middle")
    s.circle(x + 115, 522, 20, GREEN)
    s.polyline([(x + 104, 522), (x + 112, 530), (x + 128, 510)], WHITE, 6)
    s.text(x + 115, 604, lab, 30, INK, "middle")

s.save("12_relevel_three_gates.svg")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-36 padj × |log2FC| 二维过滤四象限与报告三要素。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-36；配色：spec.md §2。
依据：教材 §14.4.6 / §14.5.4，讲义 ⑦-5。"""
import random

from svghelp import *

s = SVG()

# ---- 二维平面 ----
x0, y0, w, h = 60, 90, 380, 420
s.rect(x0, y0, w, h, WHITE, BLUE, 5, rx=8)
mx, my = x0 + w / 2, y0 + h / 2
s.line(mx, y0, mx, y0 + h, PANEL, 4, dash="12 10")
s.line(x0, my, x0 + w, my, PANEL, 4, dash="12 10")
# 阈值线
tx = x0 + w * 0.72
ty = y0 + h * 0.30
s.line(tx, y0, tx, y0 + h, RED, 5)
s.line(x0, ty, x0 + w, ty, RED, 5)
s.text(tx, y0 + h + 40, "|log2FC| 阈值", 30, GRAY, "middle")
s.text(x0 + 6, y0 - 12, "-log10(padj)", 30, GRAY, "start")

rng = random.Random(20260829)
# 右上双达标（绿）
for i in range(14):
    s.circle(tx + 8 + rng.random() * (x0 + w - tx - 16),
             y0 + 10 + rng.random() * (ty - y0 - 24), 7, GREEN)
# 左上仅 padj（紫）
for i in range(10):
    s.circle(x0 + 14 + rng.random() * (mx - x0 - 30),
             y0 + 10 + rng.random() * (ty - y0 - 24), 7, PURPLE)
# 右下仅 FC（橙）— 低丰度噪声
for i in range(10):
    s.circle(tx + 8 + rng.random() * (x0 + w - tx - 16),
             ty + 16 + rng.random() * (y0 + h - ty - 30), 7, ORANGE)

# 象限注
s.text(180, y0 + h - 18, "显著 · 弱效应", 30, PURPLE, "middle")
s.text(440, y0 - 12, "双达标", 30, GREEN, "middle", "bold")
s.text(450, y0 + h - 18, "仅 FC · 噪声", 30, ORANGE, "middle")

# ---- 右侧三要素卡 ----
s.rect(480, 90, 300, 420, WHITE, BLUE, 5, rx=14)
s.text(630, 136, "报告必须写明", 30, BLUE, "middle", "bold")
items = [("1", "设计公式"), ("2", "两个阈值"),
         ("3", "背景基因集")]
for i, (num, txt) in enumerate(items):
    y = 230 + i * 110
    s.circle(518, y, 22, GREEN)
    s.text(518, y + 11, num, 32, WHITE, "middle", "bold")
    s.text(552, y + 11, txt, 30, INK, "start", "bold")

# ---- 中文结论 ----
s.text(250, 590, "统计显著与效应量", 30, INK, "middle", "bold")
s.text(640, 590, "双重正交阈值", 30, INK, "middle", "bold")
s.text(250, 646, "报告标明设计公式", 30, INK, "middle", "bold")
s.text(640, 646, "双阈值与背景集", 30, INK, "middle", "bold")

s.save("36_two_thresholds_quadrants.svg")

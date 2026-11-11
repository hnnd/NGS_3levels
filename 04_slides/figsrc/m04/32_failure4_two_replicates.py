#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-32 失效四 2 重复：单基因方差噪、跨基因收缩兜底、结论限候选清单。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-32；配色：spec.md §2。
依据：教材 §14.5.4，讲义 ⑦。抽样分布为概念形态示意（n=2 → df=1）。"""
import math

from svghelp import *

s = SVG()

# ---- 左：单基因抽样厚尾 ----
s.label(190, 56, ["单基因自由度小"], 30, BLUE, weight="bold")
s.rect(40, 90, 300, 300, WHITE, BLUE, 5, rx=12)
# 厚尾分布曲线（t-like）
pts = []
for i in range(81):
    x = i / 80 * 6 - 3
    y = 1 / (1 + abs(x) ** 2.2)
    pts.append((190 + x * 42, 340 - y * 190))
s.curve(pts, RED, 6)
s.line(60, 340, 320, 340, BLUE, 4)
s.line(190, 340, 190, 130, PANEL, 3, dash="8 8")
s.text(190, 372, "n = 2 → df = 1", 30, RED, "middle", "bold")
s.text(190, 424, "波动难辨离群", 30, INK, "middle", "bold")

# ---- 中：跨基因收缩兜底 ----
s.label(485, 56, ["跨基因收缩兜底"], 30, BLUE, weight="bold")
s.rect(350, 90, 270, 300, WHITE, BLUE, 5, rx=12)
trend = [(380 + i * 24, 140 + i * 16) for i in range(9)]
s.curve(trend, BLUE, 5)
for px, py in ((410, 210), (440, 150), (470, 260), (500, 180), (530, 300),
               (560, 200), (590, 250)):
    s.circle(px, py, 8, INK)
for px, py in ((410, 190), (440, 158), (470, 240), (500, 190), (530, 268),
               (560, 212), (590, 242)):
    s.circle(px, py, 8, CYAN_DEEP)
s.arrow(530, 300, 530, 262, GRAY, 4, 11)
s.text(485, 372, "向趋势线收缩", 30, GRAY, "middle")
s.text(485, 424, "df = 12 − 5 = 7", 30, GRAY, "middle")

# ---- 右：结论边界 ----
s.label(720, 52, ["结论限", "候选清单"], 30, GREEN, weight="bold")
s.rect(650, 90, 140, 300, WHITE, GREEN, 5, rx=12)
s.rect(680, 130, 80, 60, GREEN_TINT, None, rx=8)
s.rect(680, 210, 80, 60, GREEN_TINT, None, rx=8)
s.rect(680, 290, 80, 60, GREEN_TINT, None, rx=8)
s.polyline([(698, 170), (706, 178), (722, 156)], GREEN, 6, fill="none")
s.polyline([(698, 250), (706, 258), (722, 236)], GREEN, 6, fill="none")
s.polyline([(698, 330), (706, 338), (722, 316)], GREEN, 6, fill="none")

# ---- 底部结论 ----
s.text(400, 472, "仅限候选清单", 30, GREEN, "middle", "bold")
s.text(400, 524, "不显著 ≠ 无效应", 30, GRAY, "middle")
s.text(400, 576, "须经独立验证", 30, GRAY, "middle")
s.text(400, 624, "2 重复： 单基因方差跨基因借用", 30,
       GRAY, "middle")
s.text(400, 668, "不显著 ≠ 无变化 · 候选须跟进验证", 30,
       GRAY, "middle")

s.save("32_failure4_two_replicates.svg")

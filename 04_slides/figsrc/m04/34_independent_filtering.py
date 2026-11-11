#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-34 独立过滤 baseMean 阈值扫描与峰值容差选择。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-34；配色：spec.md §2。
依据：教材 §14.4.6，讲义 ⑦-3。散点与扫描曲线为概念形态示意。"""
import math

from svghelp import *

s = SVG()

# ---- 上：baseMean vs -log10(p) ----
s.text(190, 56, "低表达 → 功效低", 30, GRAY, "middle")
s.rect(40, 76, 300, 240, WHITE, BLUE, 5, rx=12)
s.text(190, 350, "baseMean", 30, GRAY, "middle")
s.text(60, 106, "-log10(p)", 30, GRAY, "start")
import random
rng = random.Random(20260829)
for i in range(46):
    x = 60 + rng.random() * 240
    y = 290 - min(rng.expovariate(1 / 30), 190) * (0.15 + (x - 60) / 240)
    s.circle(x, y, 5, CYAN if x > 150 else PANEL)
s.line(190, 300, 190, 90, PANEL, 3, dash="8 8")
s.text(150, 316, "低均值： 平", 30, GRAY, "middle")

# ---- 下：阈值扫描曲线 ----
s.rect(380, 76, 400, 240, WHITE, BLUE, 5, rx=12)
s.text(580, 350, "过滤分位数 θ", 30, GRAY, "middle")
s.text(400, 106, "拒绝数", 30, GRAY, "start")
pts = []
for i in range(21):
    th = i / 20
    r = 200 * math.exp(-((th - 0.42) ** 2) / 0.08) + 40
    pts.append((410 + th * 340, 296 - r))
s.curve(pts, CYAN_DEEP, 6)
# 峰值容差带
s.line(410 + 0.30 * 340, 110, 410 + 0.30 * 340, 296, ORANGE, 4, dash="10 8")
s.line(410 + 0.54 * 340, 110, 410 + 0.54 * 340, 296, ORANGE, 4, dash="10 8")
s.star(410 + 0.30 * 340, 296 - (200 * math.exp(-((0.30 - 0.42) ** 2) / 0.08)
                                  + 40), 18, GREEN)
s.text(580, 390, "峰值 ± 容差", 30, ORANGE, "middle", "bold")

# ---- 中文结论 ----
s.label(200, 416, ["低表达功效低"], 30, BLUE)
s.label(200, 478, ["阈值扫描曲线"], 30, INK)
s.label(200, 530, ["拒绝数峰值容差"], 30, INK)
s.label(200, 590, ["独立过滤控假发现"], 30, GREEN, weight="bold")
s.text(230, 640, "仅 padj = NA（被过滤）", 30, GRAY, "middle")
s.text(230, 684, "pvalue 保留 · BH 检验更少", 30, GRAY, "middle")

# 右侧补充
s.rect(420, 440, 360, 236, BLUE_TINT, BLUE, 5, rx=14)
s.text(590, 486, "为什么要过滤", 30, BLUE, "middle", "bold")
s.text(590, 532, "低均值基因几乎只添噪声", 30, GRAY, "middle")
s.text(590, 572, "徒增 BH 检验次数", 30, GRAY, "middle")
s.text(590, 620, "θ* = 峰值一个残差", 30, GRAY, "middle")
s.text(590, 656, "标准差内的最低 θ", 30, GRAY, "middle")

s.save("34_independent_filtering.svg")

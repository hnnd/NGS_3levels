#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-05 多重兼容读段分摊：featureCounts 丢弃 vs Salmon VBEM。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-05；配色：spec.md §2。
依据：教材 §14.4.2，讲义 ④4.2。"""
from svghelp import *

s = SVG()

s.label(400, 52, ["多重兼容读段"], 32, BLUE, weight="bold")

# 读段同时命中两个 isoform 的共享外显子区
s.rect(240, 84, 200, 26, CYAN, None)
for x in (280, 330, 380):
    s.line(x, 84, x, 110, WHITE, 3)
# Isoform 1 / 2
s.line(120, 168, 680, 168, BLUE, 5)
for x0 in (150, 260, 370):
    s.rect(x0, 154, 90, 28, BLUE, None)
s.text(120, 144, "Isoform 1", 30, GRAY, "start")
s.line(120, 252, 680, 252, BLUE, 5)
for x0 in (260, 370, 480):
    s.rect(x0, 238, 90, 28, PURPLE, None)
s.text(120, 228, "Isoform 2", 30, GRAY, "start")
s.rect(280, 140, 190, 124, "none", None)
s.polyline([(280, 140), (470, 140), (470, 264), (280, 264), (280, 140)],
           ORANGE, 3, dash="12 10")   # 共享区
s.line(300, 110, 300, 154, GRAY, 3, dash="8 8")
s.line(380, 110, 380, 154, GRAY, 3, dash="8 8")
s.line(330, 110, 330, 238, GRAY, 3, dash="8 8")
s.line(420, 110, 420, 238, GRAY, 3, dash="8 8")

# ---- 左下：featureCounts 丢弃 ----
s.rect(30, 330, 340, 330, WHITE, BLUE, 5, rx=14)
s.text(200, 376, "featureCounts", 30, BLUE, "middle", "bold")
s.rect(90, 420, 130, 24, CYAN, None)
s.path("M 120 424 L 190 444 M 190 424 L 120 444", RED, 7)  # 红色 ✗（全图唯一警示）
s.label(200, 500, ["简单丢弃低估"], 30, INK)
# 计数被低估的小条形
s.line(110, 620, 300, 620, BLUE, 4)
for x0, hh in ((120, 26), (165, 20), (210, 24)):
    s.rect(x0, 620 - hh, 26, hh, PANEL, None)
s.arrow(250, 560, 250, 600, ORANGE, 5, 13)
s.text(268, 592, "丢失", 30, ORANGE, "start")

# ---- 右下：Salmon VBEM ----
s.rect(430, 330, 340, 330, WHITE, GREEN, 5, rx=14)
s.text(600, 372, "Salmon VBEM", 30, GREEN, "middle", "bold")
s.label(600, 416, ["期望最大化"], 30, INK)
# 先验丰度条
s.line(470, 482, 730, 482, GREEN, 4)
s.rect(490, 448, 90, 34, GREEN, None)
s.rect(610, 460, 60, 22, CYAN, None)
s.text(640, 518, "先验", 30, GRAY, "middle")
# 读段按后验概率分摊
s.arrow(540, 524, 514, 572, GREEN, 5, 12)
s.arrow(612, 524, 656, 572, GREEN, 5, 12)
s.text(478, 556, "0.6", 30, GREEN, "middle", "bold")
s.text(706, 556, "0.4", 30, GREEN, "middle", "bold")
s.rect(455, 586, 110, 26, GREEN_TINT, GREEN, 4)
s.rect(615, 586, 100, 26, GREEN_TINT, GREEN, 4)
s.label(600, 646, ["丰度先验概率分摊"], 30, INK)

s.save("05_multimapping_em.svg")

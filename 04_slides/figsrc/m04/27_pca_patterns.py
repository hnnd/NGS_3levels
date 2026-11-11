#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-27 PCA 样本聚类三种形态判读。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-27；配色：spec.md §2。
依据：教材 §14.4.9，讲义 ⑥6.2。散点为概念形态示意。"""
from svghelp import *

s = SVG()


def panel(x0, title, title_col):
    s.rect(x0, 60, 230, 420, WHITE, BLUE, 5, rx=14)
    s.text(x0 + 115, 104, title, 30, title_col, "middle", "bold")
    # 坐标
    s.line(x0 + 40, 440, x0 + 200, 440, BLUE, 4)
    s.line(x0 + 40, 440, x0 + 40, 130, BLUE, 4)
    s.text(x0 + 200, 470, "PC1", 30, GRAY, "end")
    s.text(x0 + 26, 140, "PC2", 30, GRAY, "start")


# A 处理主导
panel(30, "A", GREEN)
for dx, dy in ((90, 210), (110, 250), (100, 290), (150, 230)):
    s.circle(30 + dx, dy, 13, GREEN)
for dx, dy in ((90, 340), (115, 370), (100, 400), (145, 355)):
    s.circle(30 + dx, dy, 13, CYAN_DEEP)
s.text(145, 530, "处理主导正常分离", 30, GREEN, "middle", "bold")

# B 批次主导
panel(285, "B", ORANGE)
for dx, dy in ((80, 220), (100, 260), (85, 300)):
    s.circle(285 + dx, dy, 13, PURPLE)
for dx, dy in ((80, 350), (105, 390), (90, 420)):
    s.circle(285 + dx, dy, 13, ORANGE)
for dx, dy in ((130, 240), (140, 330)):
    s.circle(285 + dx, dy, 13, PANEL)
s.text(400, 530, "批次效应主导混淆", 30, ORANGE, "middle", "bold")

# C 离群
panel(540, "C", RED)
for dx, dy in ((80, 230), (100, 270), (90, 310)):
    s.circle(540 + dx, dy, 13, GREEN)
for dx, dy in ((80, 370), (100, 410)):
    s.circle(540 + dx, dy, 13, CYAN_DEEP)
s.circle(540 + 165, 180, 19, PAPER)
s.circle(540 + 165, 180, 12, RED)
s.text(655, 530, "单个样本离群孤立", 30, INK, "middle", "bold")

s.text(400, 620, "N（处理） vs K（对照） · 批次 A/B", 30, GRAY,
       "middle")
s.text(400, 668, "先看 PCA： 批次还是处理主导？", 30, GRAY,
       "middle")

s.save("27_pca_patterns.svg")

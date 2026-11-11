#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_bracken_bayesian_redistrib.py — FIG-M07-12 Bracken 贝叶斯重分配机制与边界

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-12（P24，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.2（Bracken 用属层先验把高阶读段概率性地重分到种；不创造库里没有的物种，
重分之后仍是组成性数据）。
图内汉字 = 方案清单逐字，共 28 字（属层高阶读段 / 贝叶斯概率下分 / 重估到种 /
不创造新物种 / 仍属组成性）。种节点**不写份额数字**：Bracken 的重分比例依赖实测库与先验，
本图无入口可复现，按「数字纪律」只画长短不等的示意条，不给任何百分比。
红色两处同属「边界警示」一个语义组：边界卡外框 + 卡内两行红字。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 12_bracken_bayesian_redistrib.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 属层高阶读段集合 ----------------
s.rect(48, 44, 704, 140, BLUE_TINT, BLUE, 4, rx=16)
s.text(400, 96, "属层高阶读段", 36, BLUE, "middle", "bold")
for i in range(7):                       # 未定到种的读段（只到属）
    s.rect(80 + i * 96, 118, 64, 32, CYAN_DEEP, rx=7)

# ---------------- 计算动作 ----------------
s.line(400, 184, 400, 214, CYAN_DEEP, 4)
s.chip(400, 240, "贝叶斯概率下分", 32, WHITE, CYAN_DEEP, CYAN_DEEP)

# ---------------- 重分配流向：三个种节点（只画长短示意条，无数字） ----------------
SP = (128, 400, 672)
for cx in SP:
    s.arrow(400, 272, cx, 330, CYAN, 5, 14)

for i, cx in enumerate(SP):
    bx, bw, by, bh = cx - 96, 192, 334, 96
    s.rect(bx, by, bw, bh, GREEN_TINT, GREEN, 4, rx=14)
    s.circle(bx + 26, by + 30, 11, GREEN)          # 种节点标记（无文字）
    s.rect(bx + 44, by + 58, 128, 22, PANEL, rx=6)
    s.rect(bx + 44, by + 58, (128, 96, 72)[i], 22, GREEN, rx=6)

s.text(400, 470, "重估到种", 36, GREEN, "middle", "bold")

# ---------------- 边界卡：红色语义组 ----------------
s.rect(48, 512, 704, 150, RED_TINT, RED, 4, rx=16)
s.text(400, 570, "不创造新物种", 34, RED, "middle", "bold")
s.text(400, 632, "仍属组成性", 34, RED, "middle", "bold")
s.cross(118, 556, 20, RED, 7)

s.save("12_bracken_bayesian_redistrib.svg")

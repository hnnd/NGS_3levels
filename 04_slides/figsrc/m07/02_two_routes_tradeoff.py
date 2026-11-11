#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_two_routes_tradeoff.py — FIG-M07-02 双路线分流与取舍

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-02（P10，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.1（read-based 全样快照 vs assembly-based 关键重建；库外失明、低丰度断链）。
图内汉字 = 方案原句逐字，共 28 字（读段比对 / 库外失明 / 全样快照 / 从头组装 / 低丰度断 /
关键重建 / 按需分流）。方案原句「读段比对：库外失明」按标点分两行排（前置冒号留在上一行），
串读仍与方案逐字一致。顶部输入胶囊按方案「元素」画双螺旋图标、不写中文标签（写了会超 30 字）。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 02_two_routes_tradeoff.py
"""
import math
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 顶部输入：环境总 DNA 测序（图标表达，不写字） ----------------
s.rect(250, 58, 300, 76, BLUE_TINT, BLUE, 4, rx=38)
for phase in (0.0, math.pi):
    pts = [(x, 96 + 11 * math.sin(x / 42.0 + phase)) for x in range(286, 516, 8)]
    s.polyline(pts, CYAN, 4)

s.arrow(320, 140, 215, 190, CYAN, 5, 14)
s.arrow(480, 140, 585, 190, CYAN, 5, 14)

CARDS = [
    (40, "读段比对：", "库外失明", "全样快照", CYAN, CYAN_TINT, CYAN_DEEP),
    (410, "从头组装：", "低丰度断", "关键重建", GREEN, GREEN_TINT, GREEN),
]
CW, CH, CY = 350, 330, 190

for x, head, cost, trait, ink, tint, deep in CARDS:
    s.rect(x, CY, CW, CH, tint, ink, 4, rx=16)
    cx = x + CW / 2
    s.text(cx, CY + 76, head, 32, deep, "middle", "bold")
    s.text(cx, CY + 132, cost, 34, RED, "middle", "bold")
    s.text(cx, CY + 218, trait, 30, INK, "middle")
    # 路线示意：三条读段 / 重叠群短条
    for i in range(3):
        y = CY + 258 + i * 22
        s.rect(x + 88, y, CW - 176, 12, deep if i % 2 == 0 else CYAN, rx=6)

# ---------------- 底部总结 ----------------
s.rect(300, 570, 200, 78, BLUE, rx=16)
s.text(400, 622, "按需分流", 32, WHITE, "middle", "bold")

s.save("02_two_routes_tradeoff.svg")

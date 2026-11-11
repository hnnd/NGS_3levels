#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_three_questions_funnel.py — FIG-M07-01 宏基因组三问递进决策漏斗

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-01（P09，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.1（三个问题有依赖顺序：路线选型 → 组装可行性 → 功能结论强度）。
图内汉字 = 方案原句逐字，共 29 字（①物种组成：快照 / ②组装分箱：成箱 / ③功能活性：代谢 /
前问决定后问边界）；其余只有步骤序号、箭头、弧线与叉号。无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 01_three_questions_funnel.py
"""
import math
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

STEPS = [
    (140, "①物种组成：快照", BLUE, BLUE_TINT),
    (320, "②组装分箱：成箱", CYAN, CYAN_TINT),
    (500, "③功能活性：代谢", GREEN, GREEN_TINT),
]
BX, BW, BH = 56, 400, 112

s = SVG()

for y, txt, ink, tint in STEPS:
    s.rect(BX, y, BW, BH, tint, ink, 4, rx=16)
    s.text(BX + BW / 2, y + BH / 2 + 12, txt, 34, ink, "middle", "bold")

# 递进箭头：上一问的输出是下一问的输入
for y0, y1 in ((252, 320), (432, 500)):
    s.arrow(BX + BW / 2, y0 + 4, BX + BW / 2, y1 - 6, CYAN, 6, 16)

# 右侧红色反向弧线：后问的答案倒推不回前问的边界（虚线弧 + 实心箭头 + 红字标签）
s.path("M 560 594 C 672 496 672 300 574 206", RED, 6, dash="12 10")
s.polygon([(558, 200), (600, 186), (596, 224)], RED)

s.text(660, 132, "前问决定后问边界", 30, RED, "middle", "bold")

s.save("01_three_questions_funnel.svg")

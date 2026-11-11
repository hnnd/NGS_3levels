#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_dada2_six_steps.py — FIG-M06-11 DADA2 六步数据流向卡

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-11（P22，cols 一栏 800×700，new-svg）。
教材依据：§18.4.3（六步质量控制链，每一步的产出都是下一步的输入）。
图内汉字 = 方案原句逐字，共 21 字（截断过滤 4 / 学习模型 4 / 去噪推断 4 / 双端拼接 4 /
建表 2 / 去嵌合 3）；其余标注为六个函数名与 ASV table。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 11_dada2_six_steps.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

STEPS = [
    ("截断过滤", "filterAndTrim"),
    ("学习模型", "learnErrors"),
    ("去噪推断", "dada"),
    ("双端拼接", "mergePairs"),
    ("建表", "makeSequenceTable"),
    ("去嵌合", "removeBimeraDenovo"),
]

RAIL = 62
CX0, CW = 108, 636
H, PITCH = 70, 88
Y0 = 66

for i, (cap, fn) in enumerate(STEPS):
    y = Y0 + i * PITCH
    last = i == len(STEPS) - 1
    s.rect(CX0, y, CW, H, GREEN_TINT if last else WHITE,
           GREEN if last else PANEL, 3, rx=14)

    s.circle(RAIL, y + H / 2, 18, GREEN if last else BLUE)
    s.text(RAIL, y + H / 2 + 11, str(i + 1), 30, WHITE, "middle", "bold")

    s.text(CX0 + 26, y + H / 2 + 12, cap, 32, BLUE if last else INK,
           "start", "bold")
    s.text(CX0 + CW - 26, y + H / 2 + 12, fn, 30, GRAY, "end")

    if not last:
        s.arrow(RAIL, y + H / 2 + 19, RAIL, y + PITCH + H / 2 - 21,
                CYAN, 5, 12)

# ---------------- 最终产物：ASV 表 ----------------
OUT_Y = Y0 + 5 * PITCH + H + 68
s.arrow(400, 582, 400, OUT_Y - 32, GREEN, 5, 14)
s.chip(400, OUT_Y, "ASV table", 32, GREEN_TINT, GREEN, GREEN)

s.save("11_dada2_six_steps.svg")

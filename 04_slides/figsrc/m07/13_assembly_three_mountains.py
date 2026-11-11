#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_assembly_three_mountains.py — FIG-M07-13 宏基因组组装三座大山

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-13（P26，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.3（重复序列打断延伸；株系变异形成嵌合气泡；丰度悬殊使低频物种断链）。
图内汉字 = 方案清单逐字，共 27 字（高度重复打断组装 / 株系变异产生嵌合 /
丰度悬殊低频断链 / 难两全）。三座山一律深蓝主体；青蓝只画机制符号（跨越失败的重复条、
气泡与断开处）；红色只一处语义组：山顶红旗 + 红字「难两全」。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 13_assembly_three_mountains.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

PEAK = [(150, 214), (400, 176), (650, 214)]
BASE = 512
HW = 122


def mountain(cx, py, hw=HW):
    s.polygon([(cx - hw, BASE), (cx - hw * 0.28, py + 62), (cx, py),
               (cx + hw * 0.34, py + 70), (cx + hw, BASE)], BLUE)


for cx, py in PEAK:
    mountain(cx, py)

# ---------------- 山一：重复序列把延伸打断 ----------------
# 一列重复单元横跨山体，向上延伸的读段在重复区被截断（断口用青蓝缺口表示）
for i, y in enumerate((300, 342, 384, 426)):
    s.rect(60, y, 180, 16, CYAN_TINT, CYAN_DEEP, 3, rx=8)
s.line(150, 250, 150, 296, CYAN, 5, dash="10 8")
s.line(130, 384, 130, 500, CYAN_DEEP, 5, dash="8 12")
s.line(172, 384, 172, 500, CYAN_DEEP, 5, dash="8 12")

# ---------------- 山二：株系变异产生嵌合 ----------------
for cx, cy, r in ((350, 330, 20), (392, 372, 15), (444, 330, 18),
                  (368, 424, 13)):
    s.circle(cx, cy, r, CYAN_TINT, CYAN_DEEP, 3)
s.line(336, 452, 462, 452, CYAN_DEEP, 5, dash="9 9")
s.polygon([(452, 444), (472, 452), (452, 460)], CYAN_DEEP)

# ---------------- 山三：丰度悬殊导致低频断链 ----------------
for i, y in enumerate((300, 330, 360, 390, 420, 450, 480)):
    n = 6 - (i // 2)                            # 越往下点越稀 = 丰度越低
    for k in range(max(n, 1)):
        s.circle(650 - (n - 1) * 9 + k * 18, y, 6, CYAN_DEEP if i < 3 else CYAN)
s.line(650, 386, 650, 480, CYAN_DEEP, 5, dash="7 13")

# ---------------- 山脚标签（每座山两行，避免三列并排挤在一起） ----------------
for cx, lines in ((150, ("高度重复", "打断组装")),
                  (400, ("株系变异", "产生嵌合")),
                  (650, ("丰度悬殊", "低频断链"))):
    s.label(cx, 566, list(lines), 30, BLUE, "middle", "bold", leading=1.28)

# ---------------- 唯一红处：山顶旗帜「难两全」 ----------------
s.line(400, 176, 400, 96, RED, 5)
s.polygon([(400, 96), (472, 114), (400, 132)], RED)
s.rect(452, 138, 148, 48, WHITE, RED, 3, rx=10)
s.text(526, 172, "难两全", 30, RED, "middle", "bold")

s.save("13_assembly_three_mountains.svg")

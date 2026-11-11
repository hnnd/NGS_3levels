#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_design_card.py — FIG-M06-01 主线数据 20 run 三年交叉设计卡

方案：`reviews/course/M06_FIGP_001.md` §4 FIG-M06-01（P09，`.cols` 一栏 800×700，new-svg）。
教材依据：§18.1（20 个 run，Fe 与 nonFe 各 10）、§18.6（年份内两组数量相同：2 对 2、4 对 4、4 对 4）。
数字来源：教材正文与 06_data/master/README.md m06 的样本清单（20 run：2017 年 4、2018 年 8、2019 年 8）。
图内汉字 = 方案原句逐字，共 16 字（铁毒 10 / 非铁毒 10 / 三年交叉设计 / 可校正年份）；
其余为年份、样本数与 run 代号，均为教材已载事实。无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 01_design_card.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

s.title("二十个 run 的交叉设计", y=64)

# ---------------- 两列：铁毒 / 非铁毒 ----------------
COL = [(232, "铁毒 10", ORANGE, ORANGE_TINT, ORANGE_DEEP),
       (484, "非铁毒 10", CYAN, CYAN_TINT, CYAN_DEEP)]
CW, CH = 190, 108

for x, cap, ink, tint, deep in COL:
    s.text(x + CW / 2, 150, cap, 34, deep, "middle", "bold")

# 三年：2017（2+2）、2018（4+4）、2019（4+4）
ROWS = [(2017, "2 + 2"), (2018, "4 + 4"), (2019, "4 + 4")]
Y0, PITCH = 196, CH + 52

for i, (year, cnt) in enumerate(ROWS):
    y = Y0 + i * PITCH
    s.text(96, y + CH / 2 + 11, str(year), 32, GRAY, "middle")
    for x, _, ink, tint, deep in COL:
        s.rect(x, y, CW, CH, tint, deep, 4, rx=14)
        s.text(x + CW / 2, y + CH / 2 + 13, cnt, 34, INK, "middle", "bold")

# 年份轴：三年纵向连接，标出「同一批样本跨三年」
AX = 60
s.line(AX, Y0 + 10, AX, Y0 + 2 * PITCH + CH - 10, PURPLE, 4)
for i in range(3):
    s.circle(AX, Y0 + i * PITCH + CH / 2, 9, PURPLE)

# 交叉连线：同一年内两列成对（表示年份内两组都有对照）
for i in range(3):
    y = Y0 + i * PITCH + CH / 2
    s.line(COL[0][0] + CW + 6, y, COL[1][0] - 6, y, GREEN, 5, dash="10 8")

# ---------------- 结论 ----------------
s.bottom(["三年交叉设计", ("可校正年份", GREEN, "bold")], y=626, gap=46, size=32)

s.save("01_design_card.svg")

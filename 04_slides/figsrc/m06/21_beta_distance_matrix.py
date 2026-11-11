#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""21_beta_distance_matrix.py — FIG-M06-21 四大 β 距离敏感性矩阵

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-21（P34，cols 一栏 800×700，new-svg）。
教材依据：§18.4.7（选距离就是声明「何为差异」：Jaccard 不用丰度、不用树，对稀有类群敏感须抽平；
Bray–Curtis 用丰度不用树，对优势类群敏感、默认首选；Unweighted/Weighted UniFrac 需先建树）。
图内汉字 = 方案原句逐字，共 22 字（稀有种名单须抽平 / 优势种首选 / 新支出现 / 优势菌结构）；
象限轴标签用英文 presence、abundance、tree、no tree，距离名按方案英文原文。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 21_beta_distance_matrix.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

s.text(430, 54, "β distance", 34, BLUE, "middle", "bold")

# 象限区：x 152..768，y 96..580；十字线 x=460 / y=338
LX, RX, TY, BY_ = 152, 768, 96, 580
MX, MY = 460, 338
COL_L, COL_R = 306, 614
ROW_T, ROW_B = 217, 459

s.rect(LX, TY, MX - LX, MY - TY, PURPLE_TINT, PURPLE, 4, rx=10)
s.rect(MX, TY, RX - MX, MY - TY, CYAN_TINT, CYAN, 4, rx=10)
s.rect(LX, MY, MX - LX, BY_ - MY, ORANGE_TINT, ORANGE, 4, rx=10)
s.rect(MX, MY, RX - MX, BY_ - MY, GREEN_TINT, GREEN, 4, rx=10)

# 坐标轴十字（结构蓝）
s.line(LX - 16, MY, RX, MY, BLUE, 3)
s.line(MX, TY - 16, MX, BY_, BLUE, 3)

# 纵轴：上＝结合系统发育树，下＝不考虑树
s.text(58, ROW_T + 12, "tree", 30, GRAY, "middle")
s.text(58, ROW_B + 12, "no tree", 30, GRAY, "middle")
s.line(110, BY_ + 4, 110, TY - 10, GRAY, 3)
s.polygon([(110, TY - 16), (102, TY + 6), (118, TY + 6)], GRAY)

# 横轴：左＝无丰度，右＝丰度加权
s.text(COL_L, 654, "presence", 30, GRAY, "middle")
s.text(COL_R, 654, "abundance", 30, GRAY, "middle")
s.line(LX + 4, 618, RX, 618, GRAY, 3)
s.polygon([(RX + 6, 618), (RX - 16, 610), (RX - 16, 626)], GRAY)

# 四象限的距离卡：名称（英文原文）+ 方案原句
CARDS = [
    (COL_L, ROW_T, ["Unweighted", "UniFrac"], "新支出现", PURPLE, True),
    (COL_R, ROW_T, ["Weighted", "UniFrac"], "优势菌结构", CYAN_DEEP, True),
    (COL_L, ROW_B, ["Jaccard"], "稀有种名单须抽平", ORANGE_DEEP, False),
    (COL_R, ROW_B, ["Bray–Curtis"], "优势种首选", GREEN, False),
]

for cx, cy, names, phrase, ink, tree in CARDS:
    for i, ln in enumerate(names):
        s.text(cx, cy - 34 + i * 44, ln, 30, ink, "middle", "bold")
    s.text(cx, cy + 74, phrase, 30, INK, "middle", "bold")
    if tree:                      # 需先建树的两格：格内左上角的树枝图标
        bx, by = (LX + 42 if cx < MX else MX + 42), TY + 28
        s.line(bx, by, bx, by + 14, ink, 3)
        s.line(bx, by + 5, bx - 13, by + 22, ink, 3)
        s.line(bx, by + 5, bx + 13, by + 22, ink, 3)
        s.circle(bx, by - 4, 3, ink)
        s.circle(bx - 13, by + 25, 3, ink)
        s.circle(bx + 13, by + 25, 3, ink)

s.save("21_beta_distance_matrix.svg")

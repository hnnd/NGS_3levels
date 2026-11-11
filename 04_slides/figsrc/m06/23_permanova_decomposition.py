#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""23_permanova_decomposition.py — FIG-M06-23 PERMANOVA 距离方差分解几何

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-23（P37，cols 一栏 800×700，new-svg）。
教材依据：§18.4.8（由所有两两距离算 `SS_T`，拆成组间与组内；`R² = SS_组间 / SS_T` 才是效应量，
p 来自随机打乱分组标签）。
图内汉字 = 方案原句逐字，共 19 字（组内方差细线 / 组间距离粗箭 / 决定效应量大小）；
其余标注为 `SS_within`、`SS_between`、`R² = SS_between / SS_total` 与质心记号。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 23_permanova_decomposition.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

s.text(400, 54, "PERMANOVA", 34, BLUE, "middle", "bold")

# ================= 距离空间点阵：两组各 6 个样本 =================
C1, C2 = (250, 296), (556, 296)
G1 = [(192, 244), (240, 218), (296, 242), (198, 322), (250, 352), (300, 324)]
G2 = [(498, 240), (556, 216), (610, 242), (504, 318), (560, 350), (616, 316)]

# 组内细线（青蓝）：样本到本组质心 + 样本间细虚线
for g, c in ((G1, C1), (G2, C2)):
    for p in g:
        s.line(c[0], c[1], p[0], p[1], CYAN, 3)
    for i in range(len(g)):
        for j in range(i + 2, len(g)):
            s.line(g[i][0], g[i][1], g[j][0], g[j][1], CYAN, 2, dash="6 9")

# 组间粗箭头（深蓝）：两质心连线
s.arrow(C1[0] + 16, C1[1], C2[0] - 16, C2[1], BLUE, 10, head=24)

# 样本点与质心
for g, col in ((G1, CYAN_DEEP), (G2, GREEN)):
    for x, y in g:
        s.circle(x, y, 10, col)
for c in (C1, C2):
    s.circle(c[0], c[1], 13, WHITE, BLUE, 5)
    s.circle(c[0], c[1], 4, BLUE)

# ================= 符号标注 =================
s.text(212, 168, "SS_within", 30, CYAN_DEEP, "middle")
s.text(400, 168, "SS_between", 30, BLUE, "middle", "bold")
s.text(594, 168, "SS_within", 30, CYAN_DEEP, "middle")

# 语义说明：底部一行标出「组内细线」与「组间粗箭」
s.text(212, 430, "组内方差细线", 30, CYAN_DEEP, "middle", "bold")
s.text(596, 430, "组间距离粗箭", 30, BLUE, "middle", "bold")


# ================= R² 公式框 =================
s.rect(92, 458, 616, 116, GREEN_TINT, GREEN, 4, rx=14)
s.text(400, 502, "R² = SS_between / SS_total", 30, BLUE, "middle", "bold")
s.text(400, 548, "SS_between + SS_within = SS_total", 30, GRAY, "middle")

# ================= 底部 takeaway =================
s.text(400, 672, "决定效应量大小", 30, GREEN, "middle", "bold")

s.save("23_permanova_decomposition.svg")

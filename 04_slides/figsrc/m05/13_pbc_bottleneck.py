#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_pbc_bottleneck.py — FIG-M05-13 PBC 文库复杂度

方案：`reviews/course/M05_FIGP_001.md` §4.2 FIG-M05-13（P32，`.cols` 800×700，new-svg）。
教材依据：§15.4.4 L227–L230 与正文手算小库：90 个位置各 1 条读段、5 个位置各 2 条 →
M1 = 90、M_distinct = 90 + 5 = 95 → PBC1 = 90/95 = 0.947；PBC2 = 90/5 = 18。三个符号都数「位置」。
图内汉字 23 字，逐字取方案原句：瓶颈系数 4 / 单次读取位置比非冗余位置 12 / 衡量文库复杂度 7。
红不上图（本图无警示语义）：单次读取位置绿、冗余堆叠橙、位置轴深蓝。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 13_pbc_bottleneck.py
"""
from svghelp import *

M1, M2 = 90, 5
M_DISTINCT = M1 + M2
PBC1 = M1 / M_DISTINCT
PBC2 = M1 / M2
assert M_DISTINCT == 95 and abs(PBC1 - 0.947) < 1e-3 and PBC2 == 18

s = SVG()

s.text(400, 58, "瓶颈系数", 36, BLUE, "middle", "bold")

# ---------------- 位置轴：一条染色体 ----------------
AX_L, AX_R, AX_Y = 74, 726, 268
s.line(AX_L, AX_Y, AX_R, AX_Y, BLUE, 6)

# 90 个「恰好 1 条读段」的位置：15 列 × 6 行
for i in range(M1):
    x = AX_L + 12 + (i % 15) * 43
    y = AX_Y - 14 - (i // 15) * 26
    s.rect(x, y - 16, 8, 16, GREEN, rx=2)
# 5 个「恰好 2 条读段」的位置：两条柱堆在一起
for i in range(M2):
    x = AX_L + 26 + i * 128
    s.rect(x, AX_Y - 40, 9, 40, ORANGE, rx=3)
    s.rect(x + 12, AX_Y - 40, 9, 40, ORANGE, rx=3)
    s.line(x, AX_Y + 18, x + 21, AX_Y + 18, ORANGE, 4)

# ---------------- 两个系数：只写数字与符号 ----------------
s.badge(206, 470, "90/95 = 0.947", 32, GREEN, WHITE)
s.badge(568, 470, "90/5 = 18", 32, ORANGE, WHITE)

# ---------------- 底部：方案原句 ----------------
s.text(400, 570, "单次读取位置比非冗余位置", 32, INK, "middle", "bold")
s.text(400, 626, "衡量文库复杂度", 32, INK, "middle", "bold")

s.save("13_pbc_bottleneck.svg")

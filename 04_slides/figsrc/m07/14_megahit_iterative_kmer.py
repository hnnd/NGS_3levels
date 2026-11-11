#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_megahit_iterative_kmer.py — FIG-M07-14 MEGAHIT 迭代 k-mer 与 mercy-k-mer 机制

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-14（P27，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.3（k 从小到大迭代：小 k 连通低深度、大 k 跨越重复区；mercy-k-mer 用一端
已锚定的读段救回另一端低覆盖候选）。迭代链只标两端 k 值 21 与 141（MEGAHIT 递进链的首末档，
教材 §19.4.3）。
图内汉字 = 方案清单逐字，共 27 字（小尺连通低深度 / 大尺跨越重复区 / 单端锚定救低频 /
保留微弱连接）。红色一处：mercy-k-mer 的连接箭头与「保留微弱连接」同属一个语义组。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 14_megahit_iterative_kmer.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 上：迭代 k 链 21 → 141 ----------------
KS = (21, 41, 61, 81, 101, 121, 141)
X0, DX, YC = 110, 96, 182
for i, k in enumerate(KS):
    x = X0 + i * DX
    r = 22 + i * 3                       # 随 k 增大而放大的节点
    last = i == len(KS) - 1
    s.circle(x, YC, r, BLUE_TINT if last else CYAN_TINT,
             BLUE if last else CYAN_DEEP, 4)
    if i:                                # 迭代箭头
        s.arrow(x - DX + 26, YC, x - r - 4, YC, CYAN, 4, 12)

# 两端 k 值标在节点下方（不压住圆圈）
s.text(X0, YC + 62, "k=21", 30, CYAN_DEEP, "middle", "bold")
s.text(X0 + 6 * DX, YC + 66, "k=141", 30, BLUE, "middle", "bold")

# 小 k 区段 / 大 k 区段的语义括号
bracket = YC + 116
s.line(X0 - 34, bracket, X0 + 2 * DX, bracket, CYAN_DEEP, 4)
s.text(X0 + DX, bracket + 42, "小尺连通低深度", 30, CYAN_DEEP, "middle", "bold")
s.line(X0 + 4 * DX, bracket, X0 + 6 * DX + 34, bracket, BLUE, 4)
s.text(X0 + 5 * DX, bracket + 42, "大尺跨越重复区", 30, BLUE, "middle", "bold")

# 重复区标记：大 k 段上方一段横跨的重复单元，被整个跨过
s.rect(X0 + 4 * DX - 46, YC - 78, 2 * DX + 74, 20, CYAN_TINT, CYAN_DEEP, 3, rx=10)

# ---------------- 下：mercy-k-mer 单端锚定 ----------------
BY = 470
# 已锚定端（绿）：实心块 + 已确定的延伸片段（块内标「锚」，共 28 汉字，仍 ≤30）
s.rect(60, BY, 214, 64, GREEN_TINT, GREEN, 4, rx=12)
s.text(104, BY + 42, "锚", 30, GREEN, "middle", "bold")
for i in range(2):
    s.rect(136 + i * 66, BY + 19, 56, 26, GREEN, rx=6)

# 低覆盖候选端（橙虚线）：稀疏读段
s.rect(468, BY - 8, 272, 80, ORANGE_TINT, ORANGE_DEEP, 3, rx=12, dash="10 8")
for i in range(3):
    s.rect(494 + i * 80, BY + 20, 52, 26, ORANGE, rx=6)

# 红色语义组：救回连接箭头 + 说明
s.line(348, BY + 32, 452, BY + 32, RED, 6)
s.polygon([(446, BY + 21), (472, BY + 32), (446, BY + 43)], RED)

s.text(400, BY + 148, "单端锚定救低频", 32, ORANGE_DEEP, "middle", "bold")
s.text(400, BY + 206, "保留微弱连接", 32, RED, "middle", "bold")

s.save("14_megahit_iterative_kmer.svg")

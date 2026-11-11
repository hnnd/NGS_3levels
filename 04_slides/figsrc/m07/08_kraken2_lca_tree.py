#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_kraken2_lca_tree.py — FIG-M07-08 Kraken2 k-mer 查表与 LCA 树上浮

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-08（P20，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.2（读段切 k-mer 查哈希表，命中集合取最低共同祖先；不做全局比对）。
图内汉字 = 方案清单逐字，共 25 字（滑窗查表 / 命中集合 / 向上回溯 / 停在最低共同祖先 /
分叉即上浮）。叶节点与内部节点用「属 G、种 A、种 B」占位，不写真实物种名（避免编造分类单元）。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 08_kraken2_lca_tree.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 读段与 k-mer 滑窗 ----------------
s.text(44, 96, "滑窗查表", 34, CYAN_DEEP, "start", "bold")
s.rect(44, 118, 300, 44, CYAN_TINT, CYAN_DEEP, 3, rx=8)
for i in range(6):
    s.rect(58 + i * 46, 126, 38, 27, CYAN if i % 2 == 0 else CYAN_DEEP, rx=4)

# k-mer → 哈希表 → 命中集合
s.arrow(356, 140, 396, 140, CYAN_DEEP, 5, 14)
s.rect(396, 100, 172, 80, WHITE, CYAN_DEEP, 3, rx=10)
s.text(482, 152, "命中集合", 34, CYAN_DEEP, "middle", "bold")

s.arrow(482, 186, 482, 240, CYAN_DEEP, 5, 14)

# ---------------- 分类树：属 G → 种 A / 种 B ----------------
GY, GH = 240, 64
s.rect(378, GY, 208, GH, BLUE_TINT, BLUE, 4, rx=12)
s.text(482, GY + 42, "属 G", 34, BLUE, "middle", "bold")

LEAF_Y = 424
LEAF = ((196, "种 A"), (468, "种 B"))
for x, lbl in LEAF:
    s.rect(x, LEAF_Y, 176, 64, GREEN_TINT, GREEN, 4, rx=12)
    s.text(x + 88, LEAF_Y + 42, lbl, 34, GREEN, "middle", "bold")
    s.line(x + 88, LEAF_Y, 482, GY + GH, BLUE, 4)

# 分叉节点红圈：两条命中路径交汇处停在属，此即最低共同祖先
s.rect(360, GY - 24, 244, GH + 48, "none", RED, 5, rx=30, dash="12 9")

s.text(150, 586, "停在最低共同祖先", 34, RED, "middle", "bold")
s.text(150, 644, "分叉即上浮", 32, RED, "middle")

# ---------------- 向上回溯箭头（与叶节点保持距离） ----------------
s.arrow(736, 566, 736, 330, CYAN_DEEP, 5, 14)
s.text(724, 636, "向上回溯", 32, CYAN_DEEP, "end", "bold")

s.save("08_kraken2_lca_tree.svg")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_contamination_excess_copies.py — FIG-M07-19 污染度超额副本计数机理

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-19（P35，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.5（污染度 = Σ max(份数−1, 0) / M：单份不计、两份计一、三份计二；
分子可以超过分母，所以读数能大于 100%）。
图内汉字 = 方案清单逐字，共 29 字（只累计超出一的副本 / 单份不计两份计一 /
分子可超分母 / 非百分比截断）。公式用拉丁字母 n 与 M（不写「份数」，否则汉字超 30）。
份数条形图为示意（份数 1/2/3 与计入值 0/+1/+2 是公式定义，不是实测数据）。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 17_contamination_excess_copies.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 公式卡 ----------------
s.rect(48, 44, 704, 132, BLUE_TINT, BLUE, 4, rx=16)
s.text(400, 132, "Σ max(n − 1, 0) / M", 44, BLUE, "middle", "bold")

# ---------------- 份数条形图：单份 → 0，两份 → +1，三份 → +2 ----------------
L, BW, BH = 196, 54, 44
for i, (n, add, note) in enumerate(((1, 0, "单份不计两份计一"),
                                   (2, 1, None),
                                   (3, 2, None))):
    y = 232 + i * 96
    s.text(168, y + BH / 2 + 11, f"x{n}", 32, BLUE, "end", "bold")
    for k in range(n):
        col = CYAN if k == 0 else ORANGE
        s.rect(L + k * (BW + 10), y, BW, BH, col, rx=8)
    # 超出的一（橙色块）才进分子：用箭头指向计入值
    if n > 1:
        s.rect(L + BW + 10, y, (n - 1) * (BW + 10) - 10, BH, ORANGE, rx=8)
        s.line(L + BW + 10 + (n - 1) * (BW + 10) - 14, y + BH / 2,
               468, y + BH / 2, ORANGE_DEEP, 4, dash="8 8")
    s.text(474, y + BH / 2 + 12, f"+{add}" if add else "0", 36,
           ORANGE_DEEP if add else GRAY, "start", "bold")

# ---------------- 右侧警示卡（同一语义组：分子可超分母，故读数可破百） ----------------
s.rect(548, 214, 212, 178, RED_TINT, RED, 4, rx=14)
s.label(654, 303, ["分子可超分母", "非百分比截断"], 30, RED, "middle", "bold",
        leading=1.5)

# ---------------- 底部两条说明 ----------------
s.text(400, 596, "只累计超出一的副本", 34, ORANGE_DEEP, "middle", "bold")
s.text(400, 656, "单份不计两份计一", 34, ORANGE_DEEP, "middle", "bold")

s.save("17_contamination_excess_copies.svg")

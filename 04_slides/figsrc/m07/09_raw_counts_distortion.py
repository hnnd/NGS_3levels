#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_raw_counts_distortion.py — FIG-M07-09 原始计数失真双机制

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-09（P21，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.2（大量读段停在属或科只累计不指名；大基因组同等细胞数产出更多读段）。
图内汉字 = 方案清单逐字，共 27 字（高阶滞留：只累计不指名 / 大基因组：产出读段翻倍 / 不可作丰度）。
左卡三条读段落在科/属层（无人接手），右卡同一细胞数下大基因组的读段条数是小基因组的两倍。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 09_raw_counts_distortion.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

CARDS = [
    (24, ["高阶滞留：", "只累计不指名"], ORANGE, ORANGE_TINT, ORANGE_DEEP, "lca"),
    (408, ["大基因组：", "产出读段翻倍"], CYAN, CYAN_TINT, CYAN_DEEP, "size"),
]
CW, CH, CY = 368, 300, 88

for x, lines, ink, tint, deep, kind in CARDS:
    s.rect(x, CY, CW, CH, tint, ink, 4, rx=18)
    cx = x + CW / 2
    s.label(cx, CY + 62, lines, 32, deep, "middle", "bold")

    if kind == "lca":
        # 三条读段一路往上层级走，越走越粗的横条 = 只累计、不指名
        for i, w in enumerate((180, 240, 300)):
            y = CY + 132 + i * 46
            s.rect(cx - w / 2, y, w, 24, deep if i < 2 else ink, rx=6)
            s.text(cx - w / 2 - 14, y + 20, ("科", "属", "种")[i], 30, GRAY, "end")
    else:
        # 两个基因组：小基因组 2 条读段，大基因组 4 条
        s.rect(x + 40, CY + 132, 120, 44, BLUE_TINT, BLUE, 3, rx=8)
        s.rect(x + 208, CY + 132, 120, 44, CYAN_TINT, CYAN_DEEP, 3, rx=8)
        s.text(x + 100, CY + 162, "小", 30, BLUE, "middle")
        s.text(x + 268, CY + 162, "大", 30, CYAN_DEEP, "middle")
        for i in range(2):
            s.rect(x + 44 + i * 58, CY + 200, 48, 20, CYAN, rx=5)
        for i in range(4):
            s.rect(x + 212 + i * 28, CY + 200, 22, 20, CYAN_DEEP, rx=5)

# ---------------- 底部警告 ----------------
s.rect(240, 448, 320, 92, RED_TINT, RED, 4, rx=18)
s.text(400, 508, "不可作丰度", 36, RED, "middle", "bold")

# 两条机制各自的代价说明（无新汉字，仅箭头）
s.arrow(208, 392, 300, 448, RED, 5, 13)
s.arrow(592, 392, 500, 448, RED, 5, 13)

s.save("09_raw_counts_distortion.svg")

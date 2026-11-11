#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""22_functional_potential_barriers.py — FIG-M07-24 从基因潜力到真实代谢的三道生理屏障

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-24（P41，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.6（检出编码基因只说明遗传潜力；到真实代谢之间要过转录调控、酶催化活性、
底物环境可及三道门槛；因此缺失只能算弱证据）。
图内汉字 = 方案清单逐字，共 26 字（编码基因：遗传潜力 / 三道屏障：转录酶催底物 /
潜力不等于活性）。三道门只标序号 1/2/3（门本身不再写「转录/酶催/底物」单字，避免与整句重复）。
通过量逐道递减用 4→3→2 个圆点示意，不写比例数字（无入口）。红色一处：底部「潜力不等于活性」。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 22_functional_potential_barriers.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 起点：编码基因（深蓝） ----------------
s.rect(96, 40, 528, 88, BLUE_TINT, BLUE, 4, rx=16)
s.text(360, 94, "编码基因：遗传潜力", 32, BLUE, "middle", "bold")

# ---------------- 三道门（青蓝，窄口闸门形态） ----------------
GY = (182, 306, 430)
for i, y in enumerate(GY):
    s.rect(200, y, 320, 74, CYAN_TINT, CYAN_DEEP, 4, rx=8)
    s.rect(336, y + 16, 48, 58, WHITE, CYAN_DEEP, 3, rx=6)     # 窄通道
    s.text(268, y + 46, str(i + 1), 34, CYAN_DEEP, "middle", "bold")
    # 通过量递减：4 → 3 → 2 个分子（示意，不给比例）
    for k in range(4 - i):
        s.circle(562 + k * 34, y + 36, 10, CYAN_DEEP if i == 0 else CYAN)

# 门间箭头（主轴 x = 360）
s.arrow(360, 132, 360, GY[0] - 8, CYAN_DEEP, 5, 14)
for y0, y1 in ((GY[0] + 78, GY[1] - 8), (GY[1] + 78, GY[2] - 8)):
    s.arrow(360, y0, 360, y1, CYAN_DEEP, 5, 14)

# ---------------- 出口：真实代谢（绿） ----------------
s.rect(272, 552, 320, 76, GREEN_TINT, GREEN, 4, rx=16)
s.star(432, 590, 28, GREEN)

# ---------------- 左下双行：三道屏障 ----------------
s.label(52, 590, ["三道屏障：", "转录酶催底物"], 30, CYAN_DEEP, "start", "bold",
        leading=1.34)

# ---------------- 红色语义组：潜力不等于活性 ----------------
s.text(432, 676, "潜力不等于活性", 32, RED, "middle", "bold")

s.save("22_functional_potential_barriers.svg")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_error_hypothesis.py — FIG-M06-09 DADA2 泊松错误检验判据

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-09（P20，cols 一栏 800×700，new-svg）。
教材依据：§18.4.2（低丰度序列对高丰度亲本做错误假说检验：p 在极小阈值之上无法排除
测序错误则并入亲本；跌破阈值则拒绝错误假说、确立独立 ASV）。
图内汉字 = 方案原句逐字，共 18 字（高概率并入亲本 6 / 突破极小阈值 6 / 确立独立实体 6）；
其余标注为 parent、P ≥ 1e−40、P < 1e−40 与丰度符号。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 09_error_hypothesis.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 顶部：高丰度亲本序列 ----------------
PY = 76
s.rect(150, PY, 500, 76, BLUE_TINT, BLUE, 4, rx=14)
s.text(400, PY + 48, "parent  ASV", 34, BLUE, "middle", "bold")

# ---------------- 阈值分流线 ----------------
TH_Y = 240
s.line(110, TH_Y, 690, TH_Y, RED, 5, dash="16 10")
s.text(400, TH_Y - 20, "P = 1e−40", 30, ORANGE_DEEP, "middle", "bold")

s.arrow(400, PY + 80, 400, TH_Y - 50, CYAN_DEEP, 6, 16)

# ---------------- 左分支：并入亲本（P ≥ 1e−40） ----------------
LBX = 118
s.arrow(400, TH_Y + 6, 268, 368, CYAN_DEEP, 5, 14)
s.rect(LBX, 384, 286, 172, ORANGE_TINT, ORANGE, 4, rx=16)
s.text(LBX + 143, 434, "P ≥ 1e−40", 32, ORANGE_DEEP, "middle", "bold")
s.label(LBX + 143, 494, wrap("高概率并入亲本", 32, 250), 32, ORANGE_DEEP)

# ---------------- 右分支：确立独立 ASV（P < 1e−40） ----------------
RBX = 452
s.arrow(400, TH_Y + 6, 532, 368, GREEN, 5, 14)
s.rect(RBX, 384, 286, 172, GREEN_TINT, GREEN, 4, rx=16)
s.text(RBX + 143, 434, "P < 1e−40", 32, GREEN, "middle", "bold")
s.label(RBX + 143, 494, wrap("突破极小阈值", 32, 250), 32, GREEN)

# ---------------- 底部结论 ----------------
s.rect(196, 590, 408, 76, BLUE_TINT, BLUE, 4, rx=14)
s.text(400, 642, "确立独立实体", 34, BLUE, "middle", "bold")
s.arrow(RBX + 143, 560, 552, 586, GREEN, 5, 14)

s.save("09_error_hypothesis.svg")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_chimera_mechanism.py — FIG-M06-13 嵌合体双亲拼接成因与识别

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-13（P25，cols 一栏 800×700，new-svg）。
教材依据：§18.4.3 第五步（未完全延伸的产物变性后退火到另一模板中段成为「大号引物」，
产出前半段属 A、后半段属 B 的嵌合分子；候选 ASV 若丰度低于两个亲本则被剔除）。
图内汉字 = 方案原句逐字，共 19 字（模板切换假变异 7 / 双亲拼接成因 6 / 丰度低于双亲 6）；
其余标注为 A / B 与箭头。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 13_chimera_mechanism.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

X0, X1 = 96, 704

# ---------------- 亲本 A：只延伸了前半段 ----------------
s.text(X0 - 12, 108, "A", 34, CYAN_DEEP, "end", "bold")
s.rect(X0, 86, X1 - X0, 34, CYAN_TINT, CYAN_DEEP, 3, rx=6)

# 未完成延伸产物：青色前半段，3′ 端停在半途
s.rect(X0, 128, 300, 30, CYAN, None, 0, rx=6)
s.polygon([(X0 + 300, 143), (X0 + 282, 128), (X0 + 282, 158)], CYAN)

# ---------------- 亲本 B：退火位点在中段 ----------------
s.text(X0 - 12, 302, "B", 34, ORANGE_DEEP, "end", "bold")
s.rect(X0, 280, X1 - X0, 34, ORANGE_TINT, ORANGE_DEEP, 3, rx=6)

ANN = X0 + 408                     # 退火位置（亲本 B 中段）
s.line(ANN, 246, ANN, 340, ORANGE_DEEP, 3, dash="10 8")

# 由断点绕到亲本 B 中段的曲线箭头（模板切换）
s.curve([(X0 + 300, 182), (X0 + 330, 236), (ANN - 30, 264), (ANN, 276)],
        ORANGE_DEEP, 5)
s.arrow(ANN - 26, 270, ANN, 278, ORANGE_DEEP, 5, 14)

# ---------------- 拼接产物：前半 A + 后半 B ----------------
PDY = 390
s.rect(X0, PDY, ANN - X0, 34, CYAN, None, 0, rx=6)         # A 前半
s.rect(ANN, PDY, X1 - ANN, 34, ORANGE, None, 0, rx=6)      # B 后半
s.line(ANN, PDY - 8, ANN, PDY + 42, ORANGE_DEEP, 6)         # 拼接点
s.text(ANN, PDY - 22, "A+B", 30, ORANGE_DEEP, "middle", "bold")

s.arrow(X0 + 300, 352, X0 + 330, PDY - 12, BLUE, 4, 12)

# ---------------- 判定卡：丰度低于双亲 → 剔除 ----------------
CY2, CH2 = 468, 96
s.rect(120, CY2, 560, CH2, WHITE, BLUE, 4, rx=16)
s.text(400, CY2 + 58, "丰度低于双亲", 34, BLUE, "middle", "bold")
s.cross(560, CY2 + 58, 15, RED, 7)                          # 剔除标记（警示 2）

# ---------------- 两行判读 ----------------
s.text(400, 62, "双亲拼接成因", 32, INK, "middle", "bold")
s.bottom([("模板切换假变异", BLUE, "bold")], y=636, size=32)

s.save("13_chimera_mechanism.svg")

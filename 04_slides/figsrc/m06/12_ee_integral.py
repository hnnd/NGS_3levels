#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_ee_integral.py — FIG-M06-12 期望错误数 EE 积分机制

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-12（P23，cols 一栏 800×700，new-svg）。
教材依据：§18.4.3（`EE = Σ 10^(−Q/10)` 逐碱基累加错误概率，非平均质量；`maxEE=c(2,2)`）。
图内汉字 = 方案原句逐字，共 18 字（累积错误概率 6 / 极端低质主导 6 / 平均值有盲区 6）；
其余标注为 A / B、Q30 / Q10 与算术式。
两处数字均可手算复核：A 尾端 3 个 Q10 碱基 → 3 × 10^(−10/10) = 0.30；
B 全程 100 bp 的 Q28 → 100 × 10^(−28/10) = 0.158 ≈ 0.16（幂次在正文写，图面只留结果算式）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 12_ee_integral.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

X0, X1 = 156, 668

# ---------------- A：全程 Q30，尾端 3 个 Q10 ----------------
s.text(70, 104, "A", 36, BLUE, "middle", "bold")
s.text(X0, 66, "Q30", 30, GRAY, "start")
s.text(X1, 66, "Q10", 30, ORANGE_DEEP, "end", "bold")

s.rect(X0, 82, X1 - X0, 44, CYAN, None, 0, rx=8)        # Q30 主体
s.rect(590, 82, X1 - 590, 44, RED, None, 0, rx=8)       # 尾端 3 个 Q10
s.text(400, 176, "EE = 3 × 0.1 = 0.30", 32, ORANGE_DEEP, "middle", "bold")

# 累积曲线：前段几乎平的，尾端陡然抬升
s.line(X0, 300, X1, 300, INK, 4)
s.polyline([(X0, 300), (420, 298), (556, 294), (590, 288),
            (620, 250), (660, 196)], ORANGE_DEEP, 5)

# ---------------- B：全程 Q28 ----------------
s.text(70, 390, "B", 36, BLUE, "middle", "bold")
s.text(X0, 352, "Q28", 30, GRAY, "start")
s.rect(X0, 368, X1 - X0, 44, CYAN, None, 0, rx=8)
s.text(400, 462, "EE = 100 × 0.0016 = 0.16", 32, GREEN, "middle", "bold")

s.line(X0, 560, X1, 560, INK, 4)
s.polyline([(X0, 560), (X1, 500)], GREEN, 5)

# ---------------- 判读 ----------------
s.label(400, 618, ["累积错误概率"], 32, INK)
s.label(400, 668, ["极端低质主导　平均值有盲区"], 30, GRAY)

s.save("12_ee_integral.svg")

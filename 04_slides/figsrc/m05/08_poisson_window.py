#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_poisson_window.py — FIG-M05-08 MACS2 泊松窗口检验与尾概率（data-plot）

方案：`reviews/course/M05_FIGP_001.md` §4.1 FIG-M05-08（P24，`.cols` 800×700，data-plot）。
数据入口：`textbook/demos/ch15_local_lambda.py` Part 0 手算规则——
λ=10.0 时满足 P(X≥k) ≤ 1e-5 的最小 k = 27，P(X≥27 | 10.0) = 6.423e-6。
本脚本 import `min_k_for_tail` / `poisson_tail` 现算并断言，不写死数字。
纵轴取对数（10^-1 … 10^-7），否则 λ=10 的右尾在 6×10^-6 量级上肉眼不可见；
对数轴下 P(X=k) 的衰减与 27 处断崖才是真实形态。
图内汉字 24 字，逐字取方案原句（不增不减）：泊松窗口检验 6 / 全基因组多重校正 7 /
观察值达二十七显著过线 11。其余为轴刻度与符号（k、P(X=k)）。
红为唯一警示色：右尾柱（1 处）+ 阈值线（1 处）＝ 2 处。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 08_poisson_window.py
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]              # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from ch15_local_lambda import min_k_for_tail, poisson_tail   # noqa: E402

from svghelp import *                                    # noqa: F401,F403,E402

LAM, PCUT = 10.0, 1e-5
K_STAR = min_k_for_tail(LAM, PCUT)
P_TAIL = poisson_tail(K_STAR, LAM)
assert K_STAR == 27, K_STAR
assert abs(P_TAIL - 6.423e-6) < 1e-9, P_TAIL

KMAX = 36
PMF = [math.exp(-LAM) * LAM ** k / math.factorial(k) for k in range(KMAX + 1)]

s = SVG()

s.text(400, 58, "泊松窗口检验", 36, BLUE, "middle", "bold")
s.text(400, 104, "全基因组多重校正", 30, GRAY, "middle")

L, R, B, T = 128, 668, 528, 216
BW = (R - L) / (KMAX + 1)
LO, HI = -7.0, -0.6                       # log10 P 轴范围


def bx(k):
    return L + k * BW


def by(v):
    return B - (B - T) * (math.log10(max(v, 10 ** LO)) - LO) / (HI - LO)


# ---- 轴与刻度 ----
s.line(L, B, R, B, INK, 4)
s.line(L, B, L, T, INK, 4)
s.text(L, T - 30, "P(X = k)", 30, GRAY, "start")
s.text(R + 18, B + 12, "k", 30, GRAY, "start")
for e in range(-1, -8, -1):
    y = by(10 ** e)
    s.line(L, y, L - 8, y, INK, 3)
    s.text(L - 16, y + 10, f"10^{e}".replace("^-", "^-"), 30, GRAY, "end")
for k in (0, 10, 20, 27, 36):
    s.line(bx(k), B, bx(k), B + 8, INK, 3)
    s.text(bx(k) + BW / 2, B + 38, str(k), 30, GRAY, "middle")

# ---- 支流：k < 27 青蓝柱 ----
for k in range(K_STAR):
    s.rect(bx(k) + 2, by(PMF[k]), BW - 4, B - by(PMF[k]), CYAN, rx=3)

# ---- 右尾 k ≥ 27：红色柱（合成一条 path，红用量记 1 处）----
d = " ".join(
    f"M {bx(k) + 2} {B} L {bx(k) + 2} {by(PMF[k]):.1f} "
    f"L {bx(k + 1) - 2} {by(PMF[k]):.1f} L {bx(k + 1) - 2} {B} Z"
    for k in range(K_STAR, KMAX + 1))
s.path(d, RED, 3, fill=RED)

# ---- 阈值线（红 2）----
s.line(bx(K_STAR), B, bx(K_STAR), T - 24, RED, 5, dash="14 10")

# ---- 标注 ----
s.text(bx(10) + BW / 2, by(PMF[10]) - 14, "λ = 10", 30, CYAN_DEEP, "middle", "bold")
s.text(400, 148, f"P(X ≥ 27) = {P_TAIL:.3e}".replace("e-06", "×10^-6"),
       30, INK, "middle", "bold")

# ---- 底部 takeaway（方案原句）----
s.text(400, 626, "观察值达二十七显著过线", 32, BLUE, "middle", "bold")

s.save("08_poisson_window.svg")
print(f"check: λ={LAM} 最小 k={K_STAR}，P(X≥{K_STAR})={P_TAIL:.3e}")

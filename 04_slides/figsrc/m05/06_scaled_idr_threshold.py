#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_scaled_idr_threshold.py — FIG-M05-06 scaled IDR 与 540 门槛

方案：`reviews/course/M05_FIGP_001.md` §4.1 FIG-M05-06（P22，`.cols` 800×700，new-svg）。
教材依据：§15.4.2 L155–L159。
公式 y = −125·log2(x)；横轴取 log 刻度后曲线是直线：x=0.01 → 830.5，x=0.5 → 125；
x = 0.05 → 540.2（教材取整 540，脚本断言 |540.2−540| < 1）。
图内汉字 22 字，逐字取方案原句：非线性缩放：阈值五百四十对应不可重复率百分之五。
其余文字为轴刻度数字与符号（scaled / IDR / p = 0.05），不写整句英文。
红为唯一警示色：两条辅助线合成一个 path（1 处）+ 交点实心点（1 处）＝ 2 处。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 06_scaled_idr_threshold.py
"""
import math

from svghelp import *

FACTOR = 2.0
P_CUT = 0.05
Y_AT_CUT = -125.0 * math.log(P_CUT, FACTOR)     # 540.24
assert abs(Y_AT_CUT - 540) < 1, Y_AT_CUT

s = SVG()

s.text(400, 58, "非线性缩放", 36, BLUE, "middle", "bold")
s.text(400, 104, "阈值五百四十对应不可重复率百分之五", 30, INK, "middle")

# ---------------- 坐标框 ----------------
L, R, B, T = 140, 690, 566, 196
YMAX = 900.0
lo, hi = math.log10(0.01), math.log10(0.5)


def px(x):
    return L + (R - L) * (math.log10(x) - lo) / (hi - lo)


def py(y):
    return B - (B - T) * y / YMAX


s.line(L, B, R, B, INK, 4)
s.line(L, B, L, T, INK, 4)
s.text(R, B + 92, "IDR", 30, GRAY, "middle")
s.text(L - 4, T - 24, "scaled", 30, GRAY, "start")

for x in (0.01, 0.05, 0.10, 0.25, 0.50):
    s.line(px(x), B, px(x), B + 8, INK, 3)
    s.text(px(x), B + 42, f"{x:.2f}", 30, GRAY, "middle")
for y in (300, 600, 900):
    s.line(L, py(y), L - 8, py(y), INK, 3)
    s.text(L - 16, py(y) + 10, str(y), 30, GRAY, "end")

# ---------------- 曲线：log 横轴上是直线 ----------------
s.line(px(0.01), py(-125.0 * math.log(0.01, FACTOR)),
       px(0.50), py(-125.0 * math.log(0.50, FACTOR)), BLUE, 7)

# ---------------- 门槛：x=0.05 → y=540 ----------------
cx, cy = px(P_CUT), py(Y_AT_CUT)
s.path(f"M {cx} {cy} L {cx} {B} M {L} {cy} L {cx} {cy}", RED, 5, dash="15 11")
s.circle(cx, cy, 13, RED)
s.text(cx - 34, cy + 54, "540", 34, BLUE, "end", "bold")
s.text(cx + 30, B - 66, "p = 0.05", 30, GRAY, "start")

s.save("06_scaled_idr_threshold.svg")

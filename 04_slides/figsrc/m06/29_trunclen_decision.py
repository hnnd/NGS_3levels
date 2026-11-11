#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""29_trunclen_decision.py — FIG-M06-29 质量谱截断位点决策图

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-29（P50，cols 一栏 800×700，new-svg）。
教材依据：§18.4.3（`plotQualityProfile` 三组线，看橙色中位数线定 `truncLen`，不看绿均值线）、
§18.5.1 / §18.4.1（截断过度会丢重叠；在 R2 尾部质量断崖之前截断才保住合并）。
图内汉字 = 方案原句逐字，共 19 字（看橙线中位数 / 尾部断崖前截断 / 保住有效重叠）；
其余为坐标 Q、读段位置 1–250、cut 200 / cut 240 与重叠算式 `overlap 148 ≥ 12`。
质量谱为示意曲线，不是实测数据（无随机数、无网络）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 29_trunclen_decision.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

s.text(400, 58, "quality profile", 34, BLUE, "middle", "bold")

# 绘图区
L, R, B, T = 136, 664, 462, 200
NM = 250
CUT1, CUT2 = 240, 200


def X(pos):
    return L + (pos - 1) / (NM - 1) * (R - L)


def Y(q):
    return B - (q - 12) / 30 * (B - T)


# 左右两区：截断前保留（绿）／R2 尾部断崖丢弃（红）
s.rect(L, T, X(CUT2) - L, B - T, GREEN_TINT)
s.rect(X(CUT2), T, R - X(CUT2), B - T, RED_TINT)

# 坐标轴
s.line(L, B, R, B, BLUE, 3)
s.line(L, B, L, T, BLUE, 3)

# 曲线（示意）
R1 = [(1, 37.6), (60, 37.2), (120, 36.6), (190, 35.6), (240, 34.6), (250, 34.4)]
R2 = [(1, 34.4), (60, 33.2), (120, 30.8), (170, 26.6), (200, 22.0),
      (216, 17.4), (236, 14.2), (250, 13.6)]

s.curve([(X(p), Y(q)) for p, q in R1], BLUE, 5)
s.curve([(X(p), Y(q)) for p, q in R2], ORANGE_DEEP, 5)

# 截断虚线：R2 在断崖前 200，R1 在 240
s.line(X(CUT2), T + 8, X(CUT2), B, RED, 4, dash="10 8")
s.line(X(CUT1), T + 8, X(CUT1), B, BLUE, 3, dash="10 8")

# 刻线
for pos in (50, 100, 150, 200, 250):
    s.line(X(pos), B, X(pos), B + 10, INK, 3)
    s.text(X(pos), B + 42, str(pos), 30, GRAY, "middle")
for q in (15, 25, 35):
    s.line(L, Y(q), L - 10, Y(q), INK, 3)
    s.text(L - 16, Y(q) + 11, f"Q{q}", 30, GRAY, "end")

# 两条曲线的端名
s.text(X(72), 228, "R1", 30, BLUE, "middle", "bold")
s.text(X(72), 300, "R2", 30, ORANGE_DEEP, "middle", "bold")

# 截断位点标注
s.text(X(CUT2) - 12, 190, "cut 200", 30, RED, "end")
s.text(X(CUT1) + 12, 190, "cut 240", 30, BLUE, "start")

# ---------------- 结论（方案原句）----------------
s.chip(280, 118, "看橙线中位数", 30, ORANGE_TINT, ORANGE_DEEP, INK)

s.text(400, 556, "尾部断崖前截断", 30, ORANGE_DEEP, "middle", "bold")
s.text(258, 640, "保住有效重叠", 32, GREEN, "middle", "bold")
s.chip(588, 640, "overlap 148 ≥ 12", 30, GREEN_TINT, GREEN, INK)

s.save("29_trunclen_decision.svg")

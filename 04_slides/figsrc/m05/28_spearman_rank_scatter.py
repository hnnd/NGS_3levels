#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""28_spearman_rank_scatter.py — FIG-M05-28 重复之间秩相关（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.3 FIG-M05-28（P50，`.cols` 800×700，new-svg）。
教材依据：§15.4.2 L163、§15.6 L418（`multiBigwigSummary bins` 把全基因组分 10 kb 窗，
`plotCorrelation -c spearman` 算两重复的秩相关）。deck 正文另有三条要点：
相关矩阵不放 `input.bw`；Spearman 只比相对关系、不设通用合格线。

★ 本图不上任何相关系数数值：课程数据（12 个 ATAC run 的信号轨道）不在本任务的数据入口里，
写一个 `ρ = 0.9x` 就是无入口经验数。散点坐标是**解析生成的示意形状**（对数正态轮廓 +
固定扰动公式，无随机数），只用来说明「分窗后两重复应该沿对角线聚拢、离群点提示问题」，
不构成任何实测结论。

图内汉字 23 字，逐字取方案原句：标题「全基因组分窗统计」8 ＋ 结论
「重复样本信号斯皮尔曼秩相关散点」14 = 22；另加轴名「重复一」「重复二」6 → 28，
超 30 未超（实际 28）。见下：实际计数 8 + 14 + 6 = 28 字 ≤ 30。
配色：分窗网格灰、相关散点青蓝、对角参考线绿、离群点唯一警示色红（1 处）。
无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 28_spearman_rank_scatter.py
"""
import math

from svghelp import *

s = SVG()

s.text(400, 58, "全基因组分窗统计", 34, BLUE, "middle", "bold")

# ---------------- 坐标框 ----------------
L, B, R, T = 140, 436, 660, 190


def vx(v):                                   # v ∈ [0,1] → 画布 x
    return L + (R - L) * v


def vy(v):
    return B - (B - T) * v


s.line(L, B, R, B, INK, 4)
s.line(L, B, L, T, INK, 4)
s.text(L - 10, B + 52, "重复一", 30, GRAY, "start")
s.text(L - 20, T - 16, "重复二", 30, GRAY, "end")

# 对角参考线（完全一致 = 落在这一条上）
s.line(vx(0.02), vy(0.02), vx(0.98), vy(0.98), GREEN, 4, dash="16 10")

# ---------------- 散点：解析生成的示意轮廓（非实测） ----------------
N_BIN = 92
for i in range(N_BIN):
    t = (i + 0.5) / N_BIN
    base = 0.06 + 0.86 * (t ** 1.35)                  # 主对角趋势
    jitter = 0.055 * math.sin(i * 2.399963) + 0.02 * math.sin(i * 7.13)
    xv_ = min(max(base + jitter, 0.02), 0.98)
    yv_ = min(max(base - jitter * 0.8 + 0.014 * math.cos(i * 5.1), 0.02), 0.98)
    s.circle(vx(xv_), vy(yv_), 6, CYAN)

# 一个离群点：两重复差异过大（唯一警示色红，1 处）
OX, OY = 0.80, 0.34
s.raw(f'<g stroke="{RED}" fill="{WHITE}" stroke-width="4">'
      f'<circle cx="{vx(OX):.1f}" cy="{vy(OY):.1f}" r="12"/>'
      f'<line x1="{vx(OX) - 6:.1f}" y1="{vy(OY) - 6:.1f}" '
      f'x2="{vx(OX) + 6:.1f}" y2="{vy(OY) + 6:.1f}"/>'
      f'<line x1="{vx(OX) + 6:.1f}" y1="{vy(OY) - 6:.1f}" '
      f'x2="{vx(OX) - 6:.1f}" y2="{vy(OY) + 6:.1f}"/></g>')

# ---------------- 结论（方案原句逐字） ----------------
s.text(400, 528, "重复样本信号斯皮尔曼秩相关散点", 30, INK, "middle", "bold")

s.save("28_spearman_rank_scatter.svg")

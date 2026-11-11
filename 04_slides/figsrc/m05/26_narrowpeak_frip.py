#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""26_narrowpeak_frip.py — FIG-M05-26 narrowPeak 十列格式与 FRiP（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.3 FIG-M05-26（P48，`.cols` 800×700，new-svg）。
教材依据：§15.4.4 L221、§15.6 L415–L417。narrowPeak 十列 = 染色体、起点、终点、名称、
score、链、fold enrichment、−log10(p)、−log10(q)、summit 相对偏移；`--broad` 输出的
broadPeak 只有九列、没有第 10 列 summit。FRiP = 落在峰内的读段数 ÷ 总比对读段数。

图面只画格式与占比关系，不写任何 FRiP 数值：本图无 data-plot 数据入口，
写数字会变成无入口经验数（与 ALN 撤下口径 W4 同源的问题）。
上部：十列表头（1–10）与三行表体，第 10 列（summit 偏移）全线青蓝，一眼看出
「broadPeak 缺的就是这一列」；表体下方画峰轮廓，峰顶竖线正对第 10 列。
右侧：环形图用绿弧表示「落峰读段」、灰环表示「其余比对读段」，环内只写 `FRiP`
（示意占比关系，不代表任何实测比例）。

图内汉字 20 字，逐字取方案原句：标题「峰表格式」4 ＋ 结论「十列标准区间」6
＋「统计落入峰区读段占比」10 = 20。
配色：固定列深蓝、峰顶列青蓝、FRiP 占比绿。无警示语义，红不上图。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 26_narrowpeak_frip.py
"""
import math

from svghelp import *

s = SVG()

s.text(400, 62, "峰表格式", 36, BLUE, "middle", "bold")

# ---------------- 十列表头 + 三行表体 ----------------
NCOL, TX, TY = 10, 36, 152
CW, CH, ROW_H = 50, 40, 46
for c in range(NCOL):
    x = TX + c * CW
    s.rect(x, TY, CW - 4, CH, CYAN if c == NCOL - 1 else BLUE, None, rx=5)
    s.text(x + (CW - 4) / 2, TY + 28, str(c + 1), 30, WHITE, "middle", "bold")

for r in range(3):                             # 三行示例数据（占位条，不含编造数字）
    y = TY + CH + 10 + r * ROW_H
    for c in range(NCOL):
        x = TX + c * CW
        s.rect(x, y, CW - 4, ROW_H - 12,
               CYAN_DEEP if c == NCOL - 1 else PANEL, None, rx=4)

# ---------------- 峰轮廓：峰顶正对第 10 列 ----------------
PX0, PX1, PB = TX + 40, TX + 8 * CW, 470
pts = []
for i in range(0, 121):
    frac = i / 120.0
    x = PX0 + (PX1 - PX0) * frac
    h = 118 * math.exp(-((frac - 0.62) / 0.17) ** 2)
    pts.append((x, PB - h))
s.curve(pts, CYAN, 5)
s.line(PX0, PB, PX1, PB, GRAY, 4)

SUM_X = PX0 + (PX1 - PX0) * 0.62                # summit 位置（峰顶）
s.line(SUM_X, PB - 140, SUM_X, PB + 14, CYAN_DEEP, 5, dash="12 8")
s.line(SUM_X, PB - 140, TX + 9 * CW + 18, TY + CH + 10 + 3 * ROW_H + 14,
       CYAN_DEEP, 3, dash="8 8")

# ---------------- 右侧：FRiP 环形占比 ----------------
CX, CY, RR, RW = 690, 236, 74, 30
s.circle(CX, CY, RR, "none", PANEL, RW)
FRAC = 0.25                                   # 示意占比（非实测）
A0 = -math.pi / 2
A1 = A0 + 2 * math.pi * FRAC
p0 = (CX + RR * math.cos(A0), CY + RR * math.sin(A0))
p1 = (CX + RR * math.cos(A1), CY + RR * math.sin(A1))
s.path(f"M {p0[0]:.1f} {p0[1]:.1f} A {RR} {RR} 0 0 1 {p1[0]:.1f} {p1[1]:.1f}",
       GREEN, RW)
s.text(CX, CY + 10, "FRiP", 30, GREEN, "middle", "bold")

# ---------------- 结论（方案原句逐字） ----------------
s.text(400, 606, "十列标准区间", 32, BLUE, "middle", "bold")
s.text(400, 660, "统计落入峰区读段占比", 32, INK, "middle", "bold")

s.save("26_narrowpeak_frip.svg")

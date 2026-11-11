#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""27_bigwig_tss_heatmap.py — FIG-M05-27 信号轨道与 TSS 热图（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.3 FIG-M05-27（P49，`.cols` 800×700，new-svg）。
教材依据：§15.6 L417–L418（`bamCoverage --binSize 10 --normalizeUsing RPGC` 出 bigWig
单轨；`computeMatrix reference-point --referencePoint TSS -b 3000 -a 3000` 把全基因组
基因的 TSS ±3 kb 信号对齐堆叠成矩阵；`plotHeatmap` 画矩阵）。PPT 正文另有一条要点：
「热图不是 TSSE：它不给数值分数」。

图面两段：上为 bigWig 单轨（RPGC 归一的连续波形，两个峰）；下为 computeMatrix 堆叠出的
热图矩阵（每行一个基因、默认按信号强度排序——上行最强、下行最弱；列由左到右是
−3 kb → TSS → +3 kb，TSS 列居中且信号最强，向两侧衰减）。
热图行列用 18 行 × 42 列示意，不标任何基因数、倍数与分值：本图无数据入口，不上数字。

图内汉字 22 字，逐字取方案原句：标题「信号矩阵」4 ＋ 结论「全基因组区间标准化堆叠」11
＋「绘制起始区热图」7 = 22。
配色：信号波形青蓝、热图由浅黄至深蓝、TSS 参考点唯一警示色红（标记 + 竖线合成 1 处
图形 + 「TSS」标签 1 处 = 2 处，在每图 ≤ 2 处的上限内）。
波形与矩阵为解析函数生成的示意形状，无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 27_bigwig_tss_heatmap.py
"""
import math

from svghelp import *

s = SVG()

s.text(400, 60, "信号矩阵", 36, BLUE, "middle", "bold")

# ---------------- 上：bigWig 单轨 ----------------
AX, AY, AW, AMP = 56, 168, 688, 86
s.line(AX, AY, AX + AW, AY, GRAY, 4)
d = f"M {AX} {AY}"
for i in range(0, 161):
    frac = i / 160.0
    v = (0.52 * math.exp(-((frac - 0.25) / 0.058) ** 2)
         + 0.82 * math.exp(-((frac - 0.67) / 0.048) ** 2) + 0.08)
    d += f" L {AX + AW * frac:.1f} {AY - AMP * v:.1f}"
d += f" L {AX + AW} {AY} Z"
s.path(d, CYAN, 2, fill=CYAN)

# ---------------- 下：computeMatrix 堆叠热图 ----------------
HX, HY, HW, HH = 56, 306, 688, 168
NROW, NCOL = 18, 42
RH, CWID = HH / NROW, HW / NCOL
s.rect(HX - 8, HY - 8, HW + 16, HH + 16, WHITE, PANEL, 3, rx=10)

TSS_FRAC = 0.5                                   # referencePoint=TSS，居中
TSS_X = HX + HW * TSS_FRAC


def ramp(v):
    """浅黄 → 深蓝 的插值（v ∈ [0,1]）。"""
    c0, c1 = (0xFC, 0xF0, 0xC4), (0x3C, 0x54, 0x88)
    r, g, b = (round(c0[i] + (c1[i] - c0[i]) * v) for i in range(3))
    return f"#{r:02X}{g:02X}{b:02X}"


for ri in range(NROW):
    strength = 1.0 - ri / (NROW + 2.0)           # 上行最强，下行最弱（按强度排序）
    for ci in range(NCOL):
        frac = (ci + 0.5) / NCOL
        v = strength * math.exp(-((frac - TSS_FRAC) / 0.22) ** 2) * 1.15
        s.rect(HX + ci * CWID, HY + ri * RH, CWID, RH,
               ramp(min(v, 1.0)), None)

# TSS 参考点（红：竖线 + 顶部三角合成 1 个 <g>；标签另计 1 处 = 2 处）
s.raw(f'<g stroke="{RED}" fill="{RED}">'
      f'<line x1="{TSS_X:.1f}" y1="{HY - 18}" x2="{TSS_X:.1f}" y2="{HY + HH + 18}" '
      f'stroke-width="5"/>'
      f'<polygon points="{TSS_X:.1f},{HY - 34} {TSS_X - 13:.1f},{HY - 14} '
      f'{TSS_X + 13:.1f},{HY - 14}"/></g>')
s.text(TSS_X + 24, HY + HH + 52, "TSS", 30, RED, "start", "bold")

# bigWig → 矩阵（同一份信号被对齐堆叠）
s.arrow(400, AY + 10, 400, HY - 44, GRAY, 5, 16)

# ---------------- 结论（方案原句逐字） ----------------
s.text(400, 566, "全基因组区间标准化堆叠", 32, INK, "middle", "bold")
s.text(400, 626, "绘制起始区热图", 32, BLUE, "middle", "bold")

s.save("27_bigwig_tss_heatmap.svg")

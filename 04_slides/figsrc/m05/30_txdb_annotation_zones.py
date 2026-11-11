#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""30_txdb_annotation_zones.py — FIG-M05-30 TxDb 注释峰分布（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.3 FIG-M05-30（P52，`.cols` 800×700，new-svg）。
教材依据：§15.4.5 L245–L248、§15.6 L419–L420。ChIPseeker 把每个峰投到注释上，判断它落在
启动子（`tssRegion = c(-3000, 3000)` 定义的窗口）、5′UTR、外显子、内含子、3′UTR 还是远端
基因间区，再把最近 TSS 的基因写成关联基因 [@yu2015chipseeker] [@chipseeker2026source]。

图面两段：上为基因结构区划（启动子 / 外显子 / 内含子 / 基因间区四色带，TSS 竖线与虚线框
标出启动子窗口 `−3 kb…+3 kb` 的判定优先级）；下为同一四色的环状占比图，表示峰在各区划的
分布。环图只示意「各区划都有峰、启动子与内含子占大头」的相对关系，**不写任何百分比**：
本图无 data-plot 数据入口，写数字会变成无入口经验数（与 FIG-M05-26 同一口径）。

图内汉字 24 字（上限 30）：标题「基因组区划」5 ＋ 区带名「基因间区」4「启动子」3
「外显子」3「内含子」3 ＋ 结论「峰按区划归类」6；TSS 写拉丁字符。
5′UTR／3′UTR 在图上并入启动子窗口与外显子侧翼，不单列色带：方案列出的六类区划里，
这两类从属于转录本的 UTR 判定，单列会把四个主色带压到不足一条读长的宽度，
且要多出两条区名，直接顶破 30 汉字上限（与图 18／19／20 同样的取舍）。
配色按方案：启动子绿 `#00A087`、外显子青蓝 `#4DBBD5`、内含子紫 `#8491B4`、
基因间区橙 `#F39B7F`。无警示语义，红不上图。无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 30_txdb_annotation_zones.py
"""
import math

from svghelp import *

s = SVG()

s.text(400, 62, "基因组区划", 36, BLUE, "middle", "bold")

# ---------------- 上：基因结构区划（四色带） ----------------
BASE, HZ = 272, 76
ZONES = [(40, 200, ORANGE), (200, 348, GREEN), (352, 500, CYAN),
         (504, 640, PURPLE), (672, 760, ORANGE)]
for x0, x1, color in ZONES:
    s.rect(x0, BASE - HZ, x1 - x0, HZ, color, None, rx=8)
s.rect(196, BASE - HZ - 6, 152, HZ + 12, "none", GREEN, 5, dash="15 10")
s.line(200, BASE - HZ - 34, 200, BASE + 16, INK, 5)          # TSS
s.text(190, BASE - HZ - 46, "TSS", 30, INK, "end", "bold")

# 区带名（逐字取方案原句）
s.text(120, BASE + 54, "基因间区", 30, ORANGE, "middle", "bold")
s.text(274, BASE + 54, "启动子", 30, GREEN, "middle", "bold")
s.text(426, BASE + 54, "外显子", 30, CYAN_DEEP, "middle", "bold")
s.text(572, BASE + 54, "内含子", 30, PURPLE, "middle", "bold")

# ---------------- 下：同一四色的环状占比（不含数字） ----------------
CX, CY, R_OUT, R_IN = 400, 486, 106, 60
FRACS = [(GREEN, 0.22), (CYAN, 0.30), (PURPLE, 0.28), (ORANGE, 0.20)]
assert abs(sum(f for _, f in FRACS) - 1.0) < 1e-9


def ring_sector(a0_deg, a1_deg, color):
    """环扇形：外弧 → 内弧 → 闭合。角度以 12 点方向为 0、顺时针增大。"""
    a0, a1 = math.radians(a0_deg - 90), math.radians(a1_deg - 90)
    ox0, oy0 = CX + R_OUT * math.cos(a0), CY + R_OUT * math.sin(a0)
    ox1, oy1 = CX + R_OUT * math.cos(a1), CY + R_OUT * math.sin(a1)
    ix1, iy1 = CX + R_IN * math.cos(a1), CY + R_IN * math.sin(a1)
    ix0, iy0 = CX + R_IN * math.cos(a0), CY + R_IN * math.sin(a0)
    large = 1 if (a1_deg - a0_deg) > 180 else 0
    d = (f"M {ox0:.1f} {oy0:.1f} "
         f"A {R_OUT} {R_OUT} 0 {large} 1 {ox1:.1f} {oy1:.1f} "
         f"L {ix1:.1f} {iy1:.1f} "
         f"A {R_IN} {R_IN} 0 {large} 0 {ix0:.1f} {iy0:.1f} Z")
    s.path(d, None, 0, fill=color)


start = 0.0
for color, frac in FRACS:
    end = start + 360.0 * frac
    ring_sector(start, end, color)
    start = end
s.circle(CX, CY, R_IN, PAPER)                     # 中点留白（环图，不是饼图）

# ---------------- 结论（方案原句逐字） ----------------
s.text(400, 648, "峰按区划归类", 32, INK, "middle", "bold")

s.save("30_txdb_annotation_zones.svg")
print("check: 四色环占比 " + " ".join(f"{f:.2f}" for _, f in FRACS)
      + "（示意图，不标百分比）")

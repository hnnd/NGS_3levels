#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_diffpeak_union_nb.py — FIG-M05-16 差异峰：并集 + 负二项检验（流程）

方案：`reviews/course/M05_FIGP_001.md` §4.2 FIG-M05-16（P36，`.cols` 800×700，new-svg）。
教材依据：§15.4.7 L284–L290（先把所有样本峰取并集得一致峰集，再对每个区间数
各样本读段数，套负二项检验；DiffBind / csaw 不在课程环境，见 P55 警告卡）。
方案原句 22 字逐字上图：标题「差异分析」4；结论两行「取并集构建一致峰」8、
「统计读段做负二项检验」10；另加「并集」2 → 24 字。
A/B 两个样本、计数矩阵数字与工具名 DESeq2 用英文/数字，不计汉字。
矩阵里的计数是示意占位（不构成任何实测结论），不上「倍」数、不写差异倍数。
红不上图（本图无警示语义）：样本峰青蓝/紫，并集深蓝，检验绿色。
纯流程示意，无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 16_diffpeak_union_nb.py
"""
from svghelp import *

s = SVG()

s.text(400, 64, "差异分析", 36, BLUE, "middle", "bold")

# ---------------- 上行：两个样本各自的峰集 ----------------
ROW_H = 58
Y_A, Y_B = 128, 214
PEAKS_A = [(96, 74), (216, 52), (322, 96), (486, 62), (618, 78)]
PEAKS_B = [(120, 60), (240, 88), (356, 54), (508, 96), (646, 56)]
for y, peaks, color, tag in ((Y_A, PEAKS_A, CYAN, "A"), (Y_B, PEAKS_B, PURPLE, "B")):
    s.text(72, y + ROW_H / 2 + 12, tag, 32, color, "end", "bold")
    s.line(88, y + ROW_H, 712, y + ROW_H, PANEL, 4)
    for x, w in peaks:
        s.rect(x, y, w, ROW_H - 10, color, None, rx=8)

# ---------------- 中行：并集（两样本峰区间取并） ----------------
Y_U = 316
UNION = [(96, 98), (216, 76), (322, 96), (486, 62), (508, 96),
         (618, 96), (646, 56)]
s.text(72, Y_U + ROW_H / 2 + 12, "∪", 34, BLUE, "end", "bold")
s.line(88, Y_U + ROW_H, 712, Y_U + ROW_H, PANEL, 4)
for x, w in UNION:
    s.rect(x, Y_U, w, ROW_H - 10, BLUE_TINT, BLUE, 3, rx=8)
s.text(96, Y_U - 16, "并集", 30, BLUE, "start", "bold")

# 两个样本行 → 并集行
for y in (Y_A, Y_B):
    s.arrow(796 - 40, y + ROW_H + 4, 796 - 40, Y_U - 8, GRAY, 5, 14)

# ---------------- 下行左：区间计数矩阵 ----------------
MX, MY, CW2, CH2 = 96, 404, 132, 42
s.rect(MX - 14, MY - 14, 2 * CW2 + 28, 3 * CH2 + 28, WHITE, PANEL, 3, rx=12)
for r in range(3):
    for c in range(2):
        s.rect(MX + c * CW2, MY + r * CH2, CW2, CH2, BLUE_TINT, BLUE, 2, rx=4)
s.text(MX + CW2 / 2, MY + CH2 + 10, "A", 30, BLUE, "middle", "bold")
s.text(MX + 1.5 * CW2, MY + CH2 + 10, "B", 30, PURPLE, "middle", "bold")

# 并集 → 计数矩阵
s.arrow(MX + CW2, Y_U + ROW_H + 4, MX + CW2, MY - 20, GRAY, 5, 14)

# ---------------- 下行右：负二项检验 ----------------
BX, BY, BW, BH = 452, 404, 300, 130
s.rect(BX, BY, BW, BH, GREEN_TINT, GREEN, 4, rx=14)
s.text(BX + BW / 2, BY + 52, "DESeq2", 34, GREEN, "middle", "bold")
s.text(BX + BW / 2, BY + 100, "负二项", 30, GREEN, "middle")
s.arrow(MX + 2 * CW2 + 22, BY + BH / 2, BX - 10, BY + BH / 2, GRAY, 5, 14)

# ---------------- 结论行（方案原句逐字） ----------------
s.text(400, 600, "取并集构建一致峰", 32, BLUE, "middle", "bold")
s.text(400, 654, "统计读段做负二项检验", 32, INK, "middle", "bold")

s.save("16_diffpeak_union_nb.svg")

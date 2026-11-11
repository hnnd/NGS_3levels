#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-18 表达矩阵五种形态与下游去向。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-18；配色：spec.md §2。
依据：教材 §14.4.7，讲义 ④4.4。"""
from svghelp import *

s = SVG()

forms = [("raw counts", GREEN),
         ("归一化", BLUE),
         ("vst", CYAN_DEEP),
         ("rlog", CYAN_DEEP),
         ("TPM / FPKM", ORANGE)]
x0, y0, rh = 40, 104, 86
for i, (name, col) in enumerate(forms):
    y = y0 + i * rh
    s.rect(x0, y, 210, 70, WHITE, col, 5, rx=12)
    s.text(x0 + 105, y + 46, name, 30, col, "middle", "bold")

# 下游去向（caption 在目标框上方）
def target(y, cap, capcol, title, sub, col):
    s.text(500, y - 14, cap, 30, capcol, "start", "bold")
    s.rect(470, y, 290, 112, WHITE, col, 5, rx=14)
    s.text(615, y + 44, title, 30, col, "middle", "bold")
    s.text(615, y + 82, sub, 30, GRAY, "middle")

target(100, "原始整数建模检验", GREEN, "DESeq2 / edgeR", "只收原始计数",
       GREEN)
target(282, "归一化跨样本比", BLUE, "跨样本比较", "已除文库因子",
       BLUE)
target(464, "对数变换聚类", CYAN_DEEP, "PCA · 热图", "聚类 · 机器学习",
       CYAN_DEEP)

s.arrow(250, 139, 466, 144, GREEN, 6, 15)
s.arrow(250, 225, 466, 326, BLUE, 6, 15)
s.arrow(250, 397, 466, 508, CYAN_DEEP, 6, 15)

# TPM 注 + 红色阻断
s.text(60, 560, "相对丰度慎用", 30, ORANGE, "start", "bold")
s.rect(40, 600, 720, 84, RED_TINT, RED, 6, rx=14)
s.path("M 66 618 L 92 666 M 92 618 L 66 666", RED, 7)
s.text(116, 636, "round(TPM) → DESeq2", 32, INK, "start", "bold")
s.text(116, 668, "方差结构被破坏 · 假阳性失控", 30, INK, "start")

s.save("18_matrix_forms_downstream.svg")

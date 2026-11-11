#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-24 端到端六步分析流程泳道。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-24；配色：spec.md §2。
依据：教材 §14.6，讲义 ⑤。"""
from svghelp import *

s = SVG()

steps = [
    ("①", "质控过滤", "fastp", "FASTQ"),
    ("②", "准比对定量", "Salmon", "quant.sf"),
    ("③", "长度校正", "tximport", "cts + coldata"),
    ("④", "负二项建模", "DESeq2", "res 结果表"),
    ("⑤", "诊断筛选", "PCA · 火山图", "质控通过"),
    ("⑥", "功能富集", "enrichGO", "候选清单"),
]
bw, bh = 230, 150
# 布局：S 形两行三列
coords = [(40, 110), (290, 110), (540, 110), (540, 390), (290, 390), (40, 390)]
for (num, name, tool, prod), (x, y) in zip(steps, coords):
    s.rect(x, y, bw, bh, WHITE, BLUE, 5, rx=14)
    s.rect(x, y, bw, 44, BLUE_TINT, None, rx=14)
    s.text(x + 20, y + 33, num, 30, BLUE, "start", "bold")
    s.text(x + bw / 2 + 14, y + 33, name, 30, BLUE, "middle", "bold")
    s.text(x + bw / 2, y + 86, tool, 30, INK, "middle")
    s.text(x + bw / 2, y + 126, prod, 30, GRAY, "middle")
# 箭头 ①→②→③→④→⑤→⑥
s.arrow(272, 185, 286, 185, GRAY, 6, 14)
s.arrow(522, 185, 536, 185, GRAY, 6, 14)
s.arrow(655, 262, 655, 386, GRAY, 6, 14)
s.arrow(536, 465, 522, 465, GRAY, 6, 14)
s.arrow(286, 465, 272, 465, GRAY, 6, 14)
# 起点与终点
s.text(40, 84, "输入： 原始 FASTQ", 30, GRAY, "start")
s.text(40, 592, "输出： 候选基因清单", 30, GREEN, "start", "bold")

s.save("24_rnaseq_six_steps_swimlane.svg")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-17 padj = NA 三种成因判定树。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-17；配色：spec.md §2。
依据：教材 §14.4.6，讲义 ④4.4。Cook's 距离需同格 ≥3 样本，本课每格 2 样本不触发。"""
from svghelp import *

s = SVG()

# 根节点
s.rect(250, 60, 300, 70, BLUE, None, rx=12)
s.text(400, 106, "padj = NA ?", 32, WHITE, "middle", "bold")

branches = [
    (130, "baseMean = 0", "全部计数为零", "pvalue 同为 NA", CYAN,
     "全零行无信息"),
    (400, "Cook 离群点", "需同格 ≥ 3 样本", "2 重复： 不触发",
     ORANGE, "离群点需多重复"),
    (670, "独立过滤", "均值极低", "仅 padj = NA",
     GREEN, "低表达独立过滤"),
]
for cx, t1, t2, t3, col, cap in branches:
    s.arrow(400, 130, cx, 208, GRAY, 5, 13)
    s.rect(cx - 125, 212, 250, 152, WHITE, col, 5, rx=12)
    s.text(cx, 252, t1, 30, col, "middle", "bold")
    s.text(cx, 296, t2, 30, INK, "middle")
    s.text(cx, 336, t3, 30, GRAY, "middle")
    s.text(cx, 416, cap, 30, INK, "middle", "bold")

# 结论条
s.rect(90, 470, 620, 66, BLUE_TINT, BLUE, 5, rx=12)
s.text(400, 515, "仅校正值为空", 30, BLUE, "middle", "bold")
s.text(400, 580, "成批 NA → 成因 ① 或 ③", 30, GRAY, "middle")
s.rect(90, 614, 620, 62, GREEN_TINT, GREEN, 4, rx=10)
s.text(400, 657, "排除②： 每格仅 2 重复", 30, GREEN, "middle")

s.save("17_padj_na_decision_tree.svg")

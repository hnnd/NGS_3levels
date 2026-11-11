#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-26 映射率偏低四层诊断排查树。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-26；配色：spec.md §2。
依据：教材 §14.4.9，讲义 ⑥6.1。"""
from svghelp import *

s = SVG()

# 根节点
s.rect(230, 56, 340, 72, BLUE, None, rx=12)
s.text(400, 102, "映射率偏低", 32, WHITE, "middle", "bold")

nodes = [
    (110, "fastp", "报告", "接头与低质量", CYAN_DEEP),
    (290, "链特异性", "参数设置", "链特异性参数核对", ORANGE),
    (510, "参考序列", "核对", "参考序列物种版本", PURPLE),
    (690, "rRNA", "去除", "核糖体残留排查", GREEN),
]
for cx, w1, w2, cap, col in nodes:
    s.arrow(400, 128, cx, 196, GRAY, 5, 13)
    s.rect(cx - 88, 200, 176, 130, WHITE, col, 5, rx=12)
    s.text(cx, 248, w1, 30, col, "middle", "bold")
    s.text(cx, 288, w2, 30, col, "middle", "bold")

# 中文标注（两行交错，防重叠；与各自节点中心对齐）
s.text(110, 372, "接头与低质量", 30, INK, "middle", "bold")
s.text(510, 372, "参考序列物种版本", 30, INK, "middle", "bold")
s.text(290, 424, "链特异性参数核对", 30, INK, "middle", "bold")
s.text(690, 424, "核糖体残留排查", 30, INK, "middle", "bold")

# 底部读法
s.rect(60, 470, 680, 74, BLUE_TINT, BLUE, 5, rx=12)
s.text(400, 517, "按序排查 ① → ④", 30, BLUE, "middle", "bold")
s.rect(60, 568, 680, 88, RED_TINT, RED, 5, rx=12)
s.text(120, 606, "链型设反", 30, INK, "start", "bold")
s.text(120, 640, "→ 映射率腰斩", 30, INK, "start")
s.text(500, 624, "先查②", 30, GRAY, "middle", "bold")

s.save("26_mapping_rate_troubleshooting.svg")

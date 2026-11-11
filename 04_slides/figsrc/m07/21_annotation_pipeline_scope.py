#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""21_annotation_pipeline_scope.py — FIG-M07-23 宏基因组功能注释链路与执行边界

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-23（P40，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.6（课程脚本把 contigs 直接交给 eggNOG-mapper，跳过 Prodigal 蛋白预测那一步；
分配的 KO/通路只是「基因潜力」；未注释比例高属正常）。
版式：主链靠左（contigs → eggNOG-mapper → 代谢通路），右侧旁挂「跳过蛋白预测」旁路标签，
未注释出口用灰色虚线回落（不写字，汉字预算已满）。
图内汉字 = 方案清单逐字，共 26 字（重叠群直接注释 / 跳过蛋白预测 / 分配代谢通路 /
大半未知属正常）。eggNOG-mapper 为工具名（允许英文）。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 21_annotation_pipeline_scope.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 主链三段（靠左，cx = 240） ----------------
CX, BW = 240, 400
CHAIN = ((88, "重叠群直接注释", BLUE_TINT, BLUE, "contigs"),
         (256, "eggNOG-mapper", CYAN_TINT, CYAN_DEEP, "tool"),
         (424, "分配代谢通路", GREEN_TINT, GREEN, "path"))
BH = 108

for y, cap, tint, edge, kind in CHAIN:
    s.rect(CX - BW / 2, y, BW, BH, tint, edge, 4, rx=16)
    if kind == "contigs":
        s.text(CX, y + 46, cap, 30, edge, "middle", "bold")
        for i in range(4):                 # contigs 条形
            s.rect(CX - BW / 2 + 40, y + 66 + i * 9, BW - 80, 4, edge, rx=2)
    elif kind == "path":
        s.text(CX, y + 42, cap, 32, edge, "middle", "bold")
    else:
        s.text(CX, y + BH / 2 + 11, cap, 32, edge, "middle", "bold")

# 主链箭头
s.arrow(CX, CHAIN[0][0] + BH + 4, CX, CHAIN[1][0] - 6, CYAN_DEEP, 5, 14)
s.arrow(CX, CHAIN[1][0] + BH + 4, CX, CHAIN[2][0] - 6, GREEN, 5, 14)

# 通路入口的两条细条（示意通路层级，不写字）
for i, w in enumerate((150, 210, 270)):
    s.rect(CX - w / 2, CHAIN[2][0] + 64 + i * 14, w, 9, GREEN, rx=4)

# ---------------- 右侧旁路：跳过蛋白预测 ----------------
SKX, SKY = 620, 214
s.chip(SKX, SKY, "跳过蛋白预测", 30, WHITE, ORANGE_DEEP, ORANGE_DEEP,
       sw=3, rx=12)
# 旁路线：contigs 右缘 → 标签 → 注释器右缘（虚线示意绕过）
s.path(f"M {CX + BW / 2} {CHAIN[0][0] + 54} C 560 {CHAIN[0][0] + 54} "
       f"560 {SKY - 30} {SKX - 106} {SKY - 30}", ORANGE_DEEP, 4, dash="9 8")
s.path(f"M {SKX + 106} {SKY + 30} C 700 {SKY + 30} 700 {CHAIN[1][0] + 54} "
       f"{CX + BW / 2} {CHAIN[1][0] + 54}", ORANGE_DEEP, 4, dash="9 8")

# ---------------- 未注释出口：灰色虚线回落（无文字） ----------------
s.path(f"M {CX + BW / 2 + 4} {CHAIN[2][0] + 76} C 640 540 660 600 556 620",
       GRAY, 4, dash="10 9")

# ---------------- 红色语义组：大半未知属正常 ----------------
s.text(300, 636, "大半未知属正常", 34, RED, "middle", "bold")

s.save("21_annotation_pipeline_scope.svg")

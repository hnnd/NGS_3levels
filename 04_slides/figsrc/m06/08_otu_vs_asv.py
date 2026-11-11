#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_otu_vs_asv.py — FIG-M06-08 97% OTU 与单碱基 ASV 机制对比

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-08（P19，cols 一栏 800×700，new-svg）。
教材依据：§18.4.2（97% 聚类抹平 1–2 bp 误差、中心由最高丰度决定、不可跨研究；
ASV 以统计错误模型做单碱基分辨、序列即身份、跨研究可比）。
图内汉字 = 方案原句逐字，共 21 字（聚类抹平误差 6 / 不可跨研究 5 / 单碱基分辨 5 /
序列即身份 5）；其余标注为 97% / 100% / OTU / ASV。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 08_otu_vs_asv.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

LW = 356
LX, RX = 22, 422
LY, LH = 60, 580

for x in (LX, RX):
    s.rect(x, LY, LW, LH, WHITE, PANEL, 3, rx=16)

# ---------------- 左栏：OTU 97% 聚类 ----------------
LCX = LX + LW / 2
s.text(LCX, 116, "OTU", 34, BLUE, "middle", "bold")
s.text(LCX, 162, "97%", 30, GRAY, "middle")

# 聚类圈：圈住 4 条 1–2 bp 差异的序列
CCX, CCY, CR = LCX, 292, 104
s.circle(CCX, CCY, CR, ORANGE_TINT, ORANGE, 4, dash="12 8")

SEQ_X, SEQ_W = CCX - 80, 160
for i, y in enumerate((248, 276, 304, 332)):
    s.rect(SEQ_X, y, SEQ_W, 14, ORANGE_DEEP if i == 0 else ORANGE, None, 0, rx=4)
    if i:                                  # 误差位：白色小缺口
        s.rect(SEQ_X + 52 + i * 30, y, 14, 14, WHITE, None, 0, rx=2)

s.circle(CCX, 262, 11, BLUE)               # 中心 = 最高丰度序列

s.label(LCX, 448, wrap("聚类抹平误差", 32, LW - 56), 32, ORANGE_DEEP)
s.label(LCX, 528, wrap("不可跨研究", 32, LW - 56), 32, BLUE)

# ---------------- 右栏：ASV 单碱基分辨 ----------------
RCX = RX + LW / 2
s.text(RCX, 116, "ASV", 34, BLUE, "middle", "bold")
s.text(RCX, 162, "100%", 30, GRAY, "middle")

# 三条互不相同的序列条（每条一个不同碱基位置）
for i, y in enumerate((216, 268, 320)):
    s.rect(RCX - 92, y, 184, 14, CYAN, None, 0, rx=4)
    s.rect(RCX - 92 + 34 + i * 54, y, 14, 14, BLUE, None, 0, rx=2)

# 三条分别独立，之间无聚类圈（用浅色分隔虚线表示彼此独立）
for y in (246, 298):
    s.line(RCX - 100, y, RCX + 100, y, PANEL, 3, dash="8 8")

s.label(RCX, 448, wrap("单碱基分辨", 32, LW - 56), 32, CYAN_DEEP)
s.label(RCX, 528, wrap("序列即身份", 32, LW - 56), 32, GREEN)

s.save("08_otu_vs_asv.svg")

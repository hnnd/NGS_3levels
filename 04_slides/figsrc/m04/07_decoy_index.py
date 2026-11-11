#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-07 decoy 基因组诱饵捕获未剪接/假基因读段。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-07；配色：spec.md §2。
依据：教材 §14.4.2，讲义 ⑤5.2。"""
from svghelp import *

s = SVG()

# ---- 左：无诱饵，假基因读段硬比对到同源转录本 ----
s.label(200, 50, ["无诱饵假基因错配"], 30, BLUE, weight="bold")
# 基因组上的假基因（未剪接）
s.line(40, 122, 360, 122, GRAY, 4)
s.rect(90, 108, 180, 28, "none", ORANGE, 4, dash="10 8")
s.text(180, 100, "假基因（未剪接）", 30, ORANGE, "middle")
# 读段来自假基因
s.rect(110, 162, 120, 24, ORANGE, None)
s.text(250, 184, "读段", 30, GRAY, "start")
# 转录本库中无此位点 → 硬比对到同源转录本
s.line(40, 266, 360, 266, BLUE, 5)
for x0 in (70, 160, 250):
    s.rect(x0, 252, 70, 28, BLUE, None)
s.text(40, 240, "转录本索引", 30, GRAY, "start")
s.arrow(170, 190, 200, 246, ORANGE, 6, 15)
s.text(216, 224, "硬比对", 30, ORANGE, "start")
# 假阳性结果
s.rect(50, 314, 300, 112, RED_TINT, RED, 5, rx=12)
s.text(200, 358, "转录本 X", 30, INK, "middle")
s.rect(110, 374, 180, 18, ORANGE, None)
s.text(200, 416, "虚假高丰度", 30, GRAY, "middle")
s.path("M 104 470 L 128 494 M 128 470 L 104 494", RED, 6)
s.text(152, 490, "假阳性", 30, INK, "start", "bold")

# ---- 右：gentrome 诱饵捕获 ----
s.label(600, 50, ["诱饵基因组全捕获"], 30, GREEN, weight="bold")
# gentrome 索引：转录本 + 全基因组
s.rect(430, 92, 340, 76, BLUE_TINT, BLUE, 5, rx=10)
s.text(600, 126, "gentrome.fa", 30, BLUE, "middle", "bold")
s.text(600, 156, "转录本＋基因组", 30, GRAY, "middle")
# 同一读段被基因组诱饵吸收
s.rect(460, 206, 120, 24, ORANGE, None)
s.text(596, 228, "读段", 30, GRAY, "start")
s.line(430, 282, 770, 282, GREEN, 5)
s.rect(470, 268, 130, 28, GREEN, None)
s.rect(640, 268, 110, 28, "none", GREEN, 4, dash="10 8")
s.text(536, 254, "诱饵捕获", 30, GREEN, "start", "bold")
s.arrow(520, 232, 535, 264, GREEN, 6, 15)
# 转录本定量保持纯净
s.rect(460, 336, 280, 104, GREEN_TINT, GREEN, 5, rx=12)
s.text(600, 380, "转录本 X", 30, INK, "middle")
s.rect(500, 396, 120, 18, CYAN, None)
s.text(610, 478, "真实丰度", 30, GREEN, "middle", "bold")
s.polyline([(478, 464), (490, 476), (510, 452)], GREEN, 6, fill="none")

# ---- 底部结论 ----
s.label(400, 580, ["真实转录本定量纯净"], 32, INK, weight="bold")
s.text(400, 632, "decoy 索引（Salmon/STAR）", 30, GRAY, "middle")

s.save("07_decoy_index.svg")

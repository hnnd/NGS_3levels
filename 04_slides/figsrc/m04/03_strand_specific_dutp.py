#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-03 链特异性 dUTP 标记：分辨重叠反义转录本。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-03；配色：spec.md §2。
依据：教材 §14.4.1，讲义 ④4.1。"""
from svghelp import *

s = SVG()

# ---- 轨道 1：非链特异，重叠反义基因分不清 ----
s.label(400, 50, ["重叠转录本"], 32, BLUE, weight="bold")
s.line(60, 114, 740, 114, BLUE, 5)
s.polygon([(220, 114), (520, 114), (500, 100), (220, 100)], BLUE)   # 正义基因（→）
s.text(360, 90, "正义链", 30, BLUE, "middle")
s.line(60, 158, 740, 158, PURPLE, 5)
s.polygon([(520, 158), (220, 158), (240, 172), (520, 172)], PURPLE)  # 反义基因（←）
s.text(400, 200, "反义链", 30, PURPLE, "middle")
# 非链特异读段：方向混杂
for x, up in ((300, True), (340, False), (380, True), (420, False)):
    if up:
        s.polygon([(x, 218), (x + 14, 218), (x + 14, 236), (x + 22, 236),
                   (x + 7, 254), (x - 8, 236), (x, 236)], CYAN)
    else:
        s.polygon([(x, 254), (x + 14, 254), (x + 14, 236), (x + 22, 236),
                   (x + 7, 218), (x - 8, 236), (x, 236)], PURPLE)
s.circle(560, 236, 25, WHITE, RED, 6)
s.text(560, 247, "?", 36, RED, "middle", "bold")

# ---- 轨道 2：dUTP 标记，酶解第二链 ----
s.label(400, 326, ["掺入降解第二链"], 32, BLUE, weight="bold")
s.line(120, 396, 680, 396, CYAN_DEEP, 6, cap="round")          # 第一链（保留）
s.text(672, 382, "第一链", 30, CYAN_DEEP, "end")
s.line(120, 438, 560, 438, ORANGE, 6, cap="round")             # 第二链（被降解）
for x in (180, 320, 460):
    s.text(x + 10, 432, "dUTP", 30, ORANGE, "middle", "bold")
s.polyline([(560, 438), (590, 438), (610, 438)], ORANGE, 6, dash="10 12")
# 酶解剪刀
s.polyline([(600, 416), (622, 438), (600, 460)], GRAY, 6)
s.polyline([(644, 416), (622, 438), (644, 460)], GRAY, 6)
s.circle(622, 438, 7, GRAY)
s.text(622, 492, "已降解", 30, GRAY, "middle")

# ---- 轨道 3：读段方向与原 mRNA 严格对应 ----
s.line(60, 540, 740, 540, BLUE, 5)
s.polygon([(220, 540), (520, 540), (500, 526), (220, 526)], BLUE)
s.text(560, 520, "正义链", 30, BLUE, "middle")
for x in (320, 370, 420, 470):
    s.polygon([(x, 620), (x + 14, 620), (x + 14, 602), (x + 22, 602),
               (x + 7, 584), (x - 8, 602), (x, 602)], CYAN)
s.line(60, 660, 740, 660, PANEL, 5)
s.polygon([(520, 660), (220, 660), (240, 674), (520, 674)], PANEL)
s.text(400, 694, "反义链", 30, PANEL, "middle")
s.circle(546, 602, 23, WHITE, GREEN, 6)
s.polyline([(535, 602), (542, 611), (559, 591)], GREEN, 6)
s.label(158, 582, ["严格锁定转录方向"], 30, INK)
s.label(668, 582, ["分辨反义表达"], 30, INK)

s.save("03_strand_specific_dutp.svg")

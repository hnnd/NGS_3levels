#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_read_ratio_discounts.py — FIG-M06-02 16S 画像三条折扣漏斗

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-02（P10，cols 一栏 800×700，new-svg）。
教材依据：§18.1（三条折扣：拷贝数、引物偏好、区段分辨率）、§18.8（读段比例 ≠ 细胞比例）。
图内汉字 = 方案原句逐字，共 23 字（拷贝数差 4 / 引物偏好 4 / 区段限制 4 /
读段比例不等于细胞比例 11）；其余标注为 16S rRNA 与箭头符号。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 02_read_ratio_discounts.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

s.text(400, 54, "16S rRNA", 30, GRAY, "middle", "bold")

# ---------------- 三级漏斗：级间留 26 px 空档放箭头，逐级收窄 ----------------
# (y_top, y_bot, half_top, half_bot, fill, stroke, 标签, 标签色)
STAGES = [
    (86, 186, 322, 266, BLUE_TINT, BLUE, "拷贝数差", BLUE),
    (212, 312, 266, 214, CYAN_TINT, CYAN_DEEP, "引物偏好", CYAN_DEEP),
    (338, 438, 214, 160, BLUE_TINT, BLUE, "区段限制", BLUE),
]

for yt, yb, ht, hb, fill, stroke, cap, cap_ink in STAGES:
    s.polygon([(400 - ht, yt), (400 + ht, yt),
               (400 + hb, yb), (400 - hb, yb)], fill, stroke, 4)
    s.text(400, (yt + yb) / 2 + 12, cap, 34, cap_ink, "middle", "bold")

# 级间箭头（每过一级，读段比例再打一次折扣）
for y0, y1 in ((188, 210), (314, 336)):
    s.arrow(400, y0, 400, y1, CYAN_DEEP, 5, 12)

# ---------------- 底部警示卡 ----------------
CARD_Y, CARD_H = 494, 92
s.rect(74, CARD_Y, 652, CARD_H, RED_TINT, RED, 5, rx=14)
s.text(400, CARD_Y + CARD_H / 2 + 13, "读段比例不等于细胞比例", 34, RED,
       "middle", "bold")

# 漏斗出口指向警示卡
s.arrow(400, 442, 400, CARD_Y - 8, BLUE, 6, 16)

s.bottom([("reads ≠ cells", GRAY, None)], y=650, size=32)

s.save("02_read_ratio_discounts.svg")

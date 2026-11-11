#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_region_tradeoff.py — FIG-M06-04 16S rRNA 结构与三大条码取舍

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-04（P14，cols 一栏 800×700，new-svg）。
教材依据：§18.4.1（16S 全长 1542 nt、V1–V9 九段高变区、V4 253 bp / V3–V4 427 bp /
ITS 200–600 bp 三重取舍）。
图内汉字 = 方案原句逐字，共 16 字（保守引物 4 / 高变区 3 / 充裕 2 / 需长读 3 / 长度离散 4）；
其余标注为区段名、长度与平台参数。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 04_region_tradeoff.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 顶部：16S rRNA 结构横条 ----------------
BARY, BARH = 78, 74
X0, X1 = 60, 740

# 两端保守区
s.rect(X0, BARY, 96, BARH, GREEN, GREEN, 0, rx=8)
s.rect(X1 - 96, BARY, 96, BARH, GREEN, GREEN, 0, rx=8)

# 中间 V1–V9 高变区（9 段交替深浅，长度不按真实比例，示意即可）
SEG_N, GAP = 9, 6
usable = (X1 - 96) - (X0 + 96) - (SEG_N - 1) * GAP
seg_w = usable / SEG_N
for i in range(SEG_N):
    x = X0 + 96 + i * (seg_w + GAP)
    s.rect(x, BARY, seg_w, BARH, CYAN if i % 2 == 0 else CYAN_TINT,
           CYAN_DEEP, 3, rx=6)
    s.text(x + seg_w / 2, BARY + BARH / 2 + 10, f"V{i + 1}", 30,
           WHITE if i % 2 == 0 else CYAN_DEEP, "middle", "bold")

# 结构标注
s.text(X0 + 48, BARY - 16, "保守引物", 32, GREEN, "middle", "bold")
s.text(400, BARY - 16, "高变区", 32, CYAN_DEEP, "middle", "bold")

# ---------------- 下方三张取舍卡 ----------------
CY, CH = 226, 300
CW = 224
PX = [36, 288, 540]

CARDS = [
    ("V4", "253 bp", "PE250", "充裕", GREEN, GREEN_TINT),
    ("V3–V4", "427 bp", "PE300", "需长读", ORANGE, ORANGE_TINT),
    ("ITS", "200–600 bp", "ITS1/ITS2", "长度离散", PURPLE, PURPLE_TINT),
]

for x, (name, length, plat, cap, ink, tint) in zip(PX, CARDS):
    s.rect(x, CY, CW, CH, tint, ink, 4, rx=16)
    s.text(x + CW / 2, CY + 52, name, 34, ink, "middle", "bold")
    s.text(x + CW / 2, CY + 116, length, 32, INK, "middle")
    s.line(x + 26, CY + 146, x + CW - 26, CY + 146, ink, 2, dash="8 6")
    s.text(x + CW / 2, CY + 204, cap, 34, ink, "middle", "bold")
    s.text(x + CW / 2, CY + 260, plat, 30, GRAY, "middle")

# ---------------- 底部收束 ----------------
s.bottom([("V4 = 253 bp · V3–V4 = 427 bp · ITS 200–600 bp", GRAY, None)],
         y=634, size=30)

s.save("04_region_tradeoff.svg")

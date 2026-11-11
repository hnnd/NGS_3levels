#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_bio_vs_tech_replicate.py — FIG-M05-07 生物学重复与技术重复

方案：`reviews/course/M05_FIGP_001.md` §4.1 FIG-M05-07（P23，`.cols` 800×700，new-svg）。
教材依据：§15.4.2 L153–L161。
左：三个独立个体（三列）各取样两次，同一特征的信号在个体间明显分离 → 真实生物方差；
右：同一管文库分装测序，各次测量几乎重合 → 一致性虚假紧密（不可重复发现率偏低、
scaled IDR 偏高，见 ALN W8）。
图内汉字 24 字，逐字取方案原句：重复性质：技术重复虚构一致性，生物学重复提供真实方差。
红为唯一警示色，只用于「技术重复」一侧：面板红框（1 处）+ 点云红（1 处）＝ 2 处。
散点坐标为固定常量，无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 07_bio_vs_tech_replicate.py
"""
from svghelp import *

s = SVG()

s.text(400, 58, "重复性质", 36, BLUE, "middle", "bold")
s.text(400, 104, "技术重复虚构一致性，生物学重复提供真实方差", 30, INK, "middle")

PY, PH, PW = 172, 336, 314
LX, RX = 44, 442
BASE = PY + PH - 42                              # 基线 y

# ---------------- 左：生物学重复（三个独立个体，各两次取样） ----------------
s.rect(LX, PY, PW, PH, WHITE, PANEL, 3, rx=16)
s.line(LX + 56, BASE, LX + PW - 26, BASE, PANEL, 4)
s.line(LX + 56, PY + 52, LX + 56, BASE, PANEL, 4)
BIO = [(1, 4.4), (1, 6.0), (2, 7.2), (2, 8.6), (3, 3.0), (3, 4.6)]
for g, v in BIO:
    cx = LX + 96 + (g - 1) * 84
    cy = BASE - v * 32
    s.circle(cx, cy, 12, GREEN)
for g in ("1", "2", "3"):                        # 个体编号（三个独立个体）
    cx = LX + 96 + (int(g) - 1) * 84
    s.text(cx, BASE + 46, g, 30, GREEN, "middle", "bold")

# ---------------- 右：技术重复（同一管文库分装） ----------------
s.rect(RX, PY, PW, PH, WHITE, RED, 4, rx=16)
s.line(RX + 56, BASE, RX + PW - 26, BASE, PANEL, 4)
s.line(RX + 56, PY + 52, RX + 56, BASE, PANEL, 4)
cx0, cy0 = RX + 168, BASE - 6.0 * 32
TECH = [(0, 0), (11, -8), (-10, 7), (5, 11), (-5, -9),
        (15, 3), (-15, -3), (2, -13), (-2, 14), (8, -2), (-8, 3)]
d = " ".join(f"M {cx0 + dx - 11} {cy0 + dy} a 11 11 0 1 0 22 0 a 11 11 0 1 0 -22 0"
             for dx, dy in TECH)
s.path(d, RED, 3, fill=RED)

s.save("07_bio_vs_tech_replicate.svg")

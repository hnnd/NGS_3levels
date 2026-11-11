#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""03_control_replicate_pillars.py — FIG-M05-03 对照与重复两条腿

方案：`reviews/course/M05_FIGP_001.md` §4.1 FIG-M05-03（P19，`.cols` 800×700，new-svg）。
教材依据：§15.4.2 L143–L153。
图内汉字 23 字，逐字取方案原句：标题「背景模型两足」6；左卡「对照扣除偏差」6；
右卡「生物学重复压制随机噪声」11。平台本身不加字（方案未给平台文字）。
配色：基座/平台深蓝，对照青蓝，重复绿。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 03_control_replicate_pillars.py
"""
from svghelp import *

s = SVG()

s.title("背景模型两足", y=64)

# ---------------- 上方平台：可靠峰集合 ----------------
PLAT_Y, PLAT_H = 140, 82
s.rect(92, PLAT_Y, 616, PLAT_H, BLUE_TINT, BLUE, 4, rx=16)
for cx in (178, 252, 326, 400, 474, 548, 622):           # 平台上的过审峰标记
    s.polygon([(cx - 20, PLAT_Y + PLAT_H - 14), (cx, PLAT_Y + 14),
               (cx + 20, PLAT_Y + PLAT_H - 14)], BLUE_TINT, BLUE, 3)

# ---------------- 地面与两条腿 ----------------
GROUND = 486
s.line(64, GROUND, 736, GROUND, INK, 4)
for gx in range(76, 740, 26):                             # 地面斜纹
    s.line(gx, GROUND, gx - 13, GROUND + 13, GRAY, 2)

# 左腿：input 对照扣除系统偏差（三条偏差条纹 → 一条基线）
s.rect(218, PLAT_Y + PLAT_H, 150, GROUND - PLAT_Y - PLAT_H, CYAN, CYAN_DEEP, 4, rx=10)
for i in range(3):
    s.line(244, 300 + i * 30, 342, 300 + i * 30, WHITE, 5)
s.line(244, 396, 342, 396, WHITE, 8)

# 右腿：生物学重复压制随机噪声（散点被压回基线）
s.rect(464, PLAT_Y + PLAT_H, 150, GROUND - PLAT_Y - PLAT_H, GREEN, None, 4, rx=10)
NOISE = [(38, 288), (76, 316), (52, 344), (92, 372),
         (44, 400), (84, 428), (60, 456), (98, 292)]
for dx, dy in NOISE:
    s.circle(464 + dx, dy, 7, WHITE)

# ---------------- 两足说明（方案原句逐字） ----------------
s.text(293, 584, "对照扣除偏差", 30, CYAN_DEEP, "middle", "bold")
for i, ln in enumerate(("生物学重复压制", "随机噪声")):
    s.text(539, 558 + i * 50, ln, 30, GREEN, "middle", "bold")

s.save("03_control_replicate_pillars.svg")

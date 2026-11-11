#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_overlap_geometry.py — FIG-M06-05 读长与扩增子重叠几何

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-05（P15，cols 一栏 800×700，new-svg）。
教材依据：§18.3（重叠算式）、§18.4.1（V4 的 L_ins = 253 bp、l_F = 19、l_R = 20，
PE250 下 O = 208 bp）。
图内汉字 = 方案原句逐字，共 15 字（插入全长 4 / 切除引物 4 / 双端读段 4 / 重叠区 3）；
其余标注为 L_ins、F、R 与公式符号。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 05_overlap_geometry.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# 同一坐标轴、统一比例尺 S = 1.5 px/bp（插入片段 L_ins = 253 bp）
S = 1.5
I0, I1 = 190, 190 + 253 * S          # 插入片段：190 → 569.5
FP0, FP1 = I0 - 19 * S, I0           # F 读段 5′ 引物 19 bp
FX1 = I0 + 231 * S                   # F 读段 3′ 端（覆盖插入 231 bp）
RP0, RP1 = I1, I1 + 20 * S           # R 读段 5′ 引物 20 bp
RX0 = I1 - 230 * S                   # R 读段 3′ 端（覆盖插入 230 bp）

INS_T, INS_H = 72, 60
F_T, F_H = 202, 48
R_T, R_H = 292, 48

# ---------------- 有效重叠区（绿带，先画，压在读段之下） ----------------
BAND_T, BAND_B = 196, 356
s.rect(RX0, BAND_T, FX1 - RX0, BAND_B - BAND_T, GREEN_TINT, None, 0)
# 绿框只画在读段之外的上/下留白里，避免压住读段
s.line(RX0, BAND_T, FX1, BAND_T, GREEN, 4)
s.line(RX0, BAND_B, FX1, BAND_B, GREEN, 4)
for xx in (RX0, FX1):
    s.line(xx, BAND_T, xx, F_T, GREEN, 4)
    s.line(xx, R_T + R_H, xx, BAND_B, GREEN, 4)

# ---------------- 插入片段全长 ----------------
s.text(400, 60, "L_ins = 253 bp", 30, GRAY, "middle")
s.rect(I0, INS_T, I1 - I0, INS_H, BLUE_TINT, BLUE, 4, rx=10)
s.text((I0 + I1) / 2, INS_T + INS_H / 2 + 12, "插入全长", 34, BLUE,
       "middle", "bold")

# ---------------- 双端读段 ----------------
s.text(400, 170, "双端读段", 32, CYAN_DEEP, "middle", "bold")

# F 读段：左端引物段 + 插入段，5′→3′
s.rect(FP0, F_T, FX1 - FP0, F_H, CYAN, None, 0, rx=8)
s.rect(FP0, F_T, FP1 - FP0, F_H, ORANGE, None, 0, rx=8)
s.arrow(FP1 + 24, F_T + F_H / 2, FX1 - 18, F_T + F_H / 2, CYAN_DEEP, 4, 12)
s.text(FP0 - 12, F_T + F_H / 2 + 11, "F", 32, CYAN_DEEP, "end", "bold")

# R 读段：右端引物段 + 插入段，5′→3′（自右向左）
s.rect(RX0, R_T, RP1 - RX0, R_H, CYAN, None, 0, rx=8)
s.rect(RP0, R_T, RP1 - RP0, R_H, ORANGE, None, 0, rx=8)
s.arrow(RP0 - 24, R_T + R_H / 2, RX0 + 18, R_T + R_H / 2, CYAN_DEEP, 4, 12)
s.text(RP1 + 12, R_T + R_H / 2 + 11, "R", 32, CYAN_DEEP, "start", "bold")

# ---------------- 重叠区标注 ----------------
s.line(400, BAND_B, 400, BAND_B + 16, GREEN, 4)
s.text(400, BAND_B + 58, "重叠区", 32, GREEN, "middle", "bold")

# ---------------- 图例：橙色切除引物 ----------------
SW = 24
GY = 428
GX = (800 - (SW + 14 + text_width("切除引物", 30, True))) / 2
s.rect(GX, GY, SW, SW, ORANGE, ORANGE_DEEP, 2, rx=4)
s.text(GX + SW + 14, GY + SW - 2, "切除引物", 30, ORANGE_DEEP, "start", "bold")

# ---------------- 公式与参数 ----------------
s.text(400, 524, "O = (F − l_F) + (R − l_R) − L_ins", 32, INK,
       "middle", "bold")
s.text(400, 574, "231 + 230 − 253 = 208 bp", 30, GREEN, "middle", "bold")
s.text(400, 620, "F = 250   l_F = 19   R = 250   l_R = 20", 30, GRAY, "middle")

s.save("05_overlap_geometry.svg")

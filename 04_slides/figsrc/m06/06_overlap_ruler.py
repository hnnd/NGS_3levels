#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_overlap_ruler.py — FIG-M06-06 重叠减法四配置标尺

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-06（P16，cols 一栏 800×700，new-svg）。
教材依据：§18.4.1 判据表（V4 240/200 → 148 bp、V4 250/250 → 208 bp、
V3–V4 PE300 280/220 → 35 bp、V3–V4 PE250 230/230 → 0 bp）；`minOverlap` 默认 12 bp，
余量 20 bp 为本课练习设定（非文献阈值）。
图内汉字 = 方案原句逐字，共 16 字（重叠充裕 4 / 重叠紧张 4 / 重叠归零 4 / 门槛十二 4）；
其余标注为 `truncLen` 配置与 bp 数。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 06_overlap_ruler.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# 竖向标尺：0 bp 在基线 y=520，220 bp 在 y=230（k ≈ 1.318 px/bp）
AX, Y0, Y1 = 132, 520, 230
K = (Y0 - Y1) / 220


def by(bp):
    return Y0 - K * bp


# 四根柱：(配置名, truncLen, bp, 颜色, 柱内文字色)
COLS = [
    ("V4", "240/200", 148, GREEN, WHITE),
    ("V4", "250/250", 208, GREEN, WHITE),
    ("V3–V4", "280/220", 35, ORANGE, INK),
    ("V3–V4", "230/230", 0, RED, RED),
]
CX = [216, 344, 472, 600]
BW = 80

# ---------------- 标尺轴与刻度 ----------------
s.line(AX, Y0, 700, Y0, INK, 4)
s.line(AX, Y0, AX, Y1 - 30, INK, 4)
for bp in (0, 50, 100, 150, 200):
    s.line(AX - 8, by(bp), AX, by(bp), INK, 3)
    s.text(AX - 20, by(bp) + 10, str(bp), 30, GRAY, "end")

# ---------------- 门槛 12 bp（橙虚线）与余量 20 bp（绿虚线） ----------------
s.line(AX, by(12), 700, by(12), ORANGE, 3, dash="10 8")
s.line(AX, by(20), 700, by(20), GREEN, 3, dash="8 8")

# 虚线图例（右上空白区）
s.line(430, 92, 470, 92, ORANGE, 4, dash="10 8")
s.text(484, 102, "门槛十二", 30, ORANGE_DEEP, "start", "bold")
s.line(430, 140, 470, 140, GREEN, 4, dash="8 8")
s.text(484, 150, "20 bp", 30, GREEN, "start", "bold")

# ---------------- 四根柱 ----------------
for cx, (name, trunc, bp, color, ink) in zip(CX, COLS):
    x = cx - BW / 2
    if bp > 0:
        s.rect(x, by(bp), BW, Y0 - by(bp), color, None, 0, rx=8)
        s.text(cx, by(bp) - 18, f"{bp} bp", 30, color, "middle", "bold")
    else:
        s.rect(x, Y0 - 14, BW, 12, RED, None, 0, rx=4)
        s.text(cx, Y0 - 46, "0 bp", 30, INK, "middle", "bold")
    s.text(cx, Y0 + 48, name, 30, INK, "middle", "bold")
    s.text(cx, Y0 + 92, trunc, 30, GRAY, "middle")

# ---------------- 判读标签（分组覆盖，写在各柱组下方） ----------------
s.text(280, Y0 + 148, "重叠充裕", 32, GREEN, "middle", "bold")
s.text(472, Y0 + 148, "重叠紧张", 32, ORANGE_DEEP, "middle", "bold")
s.text(626, Y0 + 148, "重叠归零", 32, RED, "middle", "bold")

s.save("06_overlap_ruler.svg")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""33_few_bins_depth_check.py — FIG-M07-36 分箱过少或无箱的排查树：深度表与碎片化

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-36（P65，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.5.7（MetaBAT2 只分出很少几个箱、甚至 No bins 时，按可查对象逐项排查：
① 深度表列数是否对（列写错是「无箱」最常见原因）；
② 比对文件（BAM）个数是否与样本数一致；
③ 重叠群长度是否够（组装被打碎时任何分箱器都无解）。
三者都正常则「单样本亦可有箱」——单样本不等于不能分箱。
版式：顶部空箱图标（虚线空箱 = No bins）向下接三步排查卡，每步右侧配该步要查的对象：
① 深度表（格子表）② 比对文件（叠放的 BAM 页）③ 碎片化重叠群（长短不一的短条）；
第一步用红色外框强调（最常见原因），底部绿卡写结论。
图内汉字 = 方案清单逐字（排查深度表列数 7 / 核对比对文件数 7 / 检查重叠群长度 7 /
单样本亦可有箱 7）＝ 28 字。
红色一处：第一步卡片的外框（同一警示语义组）。
不含任何数值（深度表列数规则见正文公式）。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 33_few_bins_depth_check.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

CARD_X, CARD_W, CARD_H = 88, 420, 78
STEPS = ("排查深度表列数", "核对比对文件数", "检查重叠群长度")
YS = (212, 328, 444)

# ---------------- 顶部：空箱（No bins） ----------------
s.rect(348, 82, 104, 74, WHITE, BLUE, 3, rx=10, dash="10 7")
s.line(348, 102, 384, 122, BLUE, 3)
s.line(416, 122, 452, 102, BLUE, 3)

# ---------------- 三步排查 ----------------
for i, (y, label) in enumerate(zip(YS, STEPS)):
    s.rect(CARD_X, y, CARD_W, CARD_H, WHITE, CYAN_DEEP, 3, rx=14)
    s.text(CARD_X + 26, y + CARD_H / 2 + 11, label, 32, CYAN_DEEP, "start",
           "bold")
    if i == 0:
        s.rect(CARD_X - 14, y - 14, CARD_W + 28, CARD_H + 28, "none", RED, 5,
               rx=18)
    if i < len(STEPS) - 1:
        s.line(400, y + CARD_H, 400, YS[i + 1] - 4, GRAY, 3)
        s.arrow(400, YS[i + 1] - 26, 400, YS[i + 1] - 4, GRAY, 3, 12)
# 根到第一步
s.line(400, 156, 400, YS[0] - 26, GRAY, 3)
s.arrow(400, YS[0] - 26, 400, YS[0] - 4, GRAY, 3, 12)

# ---------------- 右侧：三步各自要查的对象 ----------------
IX = 660

# ① 深度表：3×3 格阵
for r in range(3):
    for c in range(3):
        s.rect(IX - 66 + c * 46, YS[0] - 44 + r * 32, 36, 26,
               CYAN_TINT if (r + c) % 2 else CYAN, rx=4)

# ② BAM 文件：三张叠放的页面
for k in range(3):
    s.rect(IX - 72 + k * 16, YS[1] - 40 + k * 14, 56, 46, WHITE, GRAY, 3,
           rx=8)

# ③ 碎片化重叠群：长短不一的短条
for k, w in enumerate((86, 48, 66, 30, 74)):
    s.rect(IX - 66, YS[2] - 40 + k * 22, w, 13,
           ORANGE_DEEP if k % 2 else ORANGE, rx=4)

# ---------------- 底部结论 ----------------
s.rect(96, 596, 608, 78, GREEN_TINT, GREEN, 3, rx=16)
s.text(400, 646, "单样本亦可有箱", 32, GREEN, "middle", "bold")

s.save("33_few_bins_depth_check.svg")

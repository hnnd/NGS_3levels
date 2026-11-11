#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_tsse_profile.py — FIG-M05-12 TSSE 信号剖面

方案：`reviews/course/M05_FIGP_001.md` §4.2 FIG-M05-12（P31，`.cols` 800×700，new-svg）。
教材依据：§15.4.4 L221–L227。TSSE = 中心窗口平均信号 ÷ 两侧背景平均信号（位置口径）。
图内汉字 22 字，逐字取方案原句：标题「转录起始位点富集」8；
结论「中心尖峰对比两侧平缓背景比值」14。其余标注仅为 ±2 kb、TSS 等符号。
剖面曲线为写入脚本的固定解析形状（合成示意，不含随机数，也不作实测数据使用）。
红为唯一警示色，只用于「中心窗口」与「比值」两处标记（2 处）。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 12_tsse_profile.py
"""
import math

from svghelp import *

s = SVG()

s.text(400, 58, "转录起始位点富集", 36, BLUE, "middle", "bold")

# ---------------- 坐标框：横轴 TSS ±2 kb，纵轴标准化信号 ----------------
L, R, B, T = 108, 700, 486, 184
SPAN = 2000.0                                   # ±2 kb


def px(bp):
    return L + (R - L) * (bp + SPAN) / (2 * SPAN)


def py(v):
    return B - (B - T) * v / 1.25


s.line(L, B, R, B, INK, 4)
s.line(L, B, L, T, INK, 4)
s.text(L - 10, T - 26, "信号", 30, GRAY, "start")

BAND = [(px(-SPAN), "−2 kb"), (px(0), "TSS"), (px(SPAN), "+2 kb")]
for x, lab in BAND:
    s.line(x, B, x, B + 8, INK, 3)
    s.text(x, B + 40, lab, 30, GRAY, "middle")

# ---------------- 剖面：中心尖峰 + 两侧平缓背景（加宽的核小体排布低谷） ----------------
pts = []
for i in range(0, 241):
    bp = -SPAN + 2 * SPAN * i / 240
    v = 0.16 + 0.10 * math.exp(-(bp / 900.0) ** 2)      # 平缓背景
    v += 0.95 * math.exp(-(bp / 130.0) ** 2)             # TSS 中心尖峰
    v -= 0.07 * math.exp(-((abs(bp) - 260.0) / 120.0) ** 2)   # 两侧低谷
    pts.append((px(bp), py(v)))
s.curve(pts, CYAN_DEEP, 5)

# 中心窗口（±150 bp）与背景窗口的取法
CW = [(px(-150), "left"), (px(150), "right")]
d = " ".join(f"M {x} {B} L {x} {T + 20}" for x, _ in CW)
s.path(d, RED, 4, dash="12 9")                   # 两条辅助线合成一条 path（红 1 处）
s.text(px(0), T + 8, "TSS", 30, BLUE, "middle", "bold")

# 两侧背景窗口（取 ±1–2 kb 两段）
for a, b in ((-1800, -1200), (1200, 1800)):
    s.line(px(a), B - 6, px(a), B - 46, PURPLE, 4)
    s.line(px(b), B - 6, px(b), B - 46, PURPLE, 4)
    s.line(px(a), B - 30, px(b), B - 30, PURPLE, 4)
s.text(px(-1500), B - 56, "背景", 30, PURPLE, "middle", "bold")
s.text(px(1500), B - 56, "背景", 30, PURPLE, "middle", "bold")

# ---------------- 结论：中心 ÷ 背景 ----------------
s.text(400, 574, "中心尖峰对比两侧平缓背景", 32, INK, "middle", "bold")
s.text(400, 626, "比值", 32, BLUE, "middle", "bold")

s.save("12_tsse_profile.svg")

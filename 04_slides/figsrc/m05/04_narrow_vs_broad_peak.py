#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_narrow_vs_broad_peak.py — FIG-M05-04 窄峰与宽峰物理分布

方案：`reviews/course/M05_FIGP_001.md` §4.1 FIG-M05-04（P20，`.cols` 800×700，new-svg）。
教材依据：§15.4.3 L187–L195。
图内汉字 23 字，逐字取方案原句、不增不减：标题「峰型先验」4；
上轨「转录因子尖锐窄峰」8；下轨「组蛋白修饰连续弥散宽域」11。
其余标注只用尺度符号（bp），不写整句英文。
配色（spec §2）：窄峰青蓝、宽峰紫、DNA 主轴深蓝。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 04_narrow_vs_broad_peak.py
"""
import math

from svghelp import *

s = SVG()

s.title("峰型先验", y=64)

X0, X1 = 120, 676                      # 轨道起止
DNA_W = 7


def track(y):
    s.line(X0, y, X1, y, BLUE, DNA_W, cap="round")


# ---------------- 上轨：转录因子窄峰（孤立尖峰，数百 bp 宽） ----------------
s.text(X0, 136, "转录因子尖锐窄峰", 30, CYAN_DEEP, "start", "bold")
TF_AXIS = 278
track(TF_AXIS)
for cx, h, w in ((208, 106, 12), (368, 118, 13), (516, 88, 11)):
    pts = [(cx - 2.2 * w, TF_AXIS), (cx - w, TF_AXIS - h * 0.48),
           (cx, TF_AXIS - h), (cx + w, TF_AXIS - h * 0.48),
           (cx + 2.2 * w, TF_AXIS)]
    s.polygon(pts, CYAN, CYAN_DEEP, 3)
    s.line(cx - 2.2 * w, TF_AXIS + 40, cx + 2.2 * w, TF_AXIS + 40, GRAY, 3)
s.text(208, TF_AXIS + 84, "200 bp", 30, GRAY, "middle")
s.text(368, TF_AXIS + 84, "200 bp", 30, GRAY, "middle")
s.text(516, TF_AXIS + 84, "200 bp", 30, GRAY, "middle")

# ---------------- 下轨：组蛋白修饰宽域（连续弥散，kb 数量级） ----------------
s.text(X0, 438, "组蛋白修饰连续弥散宽域", 30, PURPLE, "start", "bold")
HM_AXIS = 600
track(HM_AXIS)
d = f"M {X0} {HM_AXIS}"
n = 200
for i in range(n + 1):                  # 平台型连续信号：顶部平缓、边缘陡降
    x = X0 + (X1 - X0) * i / n
    u = (i / n - 0.5) * 2
    y = HM_AXIS - 82 * (1.0 / (1.0 + math.exp(16 * (abs(u) - 0.74))) + 0.02)
    d += f" L {x:.1f} {y:.1f}"
d += f" L {X1} {HM_AXIS} Z"
s.path(d, PURPLE, 4, fill=PURPLE_TINT)
s.line(X0 + 60, HM_AXIS + 34, X1 - 40, HM_AXIS + 34, GRAY, 3)
s.text(398, HM_AXIS + 78, "20 kb", 30, GRAY, "middle")

s.save("04_narrow_vs_broad_peak.svg")

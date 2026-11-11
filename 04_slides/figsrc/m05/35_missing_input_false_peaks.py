#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""35_missing_input_false_peaks.py — FIG-M05-35 缺 input 对照的假峰失效（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.4 FIG-M05-35（P59，`.cols` 800×700，new-svg）。
教材依据：§15.5.2 L357–L366。机制：染色体剖面上，拷贝数扩增区与高拷贝重复区（rDNA、着丝粒
周边）的读段本来就堆得高；没有同批染色质的 input 库，MACS2 只能按局部背景自估期望，于是
把这类天然高堆叠区写成显著 peak。补上 input 后，同一处信号几乎被期望线追平，差异不再显著。

图面两段，共用同一横轴、同一纵轴量程：
上段（无 input）：一条读段密度曲线 + 一条固定期望线（灰虚线）。rDNA 区与着丝粒周边区
两处高堆叠冲过期望线 → 记为假峰（红）；中央的真实开放区低于期望线，反而没被检出。
下段（补 input）：同一条密度曲线 + 按同批染色质拷贝数梯度抬起的 input 期望线（深蓝虚线，
在两处高拷贝区同步抬高）。两处高堆叠与期望线只隔一线之差，中央真实开放区的差异反而最大。

图内汉字 27 字（上限 30）：标题「未校正背景」5 ＋ 两段轴名「读段」2×2=4
＋「假峰」2 ＋ 结论「扩增区与高拷贝区误报为峰」12 ＋「落入着丝粒」5 ＝ 28，
减重复计一次「高拷贝区」可读为 27。input 写拉丁字符，不占汉字。
颜色：真实峰青蓝 `#4DBBD5`、重复区假峰红 `#E64B35`（假峰三角合成一条 path = 1 处、
「假峰」二字 1 处，共 2 处）、input 校正基线深蓝 `#3C5488`。
本图无 data-plot 数据入口，故**不标任何峰数、FRiP、倍数**（与 FIG-M05-26 同口径），
只演示几何与期望线的对比关系。无随机数（形状由解析函数生成）、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 35_missing_input_false_peaks.py
"""
import math

from svghelp import *

s = SVG()

s.text(400, 58, "未校正背景", 36, BLUE, "middle", "bold")

L, R = 104, 716
YMAX = 110.0
BASE_V = 20.0                                   # 平缓背景读段密度

# 三处堆叠：rDNA 高拷贝区 0.28、真实开放区 0.50、着丝粒周边 0.74
BUMPS = [(0.28, 0.042, 62.0), (0.50, 0.070, 40.0), (0.74, 0.034, 78.0)]
HIGH_COPY = (0.28, 0.74)


def density(f):
    v = BASE_V
    for c, w, h in BUMPS:
        v += h * math.exp(-((f - c) / w) ** 2)
    return v


def expectation_no_input(f):
    """无 input 时的自估期望：整段一条平线（看不到拷贝数梯度）。"""
    return 34.0


def expectation_input(f):
    """有 input 时的期望：跟同批染色质的拷贝数梯度走（只在高拷贝区抬起）。"""
    v = 30.0
    for c in HIGH_COPY:
        v += 66.0 * math.exp(-((f - c) / 0.052) ** 2)
    return v


def polyline_of(fn, base, gain):
    return [(L + (R - L) * (i / 180.0), base - gain * min(fn(i / 180.0), YMAX) / YMAX)
            for i in range(181)]


def panel(name, base, gain, with_input):
    s.line(L, base, R, base, INK, 4)
    s.line(L, base, L, base - gain - 22, INK, 4)
    s.text(L - 8, base - gain - 34, name, 30, GRAY, "start")
    s.curve(polyline_of(density, base, gain), CYAN_DEEP, 5)
    if with_input:
        s.curve(polyline_of(expectation_input, base, gain), BLUE, 5, dash="16 10")
    else:
        s.curve(polyline_of(expectation_no_input, base, gain), GRAY, 4, dash="16 10")


# ---------- 上：无 input，两处高堆叠冲过期望线 → 假峰 ----------
B1, G1 = 288, 132
panel("读段", B1, G1, with_input=False)

marks = []
for c in HIGH_COPY:
    x = L + (R - L) * c
    top = B1 - G1 * min(density(c), YMAX) / YMAX
    marks.append(f"M {x - 30:.1f} {top - 16:.1f} L {x:.1f} {top - 2:.1f} "
                 f"L {x + 30:.1f} {top - 16:.1f} Z")
s.path(" ".join(marks), RED, 3, fill=RED)
s.text(L + (R - L) * HIGH_COPY[0], B1 - G1 - 14, "假峰", 30, RED, "middle", "bold")

# ---------- 下：补 input，期望线同步抬起，两处只隔一线 ----------
B2, G2 = 520, 132
panel("读段", B2, G2, with_input=True)
s.text(R - 6, B2 - G2 - 34, "input", 30, BLUE, "end", "bold")

# ---------- 结论（方案原句逐字） ----------
s.text(400, 620, "扩增区与高拷贝区误报为峰", 32, INK, "middle", "bold")
s.text(400, 674, "落入着丝粒", 32, INK, "middle", "bold")

s.save("35_missing_input_false_peaks.svg")
print("check: 高拷贝区 0.28／0.74 冲过无 input 期望线 34；补 input 后期望抬到 ~96，"
      "与信号 ~98 只隔一线（示意形状，无实测数据）")

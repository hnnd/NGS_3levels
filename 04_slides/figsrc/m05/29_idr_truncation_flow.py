#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""29_idr_truncation_flow.py — FIG-M05-29 IDR 截断过滤流程（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.3 FIG-M05-29（P51，`.cols` 800×700，new-svg）。
教材依据：§15.4.2 L153–L161、§15.6 L418–L419。流程三段：
① 两个重复各以宽松阈值（`-p 1e-3`）检峰，得到两张峰列表（浅蓝）；
② IDR 按显著性排秩、用 copula 混合模型估计每个峰属于「可重复」成分的概率（深蓝）；
③ 输出第 5 列 scaled IDR ≥ 540 的过审峰集（绿）。
540 来自手算：`−125·log₂(0.05) = 540.24 → 540`（§15.4.2 L159），与 FIG-M05-06 同源，
图上只写门槛数字、不复述公式。

图内汉字 25 字（上限 30）：标题「截断过滤」4 ＋ 方案原句「宽松检峰输出排秩」8
＋「混合模型打分提取高一致峰集」13。工具名与阈值写拉丁字符（rep1／rep2／IDR／≥ 540），
不写整句英文。配色：输入列表青蓝、模型处理深蓝、过审峰集绿。无警示语义，红不上图。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 29_idr_truncation_flow.py
"""
import math

from svghelp import *

CUT = -125.0 * math.log(0.05, 2)                 # 540.24
assert abs(CUT - 540) < 1, CUT

s = SVG()

s.text(400, 62, "截断过滤", 36, BLUE, "middle", "bold")

# ---------------- 左：两个重复的宽松检峰列表（同框，标明阈值口径） ----------------
LX, LY, LW, LH = 34, 124, 206, 356
s.rect(LX, LY, LW, LH, WHITE, PANEL, 3, rx=14)
for i in range(2):
    top = LY + 30 + i * 156
    s.text(LX + 22, top + 34, f"rep{i + 1}", 30, CYAN_DEEP, "start", "bold")
    for j in range(4):                            # 峰条：长短不齐＝显著性排名
        w = LW - 44 - (12 * ((j * 3 + i) % 4))
        s.rect(LX + 22, top + 50 + j * 16, w, 9,
               CYAN_DEEP if j == 0 else CYAN, None, rx=4)
s.text(LX + LW / 2, LY + LH - 22, "-p 1e-3", 30, GRAY, "middle")

# ---------------- 中：排秩 + copula 混合模型 ----------------
MX, MY, MW, MH = 292, 186, 194, 232
s.rect(MX, MY, MW, MH, BLUE_TINT, BLUE, 4, rx=14)
s.text(MX + MW / 2, MY + 58, "IDR", 34, BLUE, "middle", "bold")
for k in range(3):                                # 排秩示意：三条递减排名线
    x0 = MX + 26 + k * 26
    s.polyline([(x0, MY + 82), (x0 + 58, MY + 118), (x0 + 46, MY + 152)],
               BLUE, 4)
s.text(MX + MW / 2, MY + MH - 22, "copula", 30, BLUE, "middle", "bold")

# 列表 → 模型 → 过审集
s.arrow(LX + LW + 8, 208, MX - 8, 276, GRAY, 5, 14)
s.arrow(LX + LW + 8, 396, MX - 8, 330, GRAY, 5, 14)
s.arrow(MX + MW + 8, 302, 542, 302, GRAY, 5, 14)

# ---------------- 右：第 5 列 ≥ 540 的过审峰集 ----------------
RX, RY, RW, RH = 542, 158, 224, 288
s.rect(RX, RY, RW, RH, GREEN_TINT, GREEN, 4, rx=14)
s.text(RX + RW / 2, RY + 54, "≥ 540", 34, GREEN, "middle", "bold")
for j in range(4):
    s.rect(RX + 26, RY + 86 + j * 40, RW - 52, 22, GREEN, None, rx=5)

# ---------------- 结论（方案原句逐字，两句） ----------------
s.text(400, 546, "宽松检峰输出排秩", 32, INK, "middle", "bold")
s.text(400, 608, "混合模型打分提取高一致峰集", 32, GREEN, "middle", "bold")
s.text(400, 666, "IDR ≥ 540", 30, GRAY, "middle")

s.save("29_idr_truncation_flow.svg")
print(f"check: 门槛 −125·log2(0.05) = {CUT:.2f} → 540")

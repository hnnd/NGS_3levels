#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""22_pcoa_arch_effect.py — FIG-M06-22 PCoA 排序图与拱形效应

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-22（P36，cols 一栏 800×700，new-svg）。
教材依据：§18.4.7（前两轴解释比例小是常态；样本沿 PC1 呈马蹄形是强梯度下的拱形效应，
属几何伪影，改用 NMDS；分组是否分离要与 R² 一起看）。
图内汉字 = 方案原句逐字，共 21 字（正常点云轻度分散 / 方差小属常态 / 拱形效应改排序）；
其余标注为 PC1、PC2 与 NMDS。红色仅 1 处（拱形弯曲弧线）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 22_pcoa_arch_effect.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

s.text(400, 52, "PCoA", 34, BLUE, "middle", "bold")

LP = (44, 92, 336, 380)      # 左：正常 PCoA
RP = (424, 92, 336, 380)     # 右：拱形效应

for x, y, w, h in (LP, RP):
    s.rect(x, y, w, h, WHITE, PANEL, 3, rx=12)

for ox in (84, 464):
    s.line(ox, 430, ox + 282, 430, BLUE, 3)
    s.line(ox, 430, ox, 140, BLUE, 3)
    s.text(ox + 286, 444, "PC1", 30, GRAY, "middle")
    s.text(ox + 26, 130, "PC2", 30, GRAY, "middle")

# ---------------- 左：两组点云，边缘轻度交叠 ----------------
HEALTH = [(132, 226), (152, 208), (172, 228), (144, 250), (166, 244),
          (186, 236), (128, 274), (152, 272), (176, 268), (198, 262),
          (170, 292)]
TREAT = [(196, 288), (220, 280), (240, 296), (204, 312), (228, 306),
         (250, 300), (212, 330), (238, 330), (258, 322), (228, 350),
         (252, 348)]

for cx, cy in HEALTH:
    s.circle(cx, cy, 9, CYAN)
for cx, cy in TREAT:
    s.circle(cx, cy, 9, GREEN)

# ---------------- 右：同一批样本沿 PC1 弯成马蹄 ----------------
ARCH = [(480, 216), (508, 282), (536, 336), (564, 370), (592, 386),
        (620, 388), (648, 374), (676, 342), (702, 288), (724, 218)]

# 两组样本分居红色马蹄中轴上下两侧：弯曲沿 PC1 发生，与分组无关
for i, (x, y) in enumerate(ARCH):
    s.circle(x, y - 20, 9, CYAN)
    s.circle(x, y + 20, 9, GREEN)

s.curve([(x, y) for x, y in ARCH], RED, 5, dash="12 10")

# ---------------- 说明（方案原句）----------------
s.text(212, 520, "正常点云轻度分散", 30, CYAN_DEEP, "middle", "bold")
s.text(212, 566, "方差小属常态", 30, GRAY, "middle")
s.text(592, 546, "拱形效应改排序", 30, BLUE, "middle", "bold")
s.text(592, 592, "NMDS", 30, GRAY, "middle")

s.save("22_pcoa_arch_effect.svg")

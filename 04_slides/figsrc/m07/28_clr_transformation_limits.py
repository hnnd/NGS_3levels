#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""28_clr_transformation_limits.py — FIG-M07-31 CLR 中心对数比变换原理与边界

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-31（P57，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.8（CLR：把每个组分除以该样本各组分几何均值 g(x) 后再取对数；文库大小 /
测序深度这个样本内的乘法常数在比值里被约掉，故 CLR 值只在本样本的组分之间可比，
而且**不恢复绝对量**——它消掉的是深度因子，不是把相对量还原成绝对量）。
版式：三栏。左栏原始相对丰度向量 x（深蓝横条，长度示意各组分占比）；中栏青色流程卡
「除以几何平均取对数」；右栏 CLR 结果 z（以 0 为中心上下分列，绿色正、橙色负）。
底部绿卡「样本内可比」+ 虚线红卡「不恢复绝对量」。
不写任何数值（CLR 值依赖具体数据，无实测入口）。
图内汉字 = 方案清单逐字（除以几何平均取对数 9 / 约掉测序深度常数 8 / 样本内可比 5 /
不恢复绝对量 6）＝ 28 字。
红色一处：「不恢复绝对量」文字与其虚线边框。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 28_clr_transformation_limits.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

TOP, BOT = 148, 452                          # 两栏面板上下沿
MID = 300                                    # 与流程卡对齐的横轴

s.text(400, 88, "约掉测序深度常数", 32, CYAN_DEEP, "middle", "bold")

# ---------------- 左栏：原始相对丰度向量 x ----------------
s.rect(56, TOP, 192, BOT - TOP, WHITE, BLUE, 3, rx=16)
s.text(76, 186, "x", 30, GRAY, "start", "bold")
for i, w in enumerate((136, 92, 62, 118)):
    s.rect(76, 204 + i * 60, w, 44, BLUE if i % 2 == 0 else BLUE_TINT, rx=8)

# ---------------- 中栏：变换流程卡 ----------------
s.rect(286, 240, 228, 120, CYAN_TINT, CYAN_DEEP, 3, rx=16)
s.label(400, MID, ["除以几何平均", "取对数"], 30, CYAN_DEEP, "middle", "bold",
        leading=1.36)
s.arrow(252, MID, 282, MID, CYAN_DEEP, 5, 15)
s.arrow(518, MID, 548, MID, CYAN_DEEP, 5, 15)

# ---------------- 右栏：CLR 结果 z（0 为中心双向） ----------------
s.rect(552, TOP, 192, BOT - TOP, WHITE, GREEN, 3, rx=16)
s.text(572, 186, "z", 30, GRAY, "start", "bold")
s.line(568, MID, 728, MID, GRAY, 3, dash="10 8")
for i, (h, up, col) in enumerate(((84, True, GREEN), (122, True, GREEN_TINT),
                                 (96, False, ORANGE), (146, False, ORANGE_TINT))):
    x = 578 + i * 38
    s.rect(x, MID - h if up else MID, 32, h, col, rx=6)

# ---------------- 底部：可比范围与边界 ----------------
s.rect(96, 498, 608, 84, WHITE, GREEN, 3, rx=16)
s.text(400, 552, "样本内可比", 30, GREEN, "middle", "bold")
s.rect(96, 606, 608, 74, WHITE, RED, 4, rx=16, dash="12 9")
s.text(400, 656, "不恢复绝对量", 32, RED, "middle", "bold")

s.save("28_clr_transformation_limits.svg")

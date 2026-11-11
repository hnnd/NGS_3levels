#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""24_upstream_failure_diagnostic.py — FIG-M07-27 上游质控与分类组装异常信号诊断卡

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-27（P51，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.5.1、§19.5.2（三个上游体征：宿主保留率骤降、未分类比例畸高、比回率暴跌，
分别指向同源误伤、参考库缺失、组装碎片化；先查参考与读长，不要先调参数）。
图内汉字 = 方案三张卡向逐字（宿主保留骤降：误伤 / 未分类畸高：缺参考 / 比回率暴跌：碎片化
= 24 字）＋底部红字「查参考与读长」（6 字）＝ 30 字；方案原文「先查参考与读长」多一个「先」，
按 30 汉字红线删去，语义不变（回执 minor issue 已记录）。三张卡都用橙框（体征形态），
仪表指针按卡内色相区分；红色一处：底部虚线框与该行红字。
仪表读数只用指针与刻度示意，不写任何百分比（无实测入口）。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 24_upstream_failure_diagnostic.py
"""
import math
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

CARDS = (
    (32, ["宿主保留骤降：", "误伤"], -0.62, ORANGE_DEEP),      # 指针偏左（异常）
    (280, ["未分类畸高：", "缺参考"], 0.66, ORANGE_DEEP),      # 指针偏右（异常）
    (528, ["比回率暴跌：", "碎片化"], -0.80, ORANGE_DEEP),
)
CW, CH, CY = 240, 344, 96

for x, lines, angle, deep in CARDS:
    s.rect(x, CY, CW, CH, ORANGE_TINT, ORANGE_DEEP, 4, rx=18)
    s.label(x + CW / 2, CY + 56, lines, 30, deep, "middle", "bold", leading=1.34)
    # 仪表盘：半圆刻度 + 指针
    cx, cy, r = x + CW / 2, CY + 250, 66
    s.path(f"M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}", ORANGE_DEEP, 4)
    for k in range(7):
        a = math.pi - k * math.pi / 6
        s.line(cx + (r - 10) * math.cos(a), cy - (r - 10) * math.sin(a),
               cx + r * math.cos(a), cy - r * math.sin(a), ORANGE_DEEP, 3)
    s.line(cx, cy, cx + (r - 16) * math.cos(angle), cy - (r - 16) * math.sin(angle),
           INK, 5)
    s.circle(cx, cy, 8, INK)

# ---------------- 红色语义组：先查参考与读长 ----------------
s.rect(64, 494, 672, 100, WHITE, RED, 4, rx=18, dash="12 9")
s.text(400, 556, "查参考与读长", 34, RED, "middle", "bold")

s.save("24_upstream_failure_diagnostic.svg")

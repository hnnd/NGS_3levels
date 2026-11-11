#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_alpha_indices_compass.py — FIG-M06-19 五大 α 多样性指数敏感性罗盘

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-19（P32，cols 一栏 800×700，new-svg）。
教材依据：§18.4.6（Observed 极度依赖深度、Shannon 默认首选、Simpson 查优势度、Faith's PD 需建树、
Chao1 依赖单双例并在 ASV 表退化）。
图内汉字 = 方案原句逐字，共 21 字（种类数极度依赖深度 / 丰富均匀首选 / 优势度查垄断）；
指数名 Observed、Shannon、Simpson、Chao1、Faith's PD 与退化记法 `n1 → 0` 为方案指定术语。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 19_alpha_indices_compass.py
"""
import math
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

s.text(400, 54, "α diversity", 34, BLUE, "middle", "bold")

CX, CY, R = 400, 344, 62

# 五张卡片：(中心x, 中心y, 宽, 高, 指数名, 方案原句或记法, 边框色, 底色, 名字色)
CARDS = [
    (400, 138, 304, 104, "Observed", "种类数极度依赖深度", ORANGE, ORANGE_TINT, ORANGE_DEEP),
    (170, 322, 244, 110, "Faith's PD", None, PURPLE, PURPLE_TINT, BLUE),
    (638, 322, 244, 104, "Chao1", "n1 → 0", BLUE, BLUE_TINT, BLUE),
    (250, 558, 250, 104, "Shannon", "丰富均匀首选", GREEN, GREEN_TINT, GREEN),
    (560, 558, 250, 104, "Simpson", "优势度查垄断", CYAN, CYAN_TINT, CYAN_DEEP),
]


def edge_point(cx, cy, w, h, ux, uy, inset=22):
    """从卡片中心沿 (ux,uy) 反向外推，落在卡片内缩 inset 后的边框上。"""
    tx = (w / 2 - inset) / abs(ux) if ux else 1e9
    ty = (h / 2 - inset) / abs(uy) if uy else 1e9
    t = min(tx, ty)
    return cx - ux * t, cy - uy * t


for cx, cy, w, h, name, phrase, ink, tint, ink2 in CARDS:
    s.rect(cx - w / 2, cy - h / 2, w, h, tint, ink, 4, rx=16)
    s.text(cx, cy - (10 if phrase else 26), name, 32, ink2, "middle", "bold")
    if phrase:
        s.text(cx, cy + 34, phrase, 30, INK, "middle")

# Faith's PD 卡内：一棵小树（表示先建树）
BX, BY = 170, 340
s.line(BX, BY - 16, BX, BY + 8, PURPLE, 4)
s.line(BX, BY - 8, BX - 26, BY + 20, PURPLE, 4)
s.line(BX, BY - 8, BX + 26, BY + 20, PURPLE, 4)
for x, y in ((BX, BY - 16), (BX - 26, BY + 22), (BX + 26, BY + 22), (BX, BY + 10)):
    s.circle(x, y, 5, PURPLE)

# 罗盘中心
s.circle(CX, CY, R, BLUE_TINT, BLUE, 4)
s.text(CX, CY + 14, "α", 38, BLUE, "middle", "bold")

# 五条辐条：从圆周指向各卡片，止于卡片边框外 16 单位
for cx, cy, w, h, *_ in CARDS:
    dx, dy = cx - CX, cy - CY
    d = math.hypot(dx, dy)
    ux, uy = dx / d, dy / d
    ex, ey = edge_point(cx, cy, w, h, ux, uy)
    s.line(CX + ux * R, CY + uy * R, ex - ux * 16, ey - uy * 16, PURPLE, 3, dash="9 7")

s.save("19_alpha_indices_compass.svg")

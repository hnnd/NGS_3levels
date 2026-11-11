#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""25_downstream_failure_diagnostic.py — FIG-M07-28 分箱、质量与注释异常体征排查流

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-28（P52，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.5.3、§19.5.7（三处下游异常各自对应一个可查对象：分箱无箱查深度表列数、
污染超标查是否混箱、注释全空查数据库路径与依赖；任何情况都严禁手动改数把指标「调好看」）。
版式：三阶体征卡自上而下=诊断顺序，卡左为体征（深蓝）、卡右为排查动作（青蓝），
右侧窄栏配一枚示意图标（深度表 / 两箱重叠 / 空注释页），只画形态不写数字。
图内汉字 = 方案清单逐字，共 29 字（无箱：查深度表 / 污染超标：查混箱 /
注释空：查库路径 / 严禁手动调数）。
红色一处：底部虚线框与「严禁手动调数」属同一语义组。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 25_downstream_failure_diagnostic.py
"""
import sys

s = None
sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()


def two_part(cx, y, head, tail, size=34, hcol=BLUE, tcol=CYAN_DEEP):
    """一行两段文字（体征深蓝 + 排查动作青蓝），整体按 cx 居中。"""
    wh = text_width(head, size, True)
    wt = text_width(tail, size, True)
    x = cx - (wh + wt) / 2
    s.text(x, y, head, size, hcol, "start", "bold")
    s.text(x + wh, y, tail, size, tcol, "start", "bold")


CARDS = (
    (128, "无箱：", "查深度表"),
    (292, "污染超标：", "查混箱"),
    (456, "注释空：", "查库路径"),
)

CW, CH, CX = 576, 104, 352          # 卡片宽度 / 高度 / 文字中心

for i, (y, head, tail) in enumerate(CARDS):
    s.rect(64, y, CW, CH, WHITE, BLUE, 3, rx=16)
    s.circle(122, y + CH / 2, 32, BLUE_TINT, BLUE, 3)
    s.text(122, y + CH / 2 + 11, str(i + 1), 30, BLUE, "middle", "bold")
    two_part(CX + 18, y + CH / 2 + 12, head, tail)
    if i < len(CARDS) - 1:
        s.arrow(352, y + CH + 4, 352, y + CH + 44, GRAY, 4, 14)

# ---------------- 右侧图标栏：三个可查对象 ----------------
ICON_X = 690

# ① 深度表：3×3 小格
for r in range(3):
    for c in range(3):
        s.rect(ICON_X - 42 + c * 30, 152 + r * 28, 24, 22,
               CYAN_TINT if (r + c) % 2 else CYAN, rx=4)

# ② 混箱：两个重叠的箱
s.circle(ICON_X - 18, 338, 30, GREEN_TINT, GREEN, 3)
s.circle(ICON_X + 18, 338, 30, ORANGE_TINT, ORANGE_DEEP, 3)

# ③ 注释空：一页空表
s.rect(ICON_X - 32, 480, 64, 84, WHITE, GRAY, 3, rx=8)
for k in range(3):
    s.rect(ICON_X - 22, 498 + k * 20, 44, 6, PANEL, rx=3)
s.line(ICON_X - 32, 480, ICON_X + 32, 480 + 18, GRAY, 3)

# ---------------- 红色语义组：严禁手动调数 ----------------
s.rect(96, 578, 608, 88, WHITE, RED, 4, rx=16, dash="12 9")
s.text(400, 636, "严禁手动调数", 36, RED, "middle", "bold")

s.save("25_downstream_failure_diagnostic.svg")

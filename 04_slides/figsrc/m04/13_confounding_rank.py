#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-13 2×2 完全混杂秩亏 vs 平衡设计满秩。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-13；配色：spec.md §2。
依据：教材 §14.4.5，讲义 ⑨-E4。"""
from svghelp import *

s = SVG()


def grid(x0, y0, cells, batch_of_col):
    cw, chh = 150, 90
    for r in range(2):
        for c in range(2):
            x = x0 + c * cw
            y = y0 + r * chh
            treat = cells[r][c]
            zh = {"Control": "对照", "Treat": "处理"}[treat]
            fill = BLUE_TINT if treat == "Control" else GREEN_TINT
            s.rect(x + 4, y + 4, cw - 8, chh - 8, fill,
                   batch_of_col(c), 5, rx=10)
            s.text(x + cw / 2, y + chh / 2 + 10, zh, 30, INK, "middle",
                   "bold")
    s.text(x0 + cw / 2, y0 - 18, "批次 1", 30, BLUE, "middle", "bold")
    s.text(x0 + 3 * cw / 2, y0 - 18, "批次 2", 30, PURPLE, "middle", "bold")


# ---- 左：完全混杂 ----
s.label(200, 50, ["批次与处理完全绑定"], 30, RED, weight="bold")
grid(70, 110, [["Control", "Control"], ["Treat", "Treat"]],
     lambda c: BLUE if c == 0 else PURPLE)
s.rect(24, 340, 352, 88, RED_TINT, RED, 5, rx=12)
s.text(200, 378, "秩 2 < 参数 3", 30, INK, "middle", "bold")
s.text(200, 414, "qr() · 不可估", 30, GRAY, "middle")
s.text(200, 472, "批次 ≡ 处理", 30, GRAY, "middle")

# ---- 右：平衡设计 ----
s.label(600, 50, ["平衡分布满秩"], 30, GREEN, weight="bold")
grid(470, 110, [["Control", "Treat"], ["Control", "Treat"]],
     lambda c: BLUE if c == 0 else PURPLE)
s.rect(460, 340, 280, 88, GREEN_TINT, GREEN, 5, rx=12)
s.text(600, 378, "满秩", 30, GREEN, "middle", "bold")
s.text(600, 414, "效应可分离", 30, GREEN, "middle")

# ---- 底部分界 ----
s.line(400, 100, 400, 440, PANEL, 4, dash="14 12")
s.label(400, 542, ["矩阵秩亏不可估"], 30, INK)
s.label(400, 612, ["效应无偏分解"], 30, INK)
s.text(400, 660, "完全混杂 → 写入边界；平衡设计 → 无偏", 30, GRAY,
       "middle")

s.save("13_confounding_rank.svg")

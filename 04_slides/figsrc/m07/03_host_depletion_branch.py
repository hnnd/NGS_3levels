#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""03_host_depletion_branch.py — FIG-M07-04 双路线前置与去宿主分流

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-04（P16，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.1（去宿主是两条路线共用的前置；命中剔除、未比对进入双路线；误删不可逆）。
图内汉字 = 方案清单逐字，共 27 字（宿主参考比对 / 比对命中：剔除 / 未比对：进入双路线 /
误删不可逆）。「原始读段」按方案只画读段条形图标、不写字（写了会与清单不一致）。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 03_host_depletion_branch.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 输入：原始读段（图标表达） ----------------
s.rect(96, 52, 288, 82, BLUE_TINT, BLUE, 4, rx=41)
for i in range(4):
    s.rect(136 + i * 58, 82, 44, 24, CYAN if i % 2 == 0 else CYAN_DEEP, rx=6)

s.arrow(240, 144, 240, 190, CYAN, 5, 14)

# ---------------- 比对模块 ----------------
s.rect(56, 190, 368, 130, CYAN_TINT, CYAN, 4, rx=18)
s.text(240, 268, "宿主参考比对", 36, CYAN_DEEP, "middle", "bold")

# ---------------- 两路分流 ----------------
s.arrow(430, 226, 494, 226, ORANGE_DEEP, 5, 14)
s.arrow(430, 284, 494, 470, GREEN, 5, 14)

# 剔除分支（橙）：命中宿主 → 丢弃，不可逆
s.rect(494, 160, 272, 132, ORANGE_TINT, ORANGE_DEEP, 4, rx=18)
s.label(630, 226, ["比对命中：", "剔除"], 32, ORANGE_DEEP, "middle", "bold")

s.text(630, 342, "误删不可逆", 32, RED, "middle", "bold")

# 保留分支（绿）：未比对 → 进入双路线
s.rect(494, 432, 272, 132, GREEN_TINT, GREEN, 4, rx=18)
s.label(630, 498, ["未比对：", "进入双路线"], 32, GREEN, "middle", "bold")

s.save("03_host_depletion_branch.svg")

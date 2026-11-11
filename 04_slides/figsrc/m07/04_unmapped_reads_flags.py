#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_unmapped_reads_flags.py — FIG-M07-05 两种「未比对」判定树与位掩码

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-05（P17，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.1（Bowtie2 `--un-conc-gz` 的「非一致对」含一端比对上的片段；
SAMtools `-f 12` 是两端都未比对，位掩码 0x4+0x8；两种口径不可混用）。
图内汉字 = 方案清单逐字，共 29 字（非一致对：含单端比对 / 两端均未比对：位掩码十二 /
口径不同勿混用）；工具名与位掩码按原文保留英文/数字。无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 04_unmapped_reads_flags.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

CARDS = [
    (32, "Bowtie2", "--un-conc-gz", ["非一致对：", "含单端比对"],
     CYAN, CYAN_TINT, CYAN_DEEP, "one"),
    (416, "SAMtools", "-f 12", ["两端均未比对：", "位掩码十二"],
     GREEN, GREEN_TINT, GREEN, "both"),
]
CW, CH, CY = 352, 460, 72

for x, tool, flag, lines, ink, tint, deep, kind in CARDS:
    s.rect(x, CY, CW, CH, tint, ink, 4, rx=18)
    cx = x + CW / 2
    s.text(cx, CY + 78, tool, 36, deep, "middle", "bold")
    s.text(cx, CY + 128, flag, 30, GRAY, "middle")

    # 一对读段示意：命中宿主的一端实心，未命中的空心
    for k in range(2):
        ex = x + 62 + k * 130
        ey = CY + 196
        hit = (kind == "one" and k == 1)
        s.rect(ex, ey, 76, 26,
               deep if hit else WHITE, deep if hit else GRAY, 4, rx=6)
        s.text(ex + 38, ey + 84, "R1" if k == 0 else "R2", 32, GRAY, "middle")

    s.label(cx, CY + 360, lines, 34, deep, "middle", "bold")

# ---------------- 中间警示：竖向虚线落在两卡空档，结论写在两卡下方 ----------------
s.line(400, 108, 400, 470, RED, 5, dash="12 10")
s.label(400, 604, ["口径不同勿混用"], 34, RED, "middle", "bold")

# 两侧指向中间的红色小箭头（示意「两种口径不可混淆」）
s.arrow(352, 400, 388, 400, RED, 5, 12)
s.arrow(448, 400, 412, 400, RED, 5, 12)

s.save("04_unmapped_reads_flags.svg")

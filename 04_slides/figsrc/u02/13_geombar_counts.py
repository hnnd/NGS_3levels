#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_geombar_counts.py — 生成 13_geombar_counts.svg
（FIG-U02-13：geom_bar() 会替你数行数）

方案：reviews/course/U02_FIGP_001.md §4 FIG-U02-13（P38，cols 一栏，viewBox 800×700）。
数据：柱高全 1 为机制描述（stat="count" vs "identity"），无数值设例；
小表数值 3 / 5 沿用教材 §3.4.7 QUAST 设例的 contig 数（3 条、5 条），仅作「表里的值」示意。
依据：教材 §3.4.6 L207。红 1 处＝等高结果（横线 + 「柱高全等于 1」）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 13_geombar_counts.py
"""
from svghelp import *  # noqa: F401,F403

ROWS = [("Canu", "3"), ("Flye", "5")]


def main():
    s = SVG(800, 700)

    s.text(136, 56, "每类一行的表", 32, BLUE, "middle", "bold")
    s.rect(16, 84, 240, 208, WHITE, BLUE, 4, rx=8)
    s.rect(16, 84, 240, 48, BLUE)
    s.text(88, 118, "assembler", 30, WHITE, "middle", "bold")
    s.text(208, 118, "value", 30, WHITE, "middle", "bold")
    for i, (g, v) in enumerate(ROWS):
        y = 132 + i * 80
        s.rect(16, y, 240, 80, WHITE if i % 2 == 0 else BLUE_TINT)
        s.line(160, y, 160, y + 80, PANEL, 3)
        s.text(88, y + 53, g, 32, INK, "middle")
        s.text(208, y + 53, v, 32, INK, "middle")
    s.rect(16, 84, 240, 208, "none", BLUE, 4, rx=8)

    s.text(406, 56, "geom_bar()", 30, GRAY, "middle", "bold")
    s.arrow(258, 188, 314, 200, CYAN, 7)
    s.rect(316, 84, 180, 366, WHITE, BLUE, 4, rx=8)
    s.line(330, 420, 482, 420, INK, 3)
    s.rect(330, 270, 56, 150, BLUE)
    s.rect(420, 270, 56, 150, BLUE)
    s.line(322, 270, 490, 270, RED, 5)
    s.text(358, 456, "Canu", 30, GRAY, "middle")
    s.text(448, 456, "Flye", 30, GRAY, "middle")
    s.text(406, 530, "柱高全等于 1", 32, RED, "middle", "bold")

    s.text(672, 56, "geom_col()", 30, GRAY, "middle", "bold")
    s.arrow(498, 200, 558, 188, CYAN, 7)
    s.rect(560, 84, 224, 366, WHITE, BLUE, 4, rx=8)
    s.line(572, 420, 772, 420, INK, 3)
    s.rect(588, 330, 56, 90, GREEN)
    s.rect(692, 270, 56, 150, GREEN)
    s.text(616, 456, "Canu", 30, GRAY, "middle")
    s.text(720, 456, "Flye", 30, GRAY, "middle")
    s.text(672, 530, "才用表里的值", 32, GREEN, "middle", "bold")
    s.save("13_geombar_counts.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

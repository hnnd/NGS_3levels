#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""23_stacked_bar_vs_upset_plot.py — 23_stacked_bar_vs_upset_plot.svg
（FIG-M02-29，P67，cols）：堆叠柱丢交集身份 vs UpSet 点阵保留交集【new-svg】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-29。
依据：教材 §11.4.4；讲义 ⑤ 5.6。设例：家族 A+B 2 个、A+C 2 个、A+B+C 1 个。
无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 23_stacked_bar_vs_upset_plot.py
"""
from svghelp import (BLUE, GRAY, GREEN, INK, PANEL, RED, SVG, WHITE)


def cross_mark(s, cx, cy, r, color):
    s.circle(cx, cy, r, WHITE, color, 6)
    s.line(cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5, color, 7,
           cap="round")
    s.line(cx - r * 0.5, cy + r * 0.5, cx + r * 0.5, cy - r * 0.5, color, 7,
           cap="round")


def check_mark(s, cx, cy, r, color):
    s.circle(cx, cy, r, WHITE, color, 6)
    s.line(cx - r * 0.45, cy, cx - r * 0.1, cy + r * 0.4, color, 7,
           cap="round")
    s.line(cx - r * 0.1, cy + r * 0.4, cx + r * 0.55, cy - r * 0.45, color,
           7, cap="round")


def main():
    s = SVG(800, 700)

    # 左图（错误替代）：按共有株数堆叠，A+B 与 A+C 被合并压平
    s.rect(30, 70, 350, 430, WHITE, "#E9E9E5", 3, rx=14)
    base = 450
    scale = 60.0
    for cat, count in ((2, 4), (3, 1)):
        bx = 60 + (cat - 1) * 130
        s.rect(bx, base - count * scale, 80, count * scale, BLUE)
        s.text(bx + 40, base - count * scale - 18, str(count), 30, BLUE,
               "middle", "bold")
        s.text(bx + 40, base + 40, str(cat), 32, INK, "middle", "bold")
    s.line(50, base, 360, base, INK, 4)
    cross_mark(s, 76, 116, 26, RED)
    s.text(205, 536, "堆叠柱丢交集身份", 32, RED, "middle", "bold")
    s.text(205, 588, "A+B 与 A+C 混为 2 株", 30, RED, "middle", "bold")

    # 右图（正确规范）：UpSet 点阵保留交集身份
    s.rect(420, 70, 350, 430, WHITE, "#E9E9E5", 3, rx=14)
    rows = {"A": 330, "B": 392, "C": 454}
    for lab, ry in rows.items():
        s.text(450, ry + 11, lab, 32, INK, "middle", "bold")
    cols = [("A+B", 540, ("A", "B"), 2), ("A+C", 630, ("A", "C"), 2),
            ("A+B+C", 720, ("A", "B", "C"), 1)]
    top_base = 250
    for lab, cx, members, count in cols:
        s.rect(cx - 28, top_base - count * scale, 56, count * scale, GREEN)
        s.text(cx, top_base - count * scale - 16, str(count), 30, GREEN,
               "middle", "bold")
        s.text(cx, 500, lab, 30, GRAY, "middle", "bold")
        ys = [rows[m] for m in members]
        if len(ys) > 1:
            s.line(cx, ys[0], cx, ys[-1], INK, 4)
        for ry in ys:
            s.circle(cx, ry, 13, BLUE)
    check_mark(s, 466, 116, 26, GREEN)
    s.text(595, 536, "UpSet 点阵保留交集", 32, GREEN, "middle", "bold")

    # 底部红色警示
    s.rect(200, 620, 400, 60, RED, rx=14)
    s.text(400, 662, "不可作等价替代", 34, WHITE, "middle", "bold")

    s.save("23_stacked_bar_vs_upset_plot.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

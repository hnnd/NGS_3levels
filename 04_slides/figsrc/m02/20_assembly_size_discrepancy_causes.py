#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_assembly_size_discrepancy_causes.py — 20_assembly_size_discrepancy_causes.svg
（FIG-M02-26，P56，cols）：组装总长偏离勘测估计的三种成因决策【new-svg】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-26。
依据：教材 §8.4.9；讲义 ⑥ 6.1。无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 20_assembly_size_discrepancy_causes.py
"""
from svghelp import (BLUE, GRAY, INK, ORANGE, PURPLE, RED, SVG, WHITE)


def icon_collapse(s, x, y, color):
    # 覆盖度骤升：低柱 + 高柱
    s.rect(x, y + 30, 26, 30, color)
    s.rect(x + 40, y, 26, 60, color)


def icon_haplotype(s, x, y, color):
    # 单倍型未分：两个交叠圆
    s.circle(x + 22, y + 30, 20, WHITE, color, 5)
    s.circle(x + 48, y + 30, 20, WHITE, color, 5)


def icon_contam(s, x, y, color):
    # 外源污染：散点
    for dx, dy in ((0, 8), (26, 26), (52, 4), (10, 44), (40, 52), (62, 34)):
        s.circle(x + dx, y + dy, 7, color)


def main():
    s = SVG(800, 700)

    # 顶端分歧框（英文标签保汉字预算）
    s.rect(190, 66, 420, 80, WHITE, RED, 6, rx=16)
    s.text(400, 116, "assembly total ≠ survey estimate", 32, INK, "middle",
           "bold")

    rows = [
        (210, BLUE, "偏小：重复塌缩，查覆盖度", icon_collapse),
        (350, ORANGE, "偏大：单倍型未分，D 异常高", icon_haplotype),
        (490, PURPLE, "偏大：外源污染，查分类", icon_contam),
    ]
    for y, color, label, icon in rows:
        s.line(400, 148, 200, y + 38, color, 5)
        s.arrow(200, y + 38, 188, y + 38, color, 5)
        s.rect(60, y, 120, 76, WHITE, color, 5, rx=14)
        icon(s, 84, y + 8, color)
        s.text(210, y + 48, label, 32, INK, "start", "bold")

    s.save("20_assembly_size_discrepancy_causes.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

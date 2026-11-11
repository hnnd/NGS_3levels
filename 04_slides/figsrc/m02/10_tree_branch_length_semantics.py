#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_tree_branch_length_semantics.py — 10_tree_branch_length_semantics.svg
（FIG-M02-14，P33，cols）：替换数树 vs 超度量树支长语义对照【new-svg】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-14（FT11-02 题材）。
依据：教材 §11.4.6、§11.5.4。无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 10_tree_branch_length_semantics.py
"""
from svghelp import (BLUE, GRAY, GREEN, INK, RED, SVG, WHITE)


def leaf(s, cx, cy, lab):
    s.circle(cx, cy, 18, BLUE)
    s.text(cx, cy + 9, lab, 30, WHITE, "middle", "bold")


def main():
    s = SVG(800, 700)

    # 左面板：替换数树（枝长不等，长枝红色高亮）
    s.rect(30, 70, 340, 500, WHITE, "#E9E9E5", 3, rx=14)
    s.text(200, 116, "替换数树：叶到根不等长", 30, BLUE, "middle", "bold")
    s.line(200, 150, 200, 240, BLUE, 6)            # 根 → 内节点
    s.circle(200, 142, 10, BLUE)
    s.line(192, 240, 92, 400, BLUE, 6)             # → sp.1（短）
    s.line(200, 240, 200, 366, BLUE, 6)            # → sp.2（中）
    s.line(208, 240, 314, 510, RED, 7)             # → sp.3（长枝，红）
    leaf(s, 88, 424, "1")
    leaf(s, 200, 390, "2")
    leaf(s, 320, 532, "3")
    s.text(88, 474, "sp.1", 30, GRAY, "middle")
    s.text(200, 440, "sp.2", 30, GRAY, "middle")
    s.text(320, 582, "sp.3", 30, GRAY, "middle")

    # 右面板：超度量树（叶到根严格等长，绿框 = CAFE5 唯一合格输入）
    s.rect(410, 70, 360, 500, WHITE, GREEN, 7, rx=14)
    s.text(590, 116, "超度量树：叶到根严格等长", 30, BLUE, "middle", "bold")
    s.text(590, 166, "CAFE5 only valid input", 30, GREEN, "middle", "bold")
    s.line(590, 190, 590, 320, BLUE, 6)
    s.circle(590, 182, 10, BLUE)
    s.line(582, 320, 482, 500, BLUE, 6)
    s.line(590, 320, 590, 500, BLUE, 6)
    s.line(598, 320, 698, 500, BLUE, 6)
    leaf(s, 478, 524, "1")
    leaf(s, 590, 524, "2")
    leaf(s, 702, 524, "3")

    # 红色警告：长枝 ≠ 漫长时间
    s.arrow(316, 522, 262, 606, RED, 6)
    s.text(240, 652, "长枝被误读为漫长时间", 32, RED, "middle", "bold")

    s.save("10_tree_branch_length_semantics.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

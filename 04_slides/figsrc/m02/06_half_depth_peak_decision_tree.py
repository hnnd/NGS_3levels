#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_half_depth_peak_decision_tree.py — 06_half_depth_peak_decision_tree.svg
（FIG-M02-08，P20，cols）：杂合/污染半深度峰与四条确认检查决策树【new-svg】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-08。数据：主峰 43×、
半深度峰 21×（相对主峰高度 139%）——demos/ch08_kmer_spectrum.py --selftest
场景二（D=60×、杂合/分歧率 0.02、种子 20261103）现跑实测。
无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 06_half_depth_peak_decision_tree.py
"""
from svghelp import (BLUE, GRAY, INK, ORANGE, RED, SVG, WHITE)

ORANGE_TINT = "#FBE3D9"


def main():
    s = SVG(800, 700)

    # 左面板：双峰频谱示意（主峰 43× 蓝、半深度峰 21× 橙，高 139%）
    s.rect(30, 70, 340, 510, WHITE, "#E9E9E5", 3, rx=14)
    base = 470
    s.line(60, base, 350, base, INK, 4)
    # 主峰（43×）：高 160；半深度峰（21×）：高 160×1.39≈222
    s.polygon([(240, base), (240 - 52, base), (240, base - 160)], BLUE)
    s.polygon([(240, base), (240 + 52, base), (240, base - 160)], BLUE)
    s.polygon([(130, base), (130 - 40, base), (130, base - 222)], ORANGE)
    s.polygon([(130, base), (130 + 40, base), (130, base - 222)], ORANGE)
    s.text(130, 470 - 222 - 12, "21×", 30, ORANGE, "middle", "bold")
    s.text(240, 470 - 160 - 12, "43×", 30, BLUE, "middle", "bold")
    s.text(185, 516, "主峰 43×", 30, INK, "middle", "bold")
    s.text(185, 552, "伴半深度峰 21×", 30, INK, "middle", "bold")

    # 右侧决策树
    s.rect(470, 90, 300, 84, WHITE, BLUE, 6, rx=14)
    s.text(620, 143, "四条基本检查", 34, BLUE, "middle", "bold")
    s.arrow(620, 178, 620, 258, GRAY, 6)
    s.line(620, 258, 470, 340, GRAY, 6)
    s.line(620, 258, 470, 490, GRAY, 6)
    s.arrow(470, 340, 470, 352, RED, 6)
    s.arrow(470, 490, 470, 502, ORANGE, 6)
    # 下分支（≥2 条同向）：红框判污染
    s.rect(330, 356, 440, 84, RED, rx=14)
    s.text(550, 409, "至少两条同向才判污染", 32, WHITE, "middle", "bold")
    # 上分支（仅 1 条）：橙底写原因待定
    s.rect(330, 506, 440, 84, ORANGE_TINT, ORANGE, 6, rx=14)
    s.text(550, 559, "否则写原因待定", 32, INK, "middle", "bold")

    s.save("06_half_depth_peak_decision_tree.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

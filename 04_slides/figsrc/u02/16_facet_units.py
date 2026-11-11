#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_facet_units.py — 生成 16_facet_units.svg
（FIG-U02-16：分面是因为单位不同，不是量级不同）

方案：reviews/course/U02_FIGP_001.md §4 FIG-U02-16（P41，cols 一栏，viewBox 800×700）。
数据：无量字数字（定性示意）；「换算后彼此不到 3 倍」留在 deck 页面文字（W5 规避），不进图。
分面标题用英文单位（contigs (n) / N50 (Mb)），图内汉字计数与方案一致（21）。
依据：教材 §3.4.6 L219、§3.4.7 L241。红 1 处＝错误面板（压扁 + Value 打叉同场景）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 16_facet_units.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    s.text(205, 56, "混在一根轴", 32, INK, "middle", "bold")
    s.rect(30, 84, 350, 476, WHITE, BLUE, 4, rx=8)
    s.line(90, 140, 90, 500, INK, 3)
    s.line(60, 500, 360, 500, INK, 3)
    s.rect(130, 180, 80, 320, BLUE)
    s.rect(250, 476, 80, 24, RED)
    s.text(290, 452, "压扁了", 30, RED, "middle", "bold")
    s.text(110, 128, "Value", 30, GRAY, "middle", "bold")
    s.line(96, 116, 124, 140, RED, 5)
    s.line(124, 116, 96, 140, RED, 5)
    s.text(170, 536, "contigs", 30, GRAY, "middle")
    s.text(290, 536, "N50", 30, GRAY, "middle")

    s.text(595, 56, "分面各标单位", 32, INK, "middle", "bold")
    for x0, title in ((410, "contigs (n)"), (600, "N50 (Mb)")):
        s.rect(x0, 84, 170, 476, WHITE, BLUE, 4, rx=8)
        s.rect(x0, 84, 170, 56, BLUE)
        s.text(x0 + 85, 122, title, 30, WHITE, "middle", "bold")
        s.line(x0 + 30, 160, x0 + 30, 500, INK, 3)
        s.line(x0 + 16, 500, x0 + 154, 500, INK, 3)
    s.rect(450, 190, 90, 310, BLUE)
    s.rect(640, 240, 90, 260, BLUE)
    for cx, cy_ in ((555, 515), (745, 515)):
        s.circle(cx, cy_, 16, GREEN)
        s.line(cx - 8, cy_, cx - 2, cy_ + 8, WHITE, 5)
        s.line(cx - 2, cy_ + 8, cx + 10, cy_ - 10, WHITE, 5)

    s.text(400, 664, "主因是单位不同", 32, INK, "middle", "bold")
    s.save("16_facet_units.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

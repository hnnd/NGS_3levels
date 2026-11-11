#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_workflow_five_steps_pipeline.py — 17_workflow_five_steps_pipeline.svg
（FIG-M02-23，P44，cols）：组装与泛基因组五步流程骨架与两处预跑自检点【new-svg】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-23。
依据：讲义 ⑤ 流程骨架；教材 §8.4.9、§11.4.2。无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 17_workflow_five_steps_pipeline.py
"""
from svghelp import (BLUE, CYAN, GRAY, GREEN, RED, SVG, WHITE)


def shield(s, cx, cy, r=30):
    s.polygon([(cx, cy - r), (cx + r, cy - r * 0.55),
               (cx + r, cy + r * 0.25), (cx, cy + r),
               (cx - r, cy + r * 0.25), (cx - r, cy - r * 0.55)], GREEN)
    s.line(cx - r * 0.45, cy, cx - r * 0.1, cy + r * 0.38, WHITE, 6,
           cap="round")
    s.line(cx - r * 0.1, cy + r * 0.38, cx + r * 0.5, cy - r * 0.35, WHITE,
           6, cap="round")


def main():
    s = SVG(800, 700)
    s.text(790, 44, "lecture ⑤ pipeline (schematic)", 30, GRAY, "end")

    steps = [
        ("①勘测", "Jellyfish + GenomeScope", BLUE, False),
        ("②组装", "Flye", BLUE, False),
        ("③质检自检点", "QUAST + BUSCO", BLUE, True),
        ("④聚类自检点", "Prokka + OrthoFinder", BLUE, True),
        ("⑤比较矩阵", "0/1 matrix + CAFE5", BLUE, False),
    ]
    x, w, h = 130, 540, 78
    y = 66
    for i, (lab, sub, color, chk) in enumerate(steps):
        s.rect(x, y, w, h, WHITE, color, 6, rx=14)
        s.text(x + w / 2 - (46 if chk else 0), y + 40, lab, 34, color,
               "middle", "bold")
        s.text(x + w / 2, y + 68, sub, 30, GRAY, "middle")
        if chk:
            shield(s, x + w - 52, y + h / 2)
        if i < 4:
            s.arrow(x + w / 2, y + h + 4, x + w / 2, y + h + 26, CYAN, 7)
        y += h + 30

    # 底部红色警示
    s.rect(200, 596, 400, 64, RED, rx=14)
    s.text(400, 640, "不合格严禁向下传导", 34, WHITE, "middle", "bold")

    s.save("17_workflow_five_steps_pipeline.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

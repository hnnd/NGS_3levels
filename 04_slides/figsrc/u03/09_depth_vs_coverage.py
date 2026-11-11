#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_depth_vs_coverage.py — 生成 09_depth_vs_coverage.svg（FIG-U03-09：深度 vs 覆盖度）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-09（P29，cols 一栏，800×700）。
教材依据：chapters/ch04/manuscript.qmd §4.4.1。
垂直方向读段多层堆叠 = 深度 D（×）；水平方向有读段覆盖的比例 = 覆盖度（%）；
中间留白缺口 = 未覆盖（深度 0）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 09_depth_vs_coverage.py
"""
from svghelp import *  # noqa: F401,F403

import random


def main():
    rng = random.Random(20261110)

    s = SVG(800, 700)
    s.text(400, 50, "深度是垂直堆叠层数", 34, BLUE, "middle", "bold")
    s.text(400, 92, "覆盖度是水平覆盖比例", 30, GRAY, "middle", "bold")

    genome_x0, genome_x1, genome_y = 90, 740, 580

    # 读段堆叠（青色块），中间留缺口 400–490
    lanes = {}
    x = genome_x0
    while x < genome_x1 - 30:
        if 400 <= x < 490:
            x = 490
            continue
        length = rng.randint(50, 90)
        lanes.setdefault(0, [])
        # 简单堆叠：按起点顺序轮流放 1–4 层
        lane = rng.randint(0, 3)
        lanes.setdefault(lane, [])
        lanes[lane].append((x, min(length, genome_x1 - x)))
        x += rng.randint(18, 34)
    for lane, segs in lanes.items():
        y = genome_y - 46 * (lane + 1)
        for sx, ln in segs:
            s.rect(sx, y, ln, 34, CYAN, rx=6)

    # 参考基因组基线（深灰）
    s.line(genome_x0, genome_y, genome_x1, genome_y, GRAY, 6)
    s.text(genome_x0, genome_y + 44, "1", 30, GRAY, "start", "bold")
    s.text(genome_x1, genome_y + 44, "G", 30, GRAY, "end", "bold")

    # 垂直标尺：深度 D
    s.line(60, genome_y - 4 * 46 - 10, 60, genome_y, PURPLE, 6)
    s.polygon([(52, genome_y - 4 * 46 - 2), (68, genome_y - 4 * 46 - 2),
               (60, genome_y - 4 * 46 - 22)], PURPLE)
    s.text(10, 320, "D（×）", 30, PURPLE, "start", "bold")

    # 水平标尺：覆盖度（绿括号，跨被覆盖区段）
    bracket_y = genome_y + 68
    s.line(genome_x0, bracket_y, 400, bracket_y, GREEN, 6)
    s.line(490, bracket_y, genome_x1, bracket_y, GREEN, 6)
    s.text((genome_x0 + 400) / 2, bracket_y + 38, "覆盖", 30, GREEN, "middle",
           "bold")
    s.text((490 + genome_x1) / 2, bracket_y + 38, "覆盖", 30, GREEN, "middle",
           "bold")

    # 红色焦点：未覆盖缺口
    s.rect(400, genome_y - 4 * 46 - 16, 90, 4 * 46 + 22, "none", RED, 5,
           dash="14 10")
    s.rect(300, 140, 290, 60, RED, rx=12)
    s.text(445, 180, "未覆盖缺口（D=0）", 30, WHITE, "middle", "bold")

    s.save("09_depth_vs_coverage.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

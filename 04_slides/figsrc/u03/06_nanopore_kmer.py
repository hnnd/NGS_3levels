#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_nanopore_kmer.py — 生成 06_nanopore_kmer.svg（FIG-U03-06：纳米孔感应窗口）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-06（P24，cols 一栏，800×700）。
教材依据：chapters/ch04/manuscript.qmd §4.4.4。
左：跨膜纳米孔，孔道狭窄感应区同时包容 5–6 个碱基（红框窗口）；
右：变化序列电流呈阶跃波（squiggle），同聚物电流平直无阶跃。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 06_nanopore_kmer.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 50, "纳米孔感应窗口时序电流", 34, BLUE, "middle", "bold")
    s.text(400, 92, "同聚物平直无阶跃", 30, GRAY, "middle", "bold")

    # ── 左：纳米孔剖面 ──
    s.rect(40, 120, 320, 550, WHITE, PANEL, 3, rx=16)
    # 磷脂双分子层（两层）
    s.rect(70, 300, 260, 26, "#94A3B8", rx=13)
    s.rect(70, 380, 260, 26, "#94A3B8", rx=13)
    # 孔道蛋白
    s.polygon([(160, 300), (240, 300), (222, 380), (178, 380)], PURPLE)
    # 红框感应窗口
    s.rect(170, 316, 60, 74, "none", RED, 5, rx=8)
    s.text(200, 470, "5–6 mer", 32, RED, "middle", "bold")
    s.arrow(200, 450, 200, 396, RED, 5)
    # 穿孔 ssDNA（竖线 + 碱基点）
    s.line(200, 140, 200, 560, CYAN_DEEP, 8)
    for y in range(160, 560, 36):
        s.circle(200, y, 9, CYAN)

    # ── 右上：变化序列 → 阶跃波 ──
    s.rect(400, 120, 360, 250, WHITE, PANEL, 3, rx=16)
    s.text(430, 162, "k-mer 变化", 30, GREEN, "start", "bold")
    steps = [(430, 320), (470, 250), (510, 320), (550, 210), (590, 290),
             (630, 230), (670, 320), (710, 260)]
    s.polyline(steps, GREEN, 7)

    # ── 右下：同聚物 → 平直电流 ──
    s.rect(400, 420, 360, 250, WHITE, PANEL, 3, rx=16)
    s.text(430, 462, "AAAAAA", 30, INK, "start", "bold")
    s.line(430, 580, 730, 580, RED, 7, cap="round")
    s.text(580, 560, "同聚物电流平直", 30, RED, "middle", "bold")

    s.save("06_nanopore_kmer.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

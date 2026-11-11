#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""23_fastq_corruption.py — 生成 23_fastq_corruption.svg（FIG-U03-23：FASTQ 损坏两模式）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-23（P64，cols 一栏，800×700）。
教材依据：chapters/ch05/manuscript.qmd §5.5.4、demos/ch05_phred_fastq.py。
左：尾部截断（行数 % 4 ≠ 0，rc=5 拦在门外）；右：中部缺行凑整（行数整除 4，
内容全线错位，rc=0 静默放行）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 23_fastq_corruption.py
"""
from svghelp import *  # noqa: F401,F403


def record_rows(s, x, y, rows, row_h=34, w=300, broken_from=None):
    """画 FASTQ 行块；broken_from 行起错位（波浪）。"""
    for i, row in enumerate(rows):
        dx = 0
        color = INK
        if broken_from is not None and i >= broken_from:
            dx = 22
            color = RED
        s.text(x + dx, y + i * row_h, row, 26, color, "start", "bold")


def main():
    s = SVG(800, 700)
    s.text(400, 50, "尾部截断行数拦截", 36, BLUE, "middle", "bold")
    s.text(400, 92, "中部缺行凑整错位静默放行", 30, GRAY, "middle", "bold")

    # ── 左：尾部截断（7 行，%4=3）──
    s.rect(30, 120, 350, 480, WHITE, GREEN, 4, rx=14)
    s.text(60, 162, "截断", 30, INK, "start", "bold")
    record_rows(s, 60, 200, ["@r1", "ACGT…", "+", "IIII…",
                             "@r2", "TGCA…", "+"])
    # 截断波浪
    s.path("M 60 438 q 15 -18 30 0 t 30 0 t 30 0", RED, 5, dash="2 10")
    s.text(200, 480, "7 行 % 4 = 3", 30, RED, "middle", "bold")
    s.rect(60, 510, 290, 62, GREEN, rx=12)
    s.text(215, 551, "rc = 5", 30, WHITE, "middle", "bold")
    s.line(96, 524, 116, 556, WHITE, 6)
    s.line(116, 524, 96, 556, WHITE, 6)

    # ── 右：中部缺行凑整（8 行但错位）──
    s.rect(420, 120, 350, 480, WHITE, RED, 5, rx=14)
    s.text(450, 162, "缺行凑整", 30, RED, "start", "bold")
    record_rows(s, 450, 200, ["@r1", "ACGT…", "+", "IIII…",
                              "IIII…", "@r2", "TGCA…", "+"],
                broken_from=4)
    s.text(595, 480, "8 行 % 4 = 0", 30, INK, "middle", "bold")
    s.rect(450, 510, 290, 62, RED, rx=12)
    s.text(605, 551, "rc = 0", 30, WHITE, "middle", "bold")
    s.polyline([(484, 540), (493, 552), (510, 530)], WHITE, 7)

    s.save("23_fastq_corruption.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

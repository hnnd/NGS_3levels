#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_format_tracks.py — 生成 11_format_tracks.svg（FIG-U03-11：格式家族双轨流转）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-11（P34，cols 一栏，800×700）。
教材依据：chapters/ch05/manuscript.qmd §5.1、§5.4.7。
FASTQ 分流为组装线（绿）与比对线（青）；bedtools 侧支吃 BED（0-based 半开，红框）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 11_format_tracks.py
"""
from svghelp import *  # noqa: F401,F403


def node(s, x, y, w, h, lines, stroke, sizes=None, fill=WHITE):
    s.rect(x, y, w, h, fill, stroke, 4, rx=12)
    n = len(lines)
    cy = y + h / 2 - 19 * (n - 1) + 11
    for i, ln in enumerate(lines):
        sz = sizes[i] if sizes else 30
        s.text(x + w / 2, cy, ln, sz, INK, "middle", "bold")
        cy += 40


def main():
    s = SVG(800, 700)
    s.text(400, 50, "组装比对双轨流转", 36, BLUE, "middle", "bold")
    s.text(400, 92, "区间求交求并唯有半开", 30, GRAY, "middle", "bold")

    # 起点 FASTQ
    node(s, 40, 320, 130, 110, ["FASTQ", "raw reads"], CYAN_DEEP,
         sizes=[30, 24])

    # ── 上轨：组装线（绿）──
    s.text(46, 210, "组装线", 30, GREEN, "start", "bold")
    node(s, 200, 150, 140, 110, ["Flye /", "Canu"], GREEN)
    node(s, 354, 150, 114, 110, ["FASTA", "contigs"], GREEN,
         sizes=[30, 24])
    node(s, 482, 150, 104, 110, ["Prokka"], GREEN)
    node(s, 600, 150, 180, 110, ["GFF3 / GTF", "(1-based 闭)"], GREEN,
         sizes=[30, 24])
    s.arrow(168, 350, 196, 240, GREEN, 6)
    for x1, x2 in ((341, 353), (469, 481), (587, 599)):
        s.arrow(x1, 205, x2, 205, GREEN, 5)

    # ── 下轨：比对线（青蓝）──
    s.text(46, 550, "比对线", 30, CYAN_DEEP, "start", "bold")
    node(s, 170, 490, 140, 110, ["BWA /", "Bowtie2"], CYAN_DEEP)
    node(s, 324, 490, 170, 110, ["SAM / BAM", "POS 1-based"], CYAN_DEEP,
         sizes=[30, 24])
    node(s, 508, 490, 130, 110, ["bcftools"], CYAN_DEEP)
    node(s, 652, 490, 140, 110, ["VCF", "(1-based)"], CYAN_DEEP,
         sizes=[30, 24])
    s.arrow(168, 400, 192, 490, CYAN_DEEP, 6)
    for x1, x2 in ((311, 323), (495, 507), (639, 651)):
        s.arrow(x1, 545, x2, 545, CYAN_DEEP, 5)

    # ── 侧支：bedtools → BED（红框焦点）──
    node(s, 200, 330, 190, 56, ["bedtools"], GRAY)
    s.arrow(390, 358, 435, 358, GRAY, 6)
    s.rect(440, 330, 120, 56, WHITE, RED, 6, rx=12)
    s.text(500, 368, "BED", 30, RED, "middle", "bold")
    s.text(500, 448, "0-based 半开，唯有 BED", 30, RED, "middle", "bold")

    s.save("11_format_tracks.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_align_sort_pipeline.py — 生成 12_align_sort_pipeline.svg（FIG-U05-12：比对排序一条管道）

方案：reviews/course/U05_FIGP_001.md §4 FIG-U05-12（P41，cols 一栏，viewBox 800×700）。
R1+R2 → bwa mem → 主流走 stdin（-）→ samtools sort → sorted.bam（绿圆柱）；
stderr 支流（橙）落 logs/bwa_mem.log，红点＝stderr 分流。图中不写参数
（-t/-M/-K/-R 留右栏代码与 P42 参数表，一图一焦点）。
依据教材 §7.6 第 3 步、§7.4.2（stderr 统计）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 12_align_sort_pipeline.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 输入双轨
    s.rect(25, 265, 70, 50, CYAN, rx=10)
    s.text(60, 299, "R1", 30, WHITE, "middle", "bold")
    s.rect(25, 345, 70, 50, CYAN, rx=10)
    s.text(60, 379, "R2", 30, WHITE, "middle", "bold")
    s.arrow(97, 292, 128, 303, CYAN, 6, head=15)
    s.arrow(97, 368, 128, 357, CYAN, 6, head=15)

    # bwa mem
    s.rect(130, 250, 180, 140, BLUE, rx=14)
    s.text(220, 332, "bwa mem", 34, WHITE, "middle", "bold")

    # 主流：stdin 箭头 + 角标
    s.arrow(312, 320, 468, 320, CYAN, 8, head=20)
    s.text(390, 304, "-", 44, CYAN_DEEP, "middle", "bold")
    s.text(390, 362, "是标准输入", 30, INK, "middle", "bold")

    # samtools sort
    s.rect(470, 250, 180, 140, BLUE, rx=14)
    s.text(560, 312, "samtools", 30, WHITE, "middle", "bold")
    s.text(560, 352, "sort", 30, WHITE, "middle", "bold")

    # sorted.bam 绿圆柱
    s.arrow(652, 320, 670, 320, CYAN, 6, head=14)
    s.text(706, 246, "sorted.bam", 30, INK, "middle", "bold")
    s.raw(f'<ellipse cx="706" cy="270" rx="34" ry="11" fill="{GREEN}"/>')
    s.rect(672, 270, 68, 82, GREEN)
    s.raw(f'<ellipse cx="706" cy="352" rx="34" ry="11" fill="{GREEN}"/>')
    s.raw(f'<ellipse cx="706" cy="352" rx="34" ry="11" fill="none" '
          f'stroke="#00776A" stroke-width="3"/>')
    s.text(706, 318, "BAM", 30, WHITE, "middle", "bold")

    # stderr 支流（橙）＋红点
    s.line(220, 392, 220, 516, ORANGE, 6)
    s.circle(220, 452, 9, RED)
    s.text(242, 460, "比对日志走 stderr", 30, INK, "start", "bold")
    s.rect(130, 518, 300, 64, ORANGE, rx=12)
    s.text(280, 560, "logs/bwa_mem.log", 30, INK, "middle", "bold")

    s.save("12_align_sort_pipeline.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

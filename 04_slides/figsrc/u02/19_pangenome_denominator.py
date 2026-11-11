#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_pangenome_denominator.py — 生成 19_pangenome_denominator.svg
（FIG-U02-19：分母错了，类别就翻）

方案：reviews/course/U02_FIGP_001.md §4 FIG-U02-19（P50，cols 一栏，viewBox 800×700）。
数据（教材 §3.4.7 L245 手算）：8/8=1.00 → Core（>=99%，允许缺失 0 株）；
8/10=0.80 → Shell（15–95%，允许缺失 2 株）。不画四类计数 3120/210/890/1450
（CNT-U02-06 已裁定不入 deck）。出现格沿用教材示意（8 株出现 + 2 株缺失）。
红 1 处＝分母错类别翻分支。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 19_pangenome_denominator.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 64, "gene_presence_absence.csv", 30, GRAY, "middle", "bold")

    for i in range(10):
        x = 88 + i * 64
        fill = ORANGE if i < 8 else "#C9C9C3"
        s.rect(x, 90, 64, 64, fill, WHITE, 3)
        s.text(x + 32, 196, f"S{i + 1}", 30, GRAY, "middle")
    s.rect(88, 90, 640, 64, "none", INK, 3)

    s.arrow(400, 156, 230, 252, GRAY, 6)
    s.arrow(400, 156, 570, 252, GRAY, 6)

    s.rect(60, 258, 340, 64, GREEN_TINT, GREEN, 4, rx=10)
    s.text(230, 302, "8 / 8 = 1.00 → Core", 34, GREEN, "middle", "bold")
    s.rect(400, 258, 340, 64, RED_TINT, RED, 4, rx=10)
    s.text(570, 302, "8 / 10 = 0.80 → Shell", 34, RED, "middle", "bold")

    s.text(570, 380, "分母错了类别就翻", 34, RED, "middle", "bold")
    s.text(400, 660, "株数从表结构来", 32, GRAY, "middle", "bold")
    s.save("19_pangenome_denominator.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

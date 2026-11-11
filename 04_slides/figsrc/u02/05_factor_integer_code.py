#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_factor_integer_code.py — 生成 05_factor_integer_code.svg
（FIG-U02-05：因子的内部是整数码）

方案：reviews/course/U02_FIGP_001.md §4 FIG-U02-05（P22，cols 一栏，viewBox 800×700）。
数据（教材 §3.4.2 L118–124 可复核两行，R base 现场可跑）：
as.numeric(f) → 1 2 3（拿到的是码，红）；as.numeric(as.character(f)) → 10 20 50（先解引用，绿）。
红 1 处＝错误取法结果条。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 05_factor_integer_code.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    s.rect(140, 90, 520, 240, WHITE, BLUE, 5, rx=12)
    s.text(175, 163, "水平表", 32, INK, "start", "bold")
    s.text(175, 285, "整数码", 32, INK, "start", "bold")
    for i, (lab, col) in enumerate((("10", ORANGE), ("20", ORANGE), ("50", ORANGE))):
        x = 320 + i * 100
        s.rect(x, 120, 100, 60, ORANGE)
        s.text(x + 50, 163, lab, 34, WHITE, "middle", "bold")
        s.line(x + 50, 182, x + 50, 238, GRAY, 3)
    for i, lab in enumerate(("1", "2", "3")):
        x = 320 + i * 100
        s.rect(x, 240, 100, 60, PURPLE)
        s.text(x + 50, 283, lab, 34, WHITE, "middle", "bold")

    s.text(40, 448, "as.numeric(f)", 30, INK, "start")
    s.arrow(272, 438, 348, 438, GRAY, 5)
    s.rect(360, 408, 240, 60, RED, rx=10)
    s.text(480, 449, "1 2 3", 34, WHITE, "middle", "bold")
    s.text(624, 448, "拿到的是码", 32, RED, "start", "bold")

    s.text(40, 558, "as.numeric(as.character(f))", 30, INK, "start")
    s.arrow(472, 548, 500, 548, GRAY, 5)
    s.rect(512, 518, 200, 60, GREEN, rx=10)
    s.text(612, 559, "10 20 50", 32, WHITE, "middle", "bold")
    s.text(612, 630, "先解引用", 32, GREEN, "middle", "bold")
    s.save("05_factor_integer_code.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

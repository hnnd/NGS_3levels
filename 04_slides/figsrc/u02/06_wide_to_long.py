#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_wide_to_long.py — 生成 06_wide_to_long.svg
（FIG-U02-06：宽转长的行数账）

方案：reviews/course/U02_FIGP_001.md §4 FIG-U02-06（P24，cols 一栏，viewBox 800×700）。
数据（教材手算）：行数 = 12 × 2 = 24（§3.4.3 L160）；2100000 / 1e6 = 2.1（§3.4.3 L147）。
宽表/长表列名与行内容沿用教材 §3.4.3 L143–149 的 QUAST 设例（Canu_01 折三行；
长表 Value 列 N50_bp 写作 2.1e6＝2100000，防列溢出）。
红 1 处＝「少一行都对不上」。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 06_wide_to_long.py
"""
from svghelp import *  # noqa: F401,F403

WIDE_ROWS = [("Canu_01", "3", "2100000"), ("Flye_01", "5", "1700000")]
LONG_ROWS = [("Canu_01", ["Contig_", "Count"], "3"),
             ("Canu_01", ["N50_bp"], "2.1e6"),
             ("Canu_01", ["BUSCO_", "pct"], "98.5")]


def wide(s):
    s.text(206, 66, "宽表", 34, BLUE, "middle", "bold")
    x0, y0 = 16, 90
    cols = [(x0, 160, ["assembler"]), (x0 + 160, 110, ["Contig_", "Count"]),
            (x0 + 270, 110, ["N50_", "bp"])]
    s.rect(x0, y0, 380, 78, BLUE)
    for cx, cw, lines in cols:
        ybase = y0 + (46 if len(lines) == 1 else 32)
        for j, ln in enumerate(lines):
            s.text(cx + cw / 2, ybase + j * 34, ln, 30, WHITE, "middle", "bold")
    for i, row in enumerate(WIDE_ROWS):
        y = y0 + 78 + i * 86
        s.rect(x0, y, 380, 86, WHITE if i % 2 == 0 else BLUE_TINT)
        for bx in (x0 + 160, x0 + 270):
            s.line(bx, y, bx, y + 86, PANEL, 3)
        for (cx, cw, _), val in zip(cols, row):
            s.text(cx + cw / 2, y + 56, val, 30, INK, "middle")
    s.rect(x0, y0, 380, 250, "none", BLUE, 4, rx=8)


def long(s):
    s.text(633, 66, "长表", 34, CYAN_DEEP, "middle", "bold")
    x0, y0 = 472, 90
    cols = [(x0, 116, ["ID"]), (x0 + 116, 112, ["Metric"]), (x0 + 228, 94, ["Value"])]
    s.rect(x0, y0, 322, 78, CYAN_DEEP)
    for cx, cw, lines in cols:
        ybase = y0 + (46 if len(lines) == 1 else 32)
        for j, ln in enumerate(lines):
            s.text(cx + cw / 2, ybase + j * 34, ln, 30, WHITE, "middle", "bold")
    for i, (sid, metric, val) in enumerate(LONG_ROWS):
        y = y0 + 78 + i * 64
        s.rect(x0, y, 322, 64, GREEN_TINT)
        for bx in (x0 + 116, x0 + 228):
            s.line(bx, y, bx, y + 64, WHITE, 4)
        s.text(x0 + 58, y + 43, sid, 30, INK, "middle")
        if len(metric) == 1:
            s.text(x0 + 172, y + 43, metric[0], 30, INK, "middle")
        else:
            s.text(x0 + 172, y + 27, metric[0], 30, INK, "middle")
            s.text(x0 + 172, y + 57, metric[1], 30, INK, "middle")
        s.text(x0 + 275, y + 43, val, 30, INK, "middle")
    s.rect(x0, y0, 322, 270, "none", CYAN_DEEP, 4, rx=8)


def main():
    s = SVG(800, 700)
    wide(s)
    long(s)
    s.text(442, 66, "pivot_longer()", 30, GRAY, "middle", "bold")
    s.arrow(398, 230, 470, 230, CYAN, 8)

    s.rect(30, 470, 740, 64, GREEN, rx=10)
    s.text(400, 514, "行数 = 12 × 2 = 24", 36, WHITE, "middle", "bold")
    s.rect(30, 560, 740, 64, ORANGE, rx=10)
    s.text(400, 604, "2100000 / 1e6 = 2.1　换成 Mb", 34, INK, "middle", "bold")
    s.text(770, 668, "少一行都对不上", 32, RED, "end", "bold")
    s.save("06_wide_to_long.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

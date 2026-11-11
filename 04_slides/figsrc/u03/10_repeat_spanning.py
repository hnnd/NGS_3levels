#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_repeat_spanning.py — 生成 10_repeat_spanning.svg（FIG-U03-10：重复区跨越几何）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-10（P30，cols 一栏，800×700）。
教材依据：chapters/ch04/manuscript.qmd §4.4.6、§4.5.3。
基因组 U1—R(5 kb)—U2：短读 150 bp 陷在重复内部两端无锚点（组装断开）；
长读 15 kb 满足 R+a+b，两端搭入独特区锚定。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 10_repeat_spanning.py
"""
from svghelp import *  # noqa: F401,F403

U1X, RX, RWX, U2X = 70, 260, 540, 730  # U1 | R | U2 边界


def genome_bar(s, y):
    s.rect(U1X, y, RX - U1X, 46, BLUE_TINT, rx=8)
    s.rect(RX, y, RWX - RX, 46, ORANGE, rx=8)
    s.rect(RWX, y, U2X - RWX, 46, BLUE_TINT, rx=8)
    s.text((U1X + RX) / 2, y + 33, "U1", 30, BLUE, "middle", "bold")
    s.text((RX + RWX) / 2, y + 33, "R（5 kb）", 30, INK, "middle", "bold")
    s.text((RWX + U2X) / 2, y + 33, "U2", 30, BLUE, "middle", "bold")


def check_mark(s, cx, cy, color):
    s.polyline([(cx - 16, cy), (cx - 4, cy + 14), (cx + 20, cy - 16)],
               color, 8)


def main():
    s = SVG(800, 700)
    s.text(400, 50, "短读陷在重复内无锚点", 34, BLUE, "middle", "bold")
    s.text(400, 92, "长读两端锚定独特序列", 30, GRAY, "middle", "bold")

    # ── 上情景：短读 150 bp ──
    genome_bar(s, 250)
    s.rect(380, 190, 90, 26, RED, rx=8)
    s.text(425, 178, "150 bp", 28, RED, "middle", "bold")
    s.text(425, 236, "?", 44, RED, "middle", "bold")
    s.rect(120, 130, 220, 56, RED, rx=12)
    s.text(230, 170, "无法锚定", 30, WHITE, "middle", "bold")
    s.arrow(280, 190, 380, 218, RED, 5)

    # ── 下情景：长读 15 kb，满足 R+a+b ──
    genome_bar(s, 470)
    s.rect(140, 400, 520, 26, GREEN, rx=8)
    s.text(400, 388, "15 kb（设例）：长度 ≥ R + a + b", 30, GREEN, "middle",
           "bold")
    check_mark(s, 200, 544, GREEN)
    check_mark(s, 600, 544, GREEN)
    s.text(200, 584, "a（5 kb）", 28, GREEN, "middle", "bold")
    s.text(600, 584, "b（5 kb）", 28, GREEN, "middle", "bold")

    s.save("10_repeat_spanning.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

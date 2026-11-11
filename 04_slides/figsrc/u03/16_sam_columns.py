#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_sam_columns.py — 生成 16_sam_columns.svg（FIG-U03-16：SAM 11 个强制列）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-16（P43，cols 一栏，800×700）。
教材依据：chapters/ch05/manuscript.qmd §5.4.5。
11 个固定列网格卡：QNAME FLAG RNAME POS MAPQ CIGAR RNEXT PNEXT TLEN SEQ QUAL；
POS 标红「1-based 起点」，MAPQ 标红「255 = 不可用」；第 12 列起为可选 TAG。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 16_sam_columns.py
"""
from svghelp import *  # noqa: F401,F403

COLS = ["QNAME", "FLAG", "RNAME", "POS", "MAPQ", "CIGAR",
        "RNEXT", "PNEXT", "TLEN", "SEQ", "QUAL"]


def main():
    s = SVG(800, 700)
    s.text(400, 50, "比对记录十一固定列", 34, BLUE, "middle", "bold")
    s.text(400, 92, "起点一基起始不可用", 30, GRAY, "middle", "bold")

    x0, y0, cw, ch, gx, gy = 50, 130, 165, 120, 12, 20
    for i, name in enumerate(COLS):
        r, c = divmod(i, 4)
        x = x0 + c * (cw + gx)
        y = y0 + r * (ch + gy)
        hot = name in ("POS", "MAPQ")
        s.rect(x, y, cw, ch, RED_TINT if hot else BLUE_TINT,
               RED if hot else CYAN_DEEP, 5 if hot else 3, rx=12)
        s.text(x + 14, y + 42, str(i + 1), 28, GRAY, "start", "bold")
        s.text(x + cw / 2, y + 82, name, 30, INK, "middle", "bold")
        if name == "POS":
            s.text(x + cw / 2, y + 108, "1-based起点", 24, RED, "middle",
                   "bold")
        elif name == "MAPQ":
            s.text(x + cw / 2, y + 108, "255=不可用", 24, RED, "middle",
                   "bold")

    # 第 12 列起：可选 TAG
    x = x0 + 3 * (cw + gx)
    y = y0 + 2 * (ch + gy)
    s.rect(x, y, cw, ch, "#F3E8FF", PURPLE, 3, rx=12)
    s.text(x + 14, y + 42, "12+", 28, GRAY, "start", "bold")
    s.text(x + cw / 2, y + 82, "TAG", 30, INK, "middle", "bold")
    s.text(x + cw / 2, y + 108, "NM:i:3", 26, PURPLE, "middle", "bold")

    s.save("16_sam_columns.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

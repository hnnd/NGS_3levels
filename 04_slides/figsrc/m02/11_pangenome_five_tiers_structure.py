#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_pangenome_five_tiers_structure.py — 11_pangenome_five_tiers_structure.svg
（FIG-M02-15，P34，cols）：泛基因组五层结构划分切片【new-svg】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-15。
依据：教材 §11.4.4；讲义 ④ 4.6。无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 11_pangenome_five_tiers_structure.py
"""
from svghelp import (BLUE, BLUE_TINT, GRAY, INK, ORANGE, PURPLE, RED, SVG,
                     WHITE)


def main():
    s = SVG(800, 700)

    x0, w = 330, 300
    tiers = [
        (80, 150, BLUE, WHITE, "核心：全部株共有"),
        (230, 100, BLUE_TINT, INK, "软核心：容忍漏检"),
        (330, 120, ORANGE, INK, "壳：表型分化"),
        (450, 110, PURPLE, WHITE, "云与单株独有"),
    ]
    for y, h, fill, tcol, lab in tiers:
        s.rect(x0, y, w, h, fill, WHITE, 3)
        s.text(x0 - 24, y + h / 2 + 11, lab, 32, INK, "end")

    # 单株独有（红框切片，本课先判独有）
    s.rect(x0, 560, w, 44, "#FAFAF7", RED, 6)
    s.text(x0 - 24, 590, "本课 n=4 先判独有", 32, RED, "end", "bold")
    s.text(x0 + w / 2, 590, "unique", 30, RED, "middle", "bold")

    s.save("11_pangenome_five_tiers_structure.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

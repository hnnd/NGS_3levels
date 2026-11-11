#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_pangenome_five_layers.py — 生成 07_pangenome_five_layers.svg（FIG-U08-07：
泛基因组五层结构划分）

方案：reviews/course/U08_FIGP_001.md §4 FIG-U08-07（P23，cols 一栏，800×700）。
分层口径：教材 §11.4.4——核心 m=n（100%）、软核心 0.95≤m/n<1（≥95%）、
壳 0.15≤m/n<0.95（15–95%）、云 0<m/n<0.15（<15%）、单株独有 m=1。
段宽为示意（定性），不表示数量比例；中文标签分两行交错防碰撞；
红色警告条＝观测分类不等于功能证明。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 07_pangenome_five_layers.py
"""
from svghelp import *  # noqa: F401,F403

LAYERS = [
    ("核心 100%", 280, BLUE, 0),
    ("软核心 ≥95%", 150, CYAN, 1),
    ("壳 15–95%", 120, ORANGE, 0),
    ("云 <15%", 100, PURPLE, 1),
    ("单株独有", 70, GRAY, 0),
]


def main():
    s = SVG(800, 700)
    x, y, h = 40, 200, 92
    for lab, w, color, row in LAYERS:
        cx = x + w / 2
        s.rect(x, y, w, h, color, rx=8)
        ly = 356 if row == 0 else 416
        s.text(cx, ly, lab, 32, INK, "middle", "bold")
        x += w
    s.line(40, y - 18, 760, y - 18, PANEL, 3)

    # 红色警告条（唯一红）
    s.rect(120, 500, 560, 62, RED, rx=12)
    s.text(400, 543, "观测分类不等于功能证明", 36, WHITE, "middle", "bold")

    s.save("07_pangenome_five_layers.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

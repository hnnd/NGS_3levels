#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_longread_qc_paradigm.py — 生成 14_longread_qc_paradigm.svg
（FIG-U04-17：长读长质控范式转换，FT06-01 落地【范式转换】）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-17（P35，cols 一栏，viewBox 800×700）。
左栏（灰底，红叉）：短读对齐——按位置对齐数学无意义（参差读段在 POS 100 处碱基各异）；
右栏（绿框，绿勾）：长读范式——看分子整体（读长长尾分布 + 读段五零）。
依据：教材 §6.4.7 L192–204、§6.5.4；figures/ch06_figures.yml FT06-01。
图内汉字 28，红色 1 处。无网络、无随机数（图标用固定列表）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 14_longread_qc_paradigm.py
"""
from svghelp import *

BASES = [GREEN, CYAN, ORANGE, PURPLE]


def main():
    s = SVG(800, 700)

    # ---- 左栏：短读对齐无意义 ----
    s.rect(40, 60, 330, 560, PANEL, rx=18)
    s.cross(330, 104, 28)
    s.text(205, 148, "短读对齐：数学无意义", 30, INK, "middle", "bold")
    # POS 100 竖虚线
    s.line(205, 180, 205, 500, GRAY, sw=4, dash="12 10")
    s.text(205, 528, "POS 100", 30, GRAY, "middle")
    # 五条参差读段（不同长度 → POS 100 处各有不同的碱基）
    rows = [(196, 250), (246, 180), (296, 300), (346, 150), (396, 220)]
    for y, ln in rows:
        for k in range(int(ln // 12)):
            s.rect(70 + k * 12, y, 11, 26, BASES[(k * 7 + y) % 4])

    # ---- 右栏：长读范式 ----
    s.rect(430, 60, 330, 560, WHITE, stroke=GREEN, sw=6, rx=18)
    s.check(720, 104, 28)
    s.text(595, 148, "长读范式：看分子整体", 30, INK, "middle", "bold")
    # 长尾分布：三条长读段 + 一条短读段
    reads = [(268, 260), (330, 240), (392, 205), (454, 70)]
    for y, ln in reads:
        for k in range(int(ln // 12)):
            s.rect(462 + k * 12, y, 11, 26, BASES[(k * 5 + y) % 4])
    s.text(595, 512, "读长长尾分布", 30, INK, "middle", "bold")
    s.rect(500, 536, 190, 62, GREEN, rx=14)
    s.text(595, 578, "读段五零", 30, WHITE, "middle", "bold")

    s.save("14_longread_qc_paradigm.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

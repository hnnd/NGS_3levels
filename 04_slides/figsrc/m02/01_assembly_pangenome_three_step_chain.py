#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_assembly_pangenome_three_step_chain.py — 01_assembly_pangenome_three_step_chain.svg
（FIG-M02-01，P07，cols）：组装与泛基因组三步认知链与不可逆依赖【new-svg】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-01。
依据：教材 §11.1；讲义 ③ 3.1。无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 01_assembly_pangenome_three_step_chain.py
"""
from svghelp import (BLUE, CYAN, GRAY, INK, RED, SVG, WHITE)


def main():
    s = SVG(800, 700)

    steps = ["① 从头组装拼序列", "② 统一注释建坐标", "③ 比较矩阵定核心"]
    y = 86
    for i, lab in enumerate(steps):
        s.rect(90, y, 470, 108, BLUE, rx=18)
        s.text(325, y + 68, lab, 38, WHITE, "middle", "bold")
        if i == 0:
            for j in range(5):  # contig 小条
                s.rect(120 + j * 34, y + 78, 26, 12, CYAN)
        elif i == 1:
            for j in range(5):  # 注释坐标刻度
                s.line(128 + j * 30, y + 84, 128 + j * 30, y + 96, CYAN, 4)
        else:
            for j in range(5):  # 0/1 矩阵格
                for k in range(2):
                    fill = CYAN if (j + k) % 3 else WHITE
                    s.rect(122 + j * 20, y + 78 + k * 12, 14, 9, fill)
        if i < 2:
            s.arrow(325, y + 112, 325, y + 142, CYAN, 8)
        y += 156

    # 右侧红色不可逆警示弧线（上游误差 → 下游放大）
    s.path("M 620 520 C 790 460, 790 220, 612 168", RED, 7, dash="18 12")
    s.polygon([(612, 168), (640, 164), (628, 190)], RED)
    s.text(688, 300, "上游误差", 32, RED, "middle", "bold")
    s.text(688, 348, "下游放大", 32, RED, "middle", "bold")

    s.save("01_assembly_pangenome_three_step_chain.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

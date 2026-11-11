#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_mashtree_vs_gtotree_iqtree.py — 生成 15_mashtree_vs_gtotree_iqtree.svg
（FIG-U08-15：Mashtree 距离树 vs GToTree+IQ-TREE 74 基因超矩阵 ML 树）

方案：reviews/course/U08_FIGP_001.md §4 FIG-U08-15（P42，cols 一栏，800×700）。
数据来源：GToTree Bacteria HMM 默认 74 个单拷贝保守基因（ALN §0.6 实查）；
IQ-TREE -m LG+F+I+G4（手册 L691，W16 已纠正带 F）；Mashtree 全基因组
MinHash 距离 + NJ（教材 §11.4.3、讲义 ④ 4.1.5）。
上下对照：上橙（轻量快速）vs 下深蓝（严谨主体，红＝双支持值检验）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 15_mashtree_vs_gtotree_iqtree.py
"""
from svghelp import *  # noqa: F401,F403

DEEP_ORANGE = "#D0763B"


def tree_icon(s, x, y, color):
    """三叶矩形进化树示意；(x, y) 为树根中心。"""
    s.line(x, y, x, y - 46, color, 5)
    s.line(x, y - 46, x - 52, y - 46, color, 5)
    s.line(x, y - 46, x + 52, y - 30, color, 5)
    s.line(x - 52, y - 46, x - 52, y - 76, color, 5)
    s.line(x + 52, y - 30, x + 52, y - 76, color, 5)
    for cx, cy in ((x, y), (x - 52, y - 46), (x + 52, y - 30)):
        s.circle(cx, cy, 9, WHITE, color, 4)
    for cx in (x - 52, x + 52):
        s.circle(cx, y - 82, 9, color)
    s.circle(x, y - 82, 9, color)


def main():
    s = SVG(800, 700)

    # —— 上面板：Mashtree（橙，轻量快速）——
    s.rect(40, 56, 20, 20, ORANGE, rx=4)
    s.text(72, 76, "Mashtree：全基因组快速树", 34, INK, "start", "bold")
    for r in range(5):                      # MinHash 距离矩阵
        for c in range(5):
            shade = ORANGE if r == c else \
                PANEL if (r + c) % 2 else "#F6E3D8"
            s.rect(60 + c * 30, 130 + r * 30, 24, 24, shade, rx=3)
    s.text(122, 300, "distance", 30, GRAY, "middle")
    s.arrow(230, 200, 300, 200, GRAY, 6)
    s.rect(310, 160, 150, 76, ORANGE, rx=12)
    s.text(385, 194, "MinHash", 30, "#33332E", "middle", "bold")
    s.text(385, 224, "+ NJ", 30, "#33332E", "middle", "bold")
    s.arrow(470, 200, 540, 200, GRAY, 6)
    tree_icon(s, 620, 268, DEEP_ORANGE)

    # 分隔线
    s.line(40, 350, 760, 350, PANEL, 4)

    # —— 下面板：GToTree + IQ-TREE（深蓝，严谨主体）——
    s.rect(40, 386, 20, 20, BLUE, rx=4)
    s.text(72, 406, "GToTree+IQ-TREE：74 基因 ML 树", 34, INK, "start",
           "bold")
    s.rect(60, 446, 150, 64, GREEN, rx=12)
    s.text(135, 488, "74 SCG", 32, WHITE, "middle", "bold")
    s.arrow(220, 478, 290, 478, GRAY, 6)
    for i, w in enumerate((200, 168, 186, 150)):     # 超矩阵比对
        s.rect(300, 442 + i * 32, w, 22, BLUE, rx=4)
    s.arrow(530, 478, 590, 478, GRAY, 6)
    tree_icon(s, 660, 556, BLUE)
    # 红框标内部节点 + 红色标签（同一红区：框与标签横幅上下相接）
    s.rect(586, 492, 176, 84, "none", RED, 4, rx=8)
    s.rect(539, 584, 250, 56, RED, rx=10)
    s.text(664, 622, "双支持值检验分支", 30, WHITE, "middle", "bold")

    s.save("15_mashtree_vs_gtotree_iqtree.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

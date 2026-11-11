#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_prodigal_features.py — 生成 06_prodigal_features.svg（FIG-U07-06：Prodigal 三条统计线索）

方案：reviews/course/U07_FIGP_001.md §4.2 FIG-U07-06（P19，cols 一栏，viewBox 800×700）。
数据：无量字数字。位置特异性 GC 偏好、RBS/SD 基序与间距、全基因组动态规划，
弃用单一长度阈值（教材 §9.4.2 L124–135）。面板英文标注不占汉字预算。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 06_prodigal_features.py
"""
import math

from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    panels = [(30, 250), (270, 510), (550, 770)]
    for x0, x1 in panels:
        s.rect(x0, 60, x1 - x0, 470, WHITE, PANEL, 3, rx=16)

    # 面板 1：三位点 GC 偏好波形（青蓝折线 + 周期 3 圆点）
    pts = []
    for i in range(0, 37):
        x = 55 + i * 5.2
        y = 300 - 120 * math.sin(i * math.pi / 3.0) * math.exp(-i / 60.0)
        pts.append((x, y))
    s.curve(pts, CYAN_DEEP, 6)
    for i in range(1, 37, 3):
        x = 55 + i * 5.2
        y = 300 - 120 * math.sin(i * math.pi / 3.0) * math.exp(-i / 60.0)
        s.circle(x, y, 8, CYAN)
    s.line(55, 300, 235, 300, PANEL, 3)

    # 面板 2：起始密码子与上游 RBS（AGGAGG）间距尺（橙色）
    s.line(285, 260, 495, 260, CYAN, 8, cap="round")
    s.rect(285, 175, 122, 46, ORANGE, rx=8)
    s.text(346, 208, "AGGAGG", 30, INK, "middle", "bold")
    s.rect(448, 175, 52, 46, GREEN, rx=8)
    s.text(474, 208, "ATG", 30, WHITE, "middle", "bold")
    s.line(414, 198, 442, 198, ORANGE, 5)
    s.line(414, 186, 414, 210, ORANGE, 5)
    s.line(442, 186, 442, 210, ORANGE, 5)
    s.text(432, 152, "5–10 bp", 30, GRAY, "middle")
    for yy, codon in ((350, "GTG"), (430, "TTG")):
        s.rect(295, yy, 90, 44, WHITE, GRAY, 4, rx=8)
        s.text(340, yy + 31, codon, 30, GRAY, "middle")

    # 面板 3：多候选读框动态规划最优路径（深蓝节点 + 绿路径）
    nodes = {}
    for c in range(4):
        for r in range(3):
            x = 590 + c * 55
            y = 140 + r * 110
            nodes[(c, r)] = (x, y)
    for c in range(3):
        for r1 in range(3):
            for r2 in range(3):
                x1, y1 = nodes[(c, r1)]
                x2, y2 = nodes[(c + 1, r2)]
                s.line(x1, y1, x2, y2, "#C7D0E4", 3)
    for (x, y) in nodes.values():
        s.circle(x, y, 15, BLUE)
    best = [(0, 1), (1, 1), (2, 0), (3, 0)]
    for (a, b) in zip(best, best[1:]):
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        s.arrow(x1, y1, x2, y2, GREEN, 6, head=14)
    for k in (best[0], best[-1]):
        x, y = nodes[k]
        s.circle(x, y, 15, GREEN)

    # 面板标题（方案逐字）
    s.text(140, 592, "位置偏好", 32, BLUE, "middle", "bold")
    s.text(390, 592, "基序与间距", 32, BLUE, "middle", "bold")
    s.text(660, 592, "全基因组最优", 32, BLUE, "middle", "bold")

    # 底部红色结论条（唯一红色）
    s.rect(270, 636, 260, 52, RED, rx=12)
    s.text(400, 672, "不用单一长度", 32, WHITE, "middle", "bold")

    s.save("06_prodigal_features.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

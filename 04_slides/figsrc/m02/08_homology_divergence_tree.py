#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_homology_divergence_tree.py — 08_homology_divergence_tree.svg
（FIG-M02-12，P30，cols）：同源概念分化树（物种分化 vs 复制 vs 水平转移）【new-svg】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-12。
依据：教材 §11.4.1；讲义 ④ 4.5。无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 08_homology_divergence_tree.py
"""
from svghelp import (BLUE, GRAY, GREEN, INK, ORANGE, PURPLE, RED, SVG, WHITE)


def main():
    s = SVG(800, 700)

    # 祖先基因（根）
    s.circle(400, 84, 14, BLUE)
    s.text(430, 96, "anc", 30, GRAY, "start", "bold")

    # 节点 ① 物种形成（深蓝圆点）→ 物种 A / 物种 B
    s.line(400, 98, 400, 190, BLUE, 6)
    s.circle(400, 202, 14, BLUE)
    s.text(400, 211, "①", 30, WHITE, "middle", "bold")
    s.line(388, 210, 286, 322, BLUE, 6)   # → A 支（经节点 ②）
    s.line(412, 210, 624, 468, BLUE, 6)   # → B 叶

    # 节点 ② 基因复制（橙方块，A 支上）→ A1 / A2
    s.rect(272, 322, 28, 28, ORANGE, rx=4)
    s.text(286, 344, "②", 30, WHITE, "middle", "bold")
    s.line(280, 350, 116, 468, ORANGE, 6)   # → A1
    s.line(292, 350, 258, 468, ORANGE, 6)   # → A2

    # 叶：基因节点
    for cx, cy, lab in ((110, 492, "A1"), (262, 492, "A2"), (630, 492, "B")):
        s.circle(cx, cy, 22, BLUE)
        s.text(cx, cy + 11, lab, 30, WHITE, "middle", "bold")
    s.text(150, 430, "species A", 30, GRAY, "middle")
    s.text(600, 430, "species B", 30, GRAY, "middle")

    # 事件标注
    s.text(436, 196, "物种分化：直系同源", 32, BLUE, "start", "bold")
    s.text(186, 566, "基因复制：旁系同源", 32, ORANGE, "middle", "bold")

    # 水平转移（紫色横穿虚线箭头：B → A2）
    s.path("M 608 466 C 480 524, 380 524, 292 502", PURPLE, 6, dash="16 12")
    s.polygon([(292, 502), (318, 490), (318, 516)], PURPLE)
    s.text(520, 560, "水平转移：异系同源", 32, PURPLE, "middle", "bold")

    # 底部红框总结
    s.rect(240, 614, 320, 66, RED, rx=14)
    s.text(400, 659, "看分开时的事件", 34, WHITE, "middle", "bold")

    s.save("08_homology_divergence_tree.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

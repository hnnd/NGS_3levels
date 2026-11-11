#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_vcf_format_layers.py — 生成 19_vcf_format_layers.svg
（FIG-M03-22：GT:AD:DP:GQ:PL 五联字段推断与观测分层）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-22（P44，cols 一栏，800×700）。
图内中文按方案（观测层 等位深度 似然层 归一似然 决策层 基因型质量）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文；字段名
（AD/DP/PL/GT/GQ/FORMAT）保留英文，字数不再按 ≤30 字核验。依据：
教材 §10.4.1（L87–106）。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 46, "FORMAT 分层", 36, INK, "middle", "bold")

    layers = [
        (420, "观测层", "AD / DP", "等位深度", BLUE, BLUE_TINT),
        (286, "似然层", "PL", "归一似然", CYAN_DEEP, None),
        (152, "决策层", "GT / GQ", "基因型质量", GREEN, GREEN_TINT),
    ]
    for y, t1, t2, t3, col, fill in layers:
        s.rect(40, y, 520, 116, WHITE, col, 5, rx=14)
        s.text(125, y + 50, t1, 32, col, "middle", "bold")
        s.rect(220, y + 22, 170, 50, fill or WHITE, col, 3, rx=8)
        s.text(305, y + 58, t2, 30, INK, "middle", "bold")
        s.text(475, y + 58, t3, 30, GRAY, "middle")

    s.arrow(590, 460, 590, 340, GRAY, 6)
    s.arrow(590, 326, 590, 206, GRAY, 6)
    s.text(578, 336, "推断", 30, GRAY, "middle", rotate=-90)

    # 诚实度标尺
    s.rect(600, 150, 135, 386, WHITE, PANEL, 3, rx=14)
    s.text(667, 190, "诚实度", 30, INK, "middle", "bold")
    s.darrow(625, 220, 625, 500, BLUE, 5, head=14)
    s.text(685, 275, "AD DP", 30, BLUE, "middle")
    s.text(685, 385, "PL", 30, CYAN_DEEP, "middle")
    s.text(685, 495, "GT GQ", 30, GREEN, "middle")

    # 回溯警示
    s.path("M 300 152 C 300 110 200 120 200 548", RED, 5, dash="14 10")
    s.arrow(200, 538, 200, 558, RED, 6)
    s.rect(60, 560, 500, 56, RED_TINT, RED, 4, rx=10)
    s.text(310, 598, "GT 下结论前必须回溯 AD", 32, RED, "middle", "bold")

    s.text(400, 662, "观测 → 似然 → 决策", 30, GRAY, "middle")
    s.save("19_vcf_format_layers.svg")


if __name__ == "__main__":
    main()

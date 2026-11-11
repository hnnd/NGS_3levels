#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_haplotype_caller_steps.py — 生成 09_haplotype_caller_steps.svg
（FIG-M03-12：HaplotypeCaller 四层流水线与局部重组装）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-12（P25，cols 一栏，800×700）。
图内中文按方案（活跃区域 局部重组装 候选单倍型 似然矩阵 贝叶斯定型）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文，工具名/字段名/
命令/参数保留英文，字数不再按 ≤30 字核验。依据：教材 §10.4.4（L140–155）。
无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 48, "HaplotypeCaller 四层", 36, INK, "middle", "bold")

    cards = [
        (80, "1", "活跃区域", "ActiveRegion", BLUE),
        (224, "2", "局部重组装", "de Bruijn 组装", CYAN_DEEP),
        (368, "3", "似然矩阵", "PairHMM", PURPLE),
        (512, "4", "贝叶斯定型", "MAP → GT/GQ", GREEN),
    ]
    for y, num, title, en, col in cards:
        s.rect(40, y, 720, 118, WHITE, col, 4, rx=14)
        s.circle(92, y + 40, 27, col)
        s.text(92, y + 50, num, 30, WHITE, "middle", "bold")
        s.text(210, y + 46, title, 32, col, "middle", "bold")
        s.text(210, y + 86, en, 30, GRAY, "middle")

    # ① 活跃区域：错配密集
    for k in range(4):
        s.rect(340 + k * 50, 106, 44, 22, CYAN, None, rx=3)
    s.line(366, 96, 366, 140, RED, 5)
    s.line(416, 96, 416, 140, RED, 5)
    s.text(640, 124, "错配堆积", 30, GRAY, "middle")
    s.text(560, 172, "消除 InDel 旁 SNP", 30, RED, "middle")

    # ② de Bruijn 气泡
    s.polyline([(350, 262), (420, 262), (480, 240)], BLUE, 6)
    s.polyline([(350, 292), (420, 292), (480, 314)], BLUE, 6)
    s.polyline([(480, 240), (540, 240), (600, 262)], CYAN, 6)
    s.polyline([(480, 314), (540, 314), (600, 262)], ORANGE, 6)
    s.text(665, 258, "气泡", 30, GRAY, "middle")
    s.text(660, 326, "候选单倍型", 30, CYAN_DEEP, "middle", "bold")

    # ③ 似然矩阵
    for r in range(3):
        for c in range(4):
            x = 360 + c * 50
            y = 398 + r * 30
            shade = [BLUE_TINT, CYAN, PURPLE_TINT, ORANGE_TINT][c]
            s.rect(x, y, 44, 24, shade, PANEL, 2)
    s.text(600, 424, "读段 × 单倍型", 30, GRAY, "middle")
    s.text(600, 462, "P(r|h)", 30, GRAY, "middle")

    # ④ 贝叶斯
    s.text(380, 574, "似然 × 先验", 30, PURPLE, "middle", "bold")
    s.arrow(455, 566, 505, 566, GRAY, 6)
    s.text(555, 574, "MAP", 30, INK, "middle", "bold")
    s.rect(620, 546, 90, 48, GREEN_TINT, GREEN, 4, rx=10)
    s.text(665, 579, "GT", 30, GREEN, "middle", "bold")

    for i in range(3):
        s.arrow(400, 198 + i * 144, 400, 222 + i * 144, GRAY, 6)
    s.save("09_haplotype_caller_steps.svg")


if __name__ == "__main__":
    main()

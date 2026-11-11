#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_duplication_double_edge.py — 生成 17_duplication_double_edge.svg
（FIG-M03-20：重复率双刃剑与独立分子库复杂度）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-20（P41，cols 一栏，800×700）。
图内中文按方案（独立分子库 测序过深 重复率飙升 有效深度折减 假变异）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文，工具名/字段名/
命令/参数保留英文，字数不再按 ≤30 字核验。依据：教材 §10.4.2（L118–121）、
§10.5.1。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 46, "重复率双刃剑", 36, INK, "middle", "bold")

    # 中央
    s.rect(280, 300, 240, 110, BLUE_TINT, BLUE, 5, rx=16)
    s.text(400, 348, "独立分子库", 34, BLUE, "middle", "bold")
    s.text(400, 386, "复杂度", 30, GRAY, "middle")
    for i, col in enumerate([CYAN, CYAN, ORANGE, CYAN, PURPLE]):
        s.circle(330 + i * 36, 318, 11, col)

    # 左刃：PCR 过度
    s.rect(40, 76, 310, 190, WHITE, RED, 4, rx=14)
    s.text(195, 116, "PCR 过度扩增", 32, RED, "middle", "bold")
    s.text(195, 154, "起始量低", 30, GRAY, "middle")
    s.circle(78, 218, 14, RED)
    for dx, dy in ((32, -16), (54, 6), (34, 26), (68, -22), (72, 20)):
        s.circle(78 + dx, 218 + dy, 12, RED_TINT, RED, 3)
    s.text(268, 208, "重复率飙升", 30, RED, "middle", "bold")
    s.text(268, 246, "错误 ×8", 30, GRAY, "middle")
    s.arrow(195, 266, 320, 300, RED, 6)
    s.rect(50, 300, 220, 60, RED_TINT, RED, 4, rx=10)
    s.text(160, 340, "不去重 → 假变异", 30, RED, "middle", "bold")

    # 右刃：测序过深
    s.rect(450, 76, 310, 190, WHITE, ORANGE, 4, rx=14)
    s.text(605, 116, "测序过深", 32, ORANGE, "middle", "bold")
    s.text(605, 154, "文库极复杂", 30, GRAY, "middle")
    for r in range(3):
        for c in range(5):
            s.rect(480 + c * 32, 196 + r * 26, 26, 18,
                   CYAN if (r + c) % 4 else ORANGE, None, rx=3)
    s.text(697, 208, "重复率 ↑", 30, ORANGE, "middle", "bold")
    s.text(690, 246, "坐标碰撞", 30, GRAY, "middle")
    s.arrow(605, 266, 480, 300, ORANGE, 6)
    s.rect(530, 300, 220, 60, ORANGE_TINT, ORANGE, 4, rx=10)
    s.text(640, 328, "过度去重 →", 30, ORANGE, "middle", "bold")
    s.text(640, 356, "有效深度折减", 30, ORANGE, "middle", "bold")

    # 底部对照轴
    s.line(120, 440, 680, 440, PANEL, 6)
    s.darrow(150, 440, 650, 440, GRAY, 5, head=14)
    s.text(400, 484, "去重不足 ↔ 去重过度", 30, GRAY, "middle")
    s.text(170, 528, "假变异", 32, RED, "middle", "bold")
    s.text(630, 528, "功效损失", 32, ORANGE, "middle", "bold")

    s.rect(40, 576, 720, 80, BLUE_TINT, BLUE, 4, rx=14)
    s.text(400, 612, "重复率须结合文库、基因组大小、深度读", 30,
           BLUE, "middle", "bold")
    s.text(400, 644, "单一数字不构成诊断", 30, GRAY,
           "middle")
    s.save("17_duplication_double_edge.svg")


if __name__ == "__main__":
    main()

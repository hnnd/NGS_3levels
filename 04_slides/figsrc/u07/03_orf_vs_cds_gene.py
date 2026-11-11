#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""03_orf_vs_cds_gene.py — 生成 03_orf_vs_cds_gene.svg（FIG-U07-03：ORF / 读框 / CDS / 基因辨析）

方案：reviews/course/U07_FIGP_001.md §4.2 FIG-U07-03（P15，cols 一栏，viewBox 800×700）。
数据：无量字数字。ORF 仅是无终止片段、CDS 是结构注释预测、基因含调控语境
（教材 §9.4.1 L80–98）。基因盒用英文标注（汉字预算 29 已满）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 03_orf_vs_cds_gene.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 顶层：长双链 DNA（灰蓝）+ 三框刻度（六种翻译轨道的提示）
    s.text(400, 62, "读框：六种翻译轨道之一", 32, "#5E78A8", "middle", "bold")
    s.line(60, 105, 740, 105, PURPLE, 5)
    s.line(60, 133, 740, 133, PURPLE, 5)
    for row in range(3):
        y = 158 + row * 16
        for x in range(80 + row * 18, 740, 54):
            s.line(x, y, x, y + 9, CYAN, 3)

    # 中层：连续三联体 ORF（青蓝高亮），末端一个橙色终止密码子
    codons = [("ATG", GREEN), ("GCT", CYAN), ("AAT", CYAN), ("GCT", CYAN),
              ("TCT", CYAN), ("GGA", CYAN), ("CTA", CYAN)]
    cx = 120
    for aa, color in codons:
        s.rect(cx, 232, 60, 56, color, rx=8)
        s.text(cx + 30, 270, aa, 30, WHITE, "middle", "bold")
        cx += 60
    s.rect(cx + 6, 232, 60, 56, ORANGE, rx=8)
    s.text(cx + 36, 270, "TAA", 30, INK, "middle", "bold")
    s.text((120 + cx) / 2, 345, "ORF：无终止三联体片段", 32, CYAN_DEEP,
           "middle", "bold")

    # 底层左分支：CDS（绿框）
    s.rect(60, 420, 300, 130, WHITE, GREEN, 6, rx=14)
    s.text(210, 478, "CDS", 36, GREEN, "middle", "bold")
    s.text(210, 522, "预测出的编码区", 30, INK, "middle")

    # 底层右分支：完整基因（深蓝框，含启动子 / UTR 与调控区，英文标注）
    s.rect(440, 420, 300, 140, WHITE, BLUE, 6, rx=14)
    s.text(590, 464, "gene", 34, BLUE, "middle", "bold")
    s.arrow(458, 508, 504, 508, ORANGE, 6)
    s.text(481, 490, "pro", 30, GRAY, "middle")
    s.rect(516, 488, 38, 30, PANEL, rx=6)
    s.text(535, 545, "UTR", 30, GRAY, "middle")
    s.rect(576, 488, 54, 30, CYAN, rx=6)
    s.text(603, 545, "CDS", 30, CYAN_DEEP, "middle")
    s.rect(652, 488, 38, 30, PANEL, rx=6)
    s.text(671, 545, "UTR", 30, GRAY, "middle")

    # 底部中央红色警示（唯一红色：ORF 不是基因）
    s.rect(250, 610, 300, 56, RED, rx=12)
    s.text(400, 648, "ORF 不是基因", 32, WHITE, "middle", "bold")

    s.save("03_orf_vs_cds_gene.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

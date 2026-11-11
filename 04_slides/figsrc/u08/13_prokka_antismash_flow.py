#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_prokka_antismash_flow.py — 生成 13_prokka_antismash_flow.svg（FIG-U08-13：
Prokka 快速注释流水线与 antiSMASH BGC 预测）

方案：reviews/course/U08_FIGP_001.md §4 FIG-U08-13（P40，cols 一栏，800×700）。
流程契约：Prokka＝Prodigal ORF 预测 + BLAST/HMM 蛋白匹配 → 含 ##FASTA 的
.gff/.faa（深蓝，2×2 蛇形网格防文字溢出）；antiSMASH＝profile HMM 扫描识别
核心生物合成酶与候选基因簇（青蓝）；红 1 处＝预测簇不等于合成
（教材 §9.4.3、§9.4.5、§9.5.4）。零数字（ALN W8 规避）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 13_prokka_antismash_flow.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 上管道：Prokka 结构注释（深蓝，2×2 蛇形）
    s.text(50, 84, "Prokka：蛋白预测与 GFF", 34, BLUE, "start", "bold")
    bw, bh = 280, 74
    s.rect(60, 130, bw, bh, WHITE, BLUE, 4, rx=12)
    s.text(200, 176, "genome.fasta", 30, INK, "middle", "bold")
    s.arrow(348, 167, 408, 167, BLUE, 6, head=14)
    s.rect(412, 130, bw, bh, WHITE, BLUE, 4, rx=12)
    s.text(552, 176, "Prodigal ORF", 30, INK, "middle", "bold")
    s.arrow(552, 212, 552, 226, BLUE, 6, head=14)
    s.rect(412, 230, bw, bh, WHITE, BLUE, 4, rx=12)
    s.text(552, 276, "BLAST / HMM", 30, INK, "middle", "bold")
    s.arrow(408, 267, 348, 267, BLUE, 6, head=14)
    s.rect(60, 230, bw, bh, BLUE, None, 4, rx=12)
    s.text(200, 276, ".gff + .faa", 30, WHITE, "middle", "bold")

    # 下管道：antiSMASH 次级代谢（青蓝）
    s.text(50, 386, "antiSMASH：次级代谢簇", 34, CYAN_DEEP, "start", "bold")
    y2 = 426
    boxes2 = [("profile HMM", WHITE, CYAN_DEEP, INK),
              ("core enzymes", WHITE, CYAN_DEEP, INK),
              ("candidate BGC", CYAN_DEEP, CYAN_DEEP, WHITE)]
    for i, (lab, fill, stroke, tcolor) in enumerate(boxes2):
        x = 40 + i * 252
        s.rect(x, y2, 220, bh, fill, stroke, 4, rx=12)
        s.text(x + 110, y2 + 47, lab, 30, tcolor, "middle", "bold")
        if i < 2:
            s.arrow(x + 224, y2 + bh / 2, x + 248, y2 + bh / 2, CYAN_DEEP, 6,
                    head=14)

    # 红色警示角标（唯一红）
    s.rect(430, 570, 330, 62, RED, rx=12)
    s.text(595, 612, "预测簇不等于合成", 34, WHITE, "middle", "bold")

    s.save("13_prokka_antismash_flow.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

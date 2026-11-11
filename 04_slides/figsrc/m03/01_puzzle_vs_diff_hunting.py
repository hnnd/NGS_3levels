#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_puzzle_vs_diff_hunting.py — 生成 01_puzzle_vs_diff_hunting.svg
（FIG-M03-01：从头组装拼图 vs 重测序找茬、极端不平衡分类）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-01（P10，cols 一栏，800×700）。
图内中文按方案（从头组装 拼图 无坐标 变异检测 找茬 极不平衡 变异仅千分之一）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文（de novo 作术语保留），
工具名/字段名/命令/参数保留英文，字数不再按 ≤30 字核验。依据：教材 §10.1
（L10–24）。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403

BASES = {"A": GREEN, "C": CYAN, "G": ORANGE, "T": PURPLE}


def read_bar(s, x, y, w, seq, h=30, gap=3):
    n = len(seq)
    cw = (w - gap * (n - 1)) / n
    for i, b in enumerate(seq):
        s.rect(x + i * (cw + gap), y, cw, h, BASES[b])


def main():
    s = SVG(800, 700)
    s.text(400, 50, "拼图与找茬", 38, INK, "middle", "bold")

    # 左：从头组装——读段散落、无坐标基准
    s.rect(40, 76, 340, 440, WHITE, PANEL, 3, rx=14)
    frag = [
        ("ACGTTGCA", 70, 150, 200), ("TTGCACGT", 210, 195, 190),
        ("GCAACGTT", 80, 250, 180), ("CGTTGCAA", 240, 292, 170),
        ("AACGTTGC", 120, 345, 200), ("GTGCAACT", 230, 390, 180),
        ("ACGTTGCA", 100, 438, 190),
    ]
    for seq, x, y, w in frag:
        read_bar(s, x, y, w, seq, h=28)
    s.text(210, 120, "de novo", 30, GRAY, "middle", "bold")
    s.text(210, 496, "从头组装  无坐标", 30, BLUE, "middle", "bold")

    # 右：重测序找茬——完成图提供全局坐标，读段回贴
    s.rect(420, 76, 340, 440, WHITE, PANEL, 3, rx=14)
    s.text(590, 120, "GCA_024981335", 30, BLUE, "middle", "bold")
    s.line(450, 150, 730, 150, BLUE, 6)
    for i in range(8):
        x = 450 + i * 38
        s.line(x, 142, x, 158, BLUE, 4)
    reads = [
        ("ACGTTGCA", 0), ("ACGTTGCA", 1), ("ACATTGCA", 2), ("ACGTTGCA", 3),
        ("ACGTTGCA", 4),
    ]
    vx = 450 + 2 * 38 + 18
    for k, (seq, off) in enumerate(reads):
        y = 180 + k * 48
        read_bar(s, 450 + off * 7, y, 210, seq, h=28)
        if k == 2:
            s.line(vx - 10, y - 6, vx + 10, y + 34, RED, 6)
            s.line(vx + 10, y - 6, vx - 10, y + 34, RED, 6)
    s.circle(585, 302, 70, "none", BLUE, 8)
    s.line(640, 357, 684, 401, BLUE, 12)
    s.text(585, 296, "SNP", 32, RED, "middle", "bold")
    s.text(585, 334, "1/4770", 30, GRAY, "middle")
    s.text(590, 500, "变异检测  找茬", 30, BLUE, "middle", "bold")

    # 底部结论条
    s.rect(40, 552, 720, 64, RED_TINT, RED, 4, rx=12)
    s.text(400, 596, "极不平衡  变异仅千分之一", 34, RED, "middle", "bold")
    s.text(400, 664, "4.77 Mb 参考基因组：约千分之一真差异", 30, GRAY,
           "middle")
    s.save("01_puzzle_vs_diff_hunting.svg")


if __name__ == "__main__":
    main()

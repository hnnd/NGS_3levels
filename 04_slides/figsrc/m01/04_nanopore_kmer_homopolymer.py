#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_nanopore_kmer_homopolymer.py — 生成 04_nanopore_kmer_homopolymer.svg
（FIG-M01-06：Nanopore 5–6 nt 感应区与同聚物平直电流）

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-06（P18，cols 一栏，800×700）。
依据：教材 §4.4.4 L127–138（感应窗口约 5–6 nt，同聚物区电流缺台阶跳变）；
讲义 ④4.1。无数字、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 04_nanopore_kmer_homopolymer.py
"""
from svghelp import *  # noqa: F401,F403

# 碱基四色编码（spec §2）：A 绿 / C 青 / G 橙 / T 紫
BASE_COLORS = [GREEN, CYAN, ORANGE, PURPLE]


def main():
    s = SVG(800, 700)

    # 上部：跨膜纳米孔纵截面 + 5–6 nt 感应窗口
    s.rect(40, 60, 720, 320, WHITE, PANEL, 3, rx=14)
    s.rect(70, 140, 660, 70, BLUE)
    s.rect(70, 310, 660, 70, BLUE)
    s.rect(360, 140, 80, 240, WHITE, BLUE, 4)  # 孔道
    s.line(400, 100, 400, 390, CYAN, 9)        # 单链 DNA 穿孔
    for i, y in enumerate(range(112, 376, 33)):
        s.rect(392, y, 16, 16, BASE_COLORS[i % 4], rx=3)
    s.rect(375, 232, 50, 52, "none", CYAN_DEEP, 6, rx=8)
    s.line(425, 258, 500, 258, CYAN_DEEP, 4)
    s.text(510, 268, "5–6 nt 感应窗口", 32, CYAN_DEEP, "start", "bold")

    # 下部左：多样序列 → 丰富阶梯电流
    s.rect(40, 400, 350, 240, WHITE, PANEL, 3, rx=14)
    pattern = [2, 0, 3, 1, 2, 3, 0, 1, 2, 1, 3, 2, 0, 2, 1, 3]
    pts = []
    for i, lv in enumerate(pattern):
        x0 = 66 + i * 19
        y = 560 - lv * 34
        pts.append((x0, y))
        pts.append((x0 + 19, y))
    s.polyline(pts, CYAN_DEEP, 6)
    s.text(215, 622, "序列起伏：丰富阶梯", 30, INK, "middle", "bold")

    # 下部右：同聚物区 → 平直电流（红色结论，全图唯一红色）
    s.rect(410, 400, 350, 240, WHITE, PANEL, 3, rx=14)
    s.line(436, 566, 736, 566, ORANGE, 7)
    s.text(586, 622, "同聚物：电流平直", 30, INK, "middle", "bold")
    s.text(586, 480, "易致 InDel", 34, RED, "middle", "bold")

    s.save("04_nanopore_kmer_homopolymer.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

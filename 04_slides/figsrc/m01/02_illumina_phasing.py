#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_illumina_phasing.py — 生成 02_illumina_phasing.svg
（FIG-M01-04：Illumina 簇内失同步累积与 3′ 质量衰减）

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-04（P16，cols 一栏，800×700）。
依据：教材 §4.4.2 L84–92（簇内去同步化物理机制）；讲义 ④4.1。无数字、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 02_illumina_phasing.py
"""
from svghelp import *  # noqa: F401,F403


def cluster(s, y0, rows, cols, special):
    """rows×cols 圆点簇；special: {(r,c): color}"""
    for r in range(rows):
        for c in range(cols):
            cx = 112 + c * 50
            cy = y0 + r * 43
            color = special.get((r, c), CYAN)
            s.circle(cx, cy, 17, color)


def main():
    s = SVG(800, 700)
    s.text(400, 52, "簇内分子合成失同步", 36, INK, "middle", "bold")

    # 上部：第 1 轮，100% 同步
    s.rect(60, 76, 680, 166, WHITE, PANEL, 3, rx=14)
    s.text(84, 116, "R1", 30, GRAY, "start", "bold")
    cluster(s, 146, 3, 5, {})
    s.text(480, 170, "正常同步", 32, CYAN_DEEP, "start", "bold")

    # 中部：第 100 轮，掉队/抢跑出现
    s.rect(60, 258, 680, 166, WHITE, PANEL, 3, rx=14)
    s.text(84, 298, "R100", 30, GRAY, "start", "bold")
    special = {(1, 2): ORANGE, (0, 4): ORANGE, (2, 1): PURPLE}
    cluster(s, 328, 3, 5, special)
    s.circle(498, 322, 11, ORANGE)
    s.text(520, 332, "掉队 −1", 32, INK, "start", "bold")
    s.circle(498, 380, 11, PURPLE)
    s.text(520, 390, "抢跑 +1", 32, INK, "start", "bold")

    # 下部左：荧光信号混合（青蓝为主、橙/紫少量）
    s.rect(60, 440, 340, 216, WHITE, PANEL, 3, rx=14)
    s.text(84, 484, "信号混合", 32, INK, "start", "bold")
    s.rect(84, 508, 200, 52, CYAN)
    s.rect(284, 508, 38, 52, ORANGE)
    s.rect(322, 508, 24, 52, PURPLE)

    # 下部右：3′ 端质量衰减曲线（末端变红下垂，全图唯一红色）
    s.rect(420, 440, 320, 216, WHITE, PANEL, 3, rx=14)
    s.line(452, 500, 452, 606, BLUE, 4)
    s.line(452, 606, 716, 606, BLUE, 4)
    pts = [(462, 506), (512, 514), (562, 530), (612, 552), (662, 578)]
    s.polyline(pts, BLUE, 6)
    s.polyline([(662, 578), (706, 612)], RED, 7)
    s.text(470, 648, "3′ 端质量衰减", 32, RED, "start", "bold")

    s.save("02_illumina_phasing.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

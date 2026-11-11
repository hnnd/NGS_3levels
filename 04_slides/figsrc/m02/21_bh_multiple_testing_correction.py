#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""21_bh_multiple_testing_correction.py — 21_bh_multiple_testing_correction.svg
（FIG-M02-27，P60，cols）：BH 多重检验校正四步流程【data-plot（算术设例）】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-27。
依据：教材 §11.4.6；讲义 ⑦ 7.3。设例：M=1000 个家族、α=0.05 → 全零假设下
期望假阳性 50（1000×0.05）；这是「期望个数」而非「假阳性比例」。
无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 21_bh_multiple_testing_correction.py
"""
from svghelp import (BLUE, CYAN, GRAY, GREEN, INK, RED, SVG, WHITE)


def check_data():
    m, alpha = 1000, 0.05
    expect = m * alpha
    assert expect == 50
    print(f"check: M={m} × α={alpha} = {expect:.0f} expected FP（算术设例）")
    return m, alpha, expect


def main():
    m, alpha, expect = check_data()

    s = SVG(800, 700)
    s.text(790, 44, "textbook §11.4.6 (arithmetic demo)", 30, GRAY, "end")

    steps = [
        ("①排序", "p(1) ≤ p(2) ≤ … ≤ p(M)", BLUE),
        ("②按秩放缩", "p(i) × M / i", BLUE),
        ("③倒序单调化", "min from right", BLUE),
        ("④截断至 1", "min(q, 1.0)", GREEN),
    ]
    x, w, h, gap = 40, 380, 96, 34
    y = 84
    for i, (lab, sub, color) in enumerate(steps):
        s.rect(x, y, w, h, WHITE, color, 6, rx=14)
        s.text(x + 24, y + 42, lab, 34, color, "start", "bold")
        s.text(x + 24, y + 80, sub, 30, GRAY, "start")
        if i < 3:
            s.arrow(x + w / 2, y + h + 3, x + w / 2, y + h + gap - 3, CYAN, 7)
        y += h + gap
    # 倒序回溯线（③ ← ④）
    s.path(f"M {x + w + 6} {84 + 3 * (h + gap) + h / 2} "
           f"C {x + w + 38} {84 + 3 * (h + gap) + h / 2} "
           f"{x + w + 38} {84 + 2 * (h + gap) + h / 2} "
           f"{x + w + 6} {84 + 2 * (h + gap) + h / 2}", CYAN, 5, dash="12 9")

    # 右侧设例算卡
    s.rect(470, 84, 300, 300, WHITE, "#E9E9E5", 4, rx=16)
    s.text(620, 140, "M = 1000 families", 32, INK, "middle", "bold")
    s.text(620, 196, f"α = {alpha}", 32, INK, "middle", "bold")
    s.text(620, 252, f"E[FP] = {expect:.0f}", 34, BLUE, "middle", "bold")
    s.text(620, 308, f"千个家族 {expect:.0f} 期望假阳性", 30, INK, "middle",
           "bold")
    s.text(620, 358, "语义非假阳性比例", 32, RED, "middle", "bold")

    s.save("21_bh_multiple_testing_correction.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

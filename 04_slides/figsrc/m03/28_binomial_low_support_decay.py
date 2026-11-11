#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""28_binomial_low_support_decay.py — 生成 28_binomial_low_support_decay.svg
（FIG-M03-29：局部深度 d 下低等位支持概率衰减曲线）【data-plot】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-29（P54，cols 一栏，800×700）。
数据：textbook/demos/ch10_depth_het_dropout.py Part 1（X ~ Binomial(d, 0.5)）：
P(X=0)：5× 3.125% → 10× 0.098%；P(X≤1)：5× 18.75% → 10× 1.074%；
P(X≤2)：5× 50.0% → 8× 14.45% → 10× 5.469% → 20× 0.020%。d=10 手算格点
1/1024, 11/1024, 56/1024。图内中文按方案（局部深度 低支持概率 泊松抽样
阶梯衰减 手算格点）。D135（2026-11-10，总编复检）：图内英文说明短语已译
中文（demos 出处标签按 D135「不增删图」仅译前缀，与 COURSE_SYNC §7.10 的
冲突已上报）；数学记号 P(X≤k) 与脚本名保留英文，字数不再按 ≤30 字核验。
依据：教材 §10.4.6（L177–199）。
"""
import math

from svghelp import *  # noqa: F401,F403

GRID = [5, 8, 10, 15, 20, 25, 30]


def p_le(d, k):
    return sum(math.comb(d, i) for i in range(k + 1)) / 2 ** d


def main():
    # 与 demos Part 1 逐格核对（解析二项）
    assert abs(p_le(5, 0) - 0.03125) < 1e-12
    assert abs(p_le(5, 1) - 0.1875) < 1e-12
    assert abs(p_le(5, 2) - 0.5) < 1e-12
    assert abs(p_le(8, 2) - 0.1445) < 1e-4
    assert abs(p_le(10, 2) - 56 / 1024) < 1e-12
    assert abs(p_le(10, 1) - 11 / 1024) < 1e-12
    assert abs(p_le(10, 0) - 1 / 1024) < 1e-12
    assert abs(p_le(20, 2) - 0.0002012) < 1e-7
    print("check vs demos Part 1: d=10 格点 1/1024, 11/1024, 56/1024")

    s = SVG(800, 700)
    s.text(400, 46, "低支持概率", 38, INK, "middle", "bold")

    x0, x1, y0, y1 = 100, 680, 560, 150

    def X(d):
        return x0 + (d - 5) / 25 * (x1 - x0)

    def Y(p):
        p = max(p, 1e-8)
        return min(y0, y0 - (math.log10(p) + 8) / 9 * (y0 - y1))

    s.rect(40, 70, 720, 540, WHITE, PANEL, 3, rx=14)
    s.line(x0, y0, 710, y0, BLUE, 4)
    s.line(x0, y0, x0, y1 - 20, BLUE, 4)
    for d in GRID:
        s.text(X(d), y0 + 40, str(d), 30, GRAY, "middle")
    s.text(400, 640, "局部深度 d（×）   泊松抽样", 30, GRAY, "middle")
    for p, lab in [(1e-2, "1%"), (1e-3, "0.1%"), (1e-4, "0.01%"),
                   (1e-5, "1e-5"), (1e-6, "1e-6"), (1e-7, "1e-7"),
                   (1e-8, "1e-8")]:
        s.text(x0 - 14, Y(p) + 10, lab, 30, GRAY, "end")
        s.line(x0, Y(p), 710, Y(p), PANEL, 2)

    curves = [(0, "P(X=0)", RED), (1, "P(X≤1)", ORANGE), (2, "P(X≤2)", CYAN_DEEP)]
    for k, lab, col in curves:
        pts = [(X(d), Y(p_le(d, k))) for d in range(5, 31)]
        s.polyline(pts, col, 6)
    s.text(620, Y(p_le(28, 2)) - 14, "P(X≤2)", 30, CYAN_DEEP, "middle")
    s.text(620, Y(p_le(28, 1)) - 14, "P(X≤1)", 30, ORANGE, "middle")
    s.text(620, y0 - 14, "P(X=0)", 30, RED, "middle")

    # d=10 手算格点
    d10 = X(10)
    s.line(d10, y1 - 20, d10, y0, GREEN, 4, dash="12 10")
    for lab, k in [("56/1024", 2), ("11/1024", 1), ("1/1024", 0)]:
        y = Y(p_le(10, k))
        s.circle(d10, y, 10, WHITE, GREEN, 6)
        s.text(d10 + 18, y + 10, lab, 30, GREEN, "start", "bold")
    s.text(d10 - 12, y1 - 34, "d=10", 30, GREEN, "middle", "bold")
    s.text(420, y1 - 34, "手算格点", 32, GREEN, "middle", "bold")

    # 低深度风险区
    s.rect(x0, y1 - 20, X(8) - x0, y0 - y1 + 20, RED_TINT)
    s.text(180, 200, "阶梯衰减", 32, RED, "middle", "bold")
    s.text(400, 690, "数据源： ch10_depth_het_dropout.py", 30, GRAY, "middle")
    s.save("28_binomial_low_support_decay.svg")


if __name__ == "__main__":
    main()

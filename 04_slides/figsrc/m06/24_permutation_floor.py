#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""24_permutation_floor.py — FIG-M06-24 两等组样本量 vs 最小可能 p 值阶梯（data-plot）

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-24（P41，cols 一栏
800×700，data-plot）。
数据来源：教材 §18.4.8 的手算表公式 p_min = 2/C(2m,m)（两等组、穷举置换、无限制置换），
脚本用 math.comb 现算并断言（见 main 里的 assert），不抄任何现成数字：
3v3 2/20 = 0.100；4v4 2/70 = 0.0286；5v5 2/252 = 0.0079；6v6 2/924 = 0.0022；
10v10 2/184 756 ≈ 1.08e-5。
图内汉字 = 方案原句逐字，共 22 字（三对三永不显著 / 五对五进入有效区 /
加重复优于加深度）；其余标注为组数、最小 p 值与坐标刻度（10 的幂用 ASCII 指数）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 24_permutation_floor.py
"""
import sys
import math

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403
from svghelp import (BLUE, GRAY, GREEN, GREEN_TINT, INK, RED, SVG, WHITE)

MS = [3, 4, 5, 6, 10]
PRINTED = ["0.100", "0.0286", "0.0079", "0.0022", "1.08e-5"]
YTICKS = [(0, "1"), (-2, "1e-2"), (-4, "1e-4"), (-6, "1e-6")]
AX, X0, X1 = 116, 180, 680        # 纵轴 x、绘图区左右
YTOP, YBASE = 210, 552            # YTOP = 10⁰，YBASE = 10⁻⁶


def pmin(m):
    return 2 / math.comb(2 * m, m)


def main():
    vals = {m: pmin(m) for m in MS}
    assert abs(vals[3] - 0.100) < 5e-4, vals[3]
    assert abs(vals[4] - 0.0285714) < 5e-7, vals[4]
    assert abs(vals[5] - 0.0079365) < 5e-7, vals[5]
    assert abs(vals[6] - 0.0021645) < 5e-7, vals[6]
    assert abs(vals[10] - 1.0825e-5) < 5e-9, vals[10]
    assert f"{vals[3]:.3f}" == "0.100"
    assert f"{vals[4]:.4f}" == "0.0286"
    assert f"{vals[5]:.4f}" == "0.0079"
    assert f"{vals[6]:.4f}" == "0.0022"
    assert f"{vals[10]:.2e}" == "1.08e-05"
    print("check: " + " / ".join(f"{m}v{m} p_min={vals[m]:.4g}" for m in MS))

    s = SVG(800, 700)

    def X(i):
        return X0 + i * (X1 - X0) / (len(MS) - 1)

    def Y(p):
        return YBASE - (math.log10(p) + 6) / 6 * (YBASE - YTOP)

    # 绿色有效区底纹：从 5v5 起、p ≤ 0.0079 的区域
    gy = Y(vals[5])
    s.rect(X(2) - 14, gy - 6, X1 - X(2) + 34, YBASE - gy + 6, GREEN_TINT, rx=12)

    s.line(AX, YBASE, X1 + 34, YBASE, GRAY, 4)
    s.line(AX, YBASE, AX, YTOP - 8, GRAY, 4)
    for e, lab in YTICKS:
        y = YBASE - (e + 6) / 6 * (YBASE - YTOP)
        s.line(AX, y, AX - 10, y, GRAY, 4)
        s.text(AX - 20, y + 10, lab, 30, GRAY, "end")

    # 公式（非中文标注）
    s.text(X1 + 34, 118, "p_min = 2/C(2m,m)", 30, GRAY, "end")

    # 阶梯折线（深蓝骨架）
    pts = [(X(i), Y(vals[m])) for i, m in enumerate(MS)]
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        s.line(x1, y1, x2, y1, BLUE, 6)
        s.line(x2, y1, x2, y2, BLUE, 6)

    for i, m in enumerate(MS):
        px, py = pts[i]
        s.circle(px, py, 8, BLUE)
        s.text(px, YBASE + 42, f"{m}v{m}", 30, GRAY, "middle", "bold")

    # 最小 p 值：前四段写在水平线下方；末点写在点左侧
    for i in range(len(MS) - 1):
        cx = (pts[i][0] + pts[i + 1][0]) / 2
        s.text(cx, pts[i][1] + 46, PRINTED[i], 30, INK, "middle", "bold")
    s.text(pts[-1][0] - 18, pts[-1][1] + 10, PRINTED[-1], 30, INK, "end", "bold")

    # 红：3v3 的置换天花板（全图唯一警示）
    px = pts[0][0]
    s.line(px, 172, px, YBASE + 8, RED, 5, dash="12 9")
    s.text(px + 18, 196, "三对三永不显著", 30, RED, "start", "bold")

    # 绿：5v5 起进入有效区
    s.chip(596, 292, "五对五进入有效区", 30, WHITE, GREEN, GREEN, sw=4)

    s.text(400, 646, "加重复优于加深度", 32, INK, "middle", "bold")

    s.save("24_permutation_floor.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

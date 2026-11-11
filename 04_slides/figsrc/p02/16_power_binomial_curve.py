#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_power_binomial_curve.py — 生成 16_power_binomial_curve.svg
（FIG-P02-19：期望捕获达标 ≠ 抓取把握达标）【data-plot】

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-19（Slide 40，cols 一栏，800×700）。
数据：目标丰度 p=0.01、需至少捕获 k=10 个目标细胞；P(X≥10) 用**精确二项**
（math.comb 整数组合，无第三方库）逐 n 计算，并断言与方案/教材同口径的四个点：
n=1000 → 0.5427、n=1568（整数最小 95%）→ 0.9502、n=1570（脚本网格值）→ 0.9507、
n=2000 → 0.9952；另断言最小整数 n 确为 1568（n=1567 为 0.94996 < 0.95）。
图内汉字 = 方案指定整句逐字一致（28 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 16_power_binomial_curve.py
"""
import re
import sys
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "期望达标不等于把握达标。二项抽样规划细胞预算，九五把握需千五。"
P, K = 0.01, 10


def ge_k(n, p=P, k=K):
    """P(X >= k) 的精确二项计算（整数组合，无第三方库）。"""
    return 1.0 - sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k))


def main():
    pts = {n: ge_k(n) for n in (500, 1000, 1568, 1570, 2000, 2500)}
    assert round(pts[1000], 4) == 0.5427, pts[1000]
    assert round(pts[1568], 4) == 0.9502, pts[1568]
    assert round(pts[1570], 4) == 0.9507, pts[1570]
    assert round(pts[2000], 4) == 0.9952, pts[2000]
    n_min = next(n for n in range(500, 3000) if ge_k(n) >= 0.95)
    assert n_min == 1568 and ge_k(1567) < 0.95, (n_min, ge_k(1567))
    print(f"check: n_min(95%)={n_min}; P1000={pts[1000]:.4f} "
          f"P1568={pts[1568]:.4f} P1570={pts[1570]:.4f} P2000={pts[2000]:.4f}")

    s = SVG(800, 700, "Sampling power vs expected capture", plan=TEXT)
    X0, X1, YT, YB = 150, 700, 120, 430

    def px(n):
        return X0 + (n - 500) / 2000 * (X1 - X0)

    def py(v):
        return YB - v * (YB - YT)

    s.line(X0, YT, X0, YB, INK, 3)
    s.line(X0, YB, X1 + 10, YB, INK, 3)
    s.yaxis(X0, YT, YB, [(py(1.0), "1.0"), (py(0.5), "0.5"), (py(0.0), "0.0")])
    for n in (500, 1000, 1500, 2000, 2500):
        s.line(px(n), YB, px(n), YB + 8, INK, 3)
        s.text(px(n), YB + 40, str(n), 30, GRAY, "middle")
    s.text((X0 + X1) / 2, 500, "cells planned (n)", 30, GRAY, "middle")
    s.text(150, 106, "P(X≥10)", 30, GRAY, "start", "bold")

    # 95% 把握线
    s.line(X0, py(0.95), X1, py(0.95), GREEN, 4, dash="12 8")
    s.text(690, py(0.95) - 12, "0.95", 30, GREEN, "end", "bold")

    # 精确二项曲线
    xs = list(range(500, 2501, 25))
    s.polyline([(px(n), py(ge_k(n))) for n in xs], BLUE, 6)

    # n=1000：期望恰为 10，把握只有 54.3%
    s.line(px(1000), YT, px(1000), YB, ORANGE, 4, dash="10 8")
    s.circle(px(1000), py(pts[1000]), 9, ORANGE)
    s.text(px(1000) - 14, 268, f"{pts[1000]:.3f}", 30, ORANGE, "end", "bold",
           bg=True)

    # n=1570（脚本网格值）：刚好压住 95% 线
    s.line(px(1570), YT, px(1570), YB, GREEN, 4, dash="10 8")
    s.circle(px(1570), py(pts[1570]), 9, GREEN)
    s.text(px(1570) + 14, 150, f"{pts[1570]:.3f}", 30, GREEN, "start", "bold",
           bg=True)

    # n=2000：把握 99.5%
    s.circle(px(2000), py(pts[2000]), 9, BLUE)
    s.text(px(2000) + 14, 210, f"{pts[2000]:.3f}", 30, BLUE, "start", "bold")

    # 红色（1 处）：期望达标不等于把握达标
    s.text(696, 396, "EXPECTED ≠ POWER", 30, RED, "end", "bold")

    s.caption(["期望达标不等于把握达标。",
               "二项抽样规划细胞预算，九五把握需千五。"], [INK, INK], 30,
              top=536)
    s.save("16_power_binomial_curve.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_depth_saturation_curve.py — 生成 10_depth_saturation_curve.svg
（FIG-M01-12：固定 n=6 深度饱和曲线）【data-plot】

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-12（P30，cols 一栏，800×700）。
数据（与 demos 现跑一致）：demos/ch13_variance_partition.py --selftest Part 3
（固定 n=6；d=5: 0.263；d=20: 0.321；d=40: 0.334；d=120: 0.343，
20→120 M 相对增幅 +6.7%）。教材 §13.4.3 L193、§13.5.3 L359。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 10_depth_saturation_curve.py
"""
import sys
from pathlib import Path

from svghelp import *  # noqa: F401,F403

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from ch13_variance_partition import power_twosample  # noqa: E402

DEPTHS = [5, 10, 20, 30, 40, 60, 120]
PRINTED = [0.263, 0.299, 0.321, 0.329, 0.334, 0.338, 0.343]


def main():
    pw = {d: power_twosample(6, 1.0 + 2.0 / d, 1.0, 0.05) for d in DEPTHS}
    for d, pp in zip(DEPTHS, PRINTED):
        assert abs(pw[d] - pp) < 5e-4, (d, pw[d], pp)
    gain = 100 * (pw[120] / pw[20] - 1)
    assert abs(gain - 6.7) < 0.15, gain
    print(f"check: n=6 功效 d=20 {pw[20]:.3f} → d=120 {pw[120]:.3f}，"
          f"增幅 +{gain:.1f}%（demos Part 3）")

    s = SVG(800, 700)
    s.text(60, 46, "固定 n=6 深度饱和", 34, INK, "start", "bold")

    x0, x1, y0, y1 = 100, 740, 580, 80

    def X(d):
        return x0 + d / 130 * (x1 - x0)

    def Y(p):
        return y0 - (p - 0.25) / 0.11 * (y0 - y1)

    s.line(x0, y1, x0, y0, BLUE, 4)
    s.line(x0, y0, x1, y0, BLUE, 4)
    for tick in (0.30, 0.35):
        s.text(x0 - 12, Y(tick) + 10, f"{tick:.2f}", 30, GRAY, "end")
    for d in (10, 40, 60):
        s.text(X(d), y0 + 40, str(d), 30, GRAY, "middle")

    pts = [(X(d), Y(pw[d])) for d in DEPTHS]
    s.curve(pts, BLUE, 6)
    for d in DEPTHS:
        s.circle(X(d), Y(pw[d]), 7, BLUE)

    # 红色区间支架：20→120 M（全图红色标注）
    s.line(X(20), Y(pw[20]), X(20), 640, RED, 4, dash="14 10")
    s.line(X(120), Y(pw[120]), X(120), 640, RED, 4, dash="14 10")
    s.line(X(20), 640, X(120), 640, RED, 5)
    s.line(X(20), 632, X(20), 648, RED, 5)
    s.line(X(120), 632, X(120), 648, RED, 5)
    s.text(300, 680, "20→120 M 深度翻 6 倍", 30, RED, "middle", "bold")
    s.text(590, 680, "功效仅增 6.7%", 30, RED, "middle", "bold")

    s.text(740, 46, "不可盲目加深", 30, GRAY, "end")

    s.save("10_depth_saturation_curve.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

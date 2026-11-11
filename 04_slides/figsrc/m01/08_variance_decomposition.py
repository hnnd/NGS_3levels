#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_variance_decomposition.py — 生成 08_variance_decomposition.svg
（FIG-M01-10：方差分解与生物学方差地板）【data-plot】

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-10（P26，cols 一栏，800×700）。
数据（与 demos 现跑一致）：demos/ch13_variance_partition.py --selftest Part 1
（σ²_bio=1.0, σ²_shot=2.0；d=5: v=1.4000 技术占 28.6%；d=20: v=1.1000；
d=40: v=1.0500（20→40 M 降 4.5%）；d=120: v=1.0167）。教材 §13.4.3 L152–156。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 08_variance_decomposition.py
"""
from svghelp import *  # noqa: F401,F403

SB, ST = 1.0, 2.0  # demos 默认 σ²_bio / σ²_shot（每 1 M）


def main():
    depths = [5, 10, 20, 30, 40, 60, 80, 120]
    v = {d: SB + ST / d for d in depths}
    # 与 demos Part 1 印刷值逐一核对
    assert abs(v[5] - 1.4000) < 1e-9
    assert abs(v[20] - 1.1000) < 1e-9
    assert abs(v[40] - 1.0500) < 1e-9
    assert abs(v[120] - 1.0167) < 1e-4
    tech5 = 100 * (ST / 5) / v[5]
    drop = 100 * (1 - v[40] / v[20])
    assert abs(tech5 - 28.6) < 0.05, tech5
    assert abs(drop - 4.5) < 0.05, drop
    print(f"check: v(5)={v[5]:.4f}（技术 {tech5:.1f}%）；v(20)={v[20]:.4f}；"
          f"v(40)={v[40]:.4f}；20→40 M 降 {drop:.1f}%（demos Part 1）")

    s = SVG(800, 700)
    s.text(400, 48, "v(d) 随深度收敛", 34, INK, "middle", "bold")

    x0, x1, y0, y1 = 100, 740, 560, 90

    def X(d):
        return x0 + d / 125 * (x1 - x0)

    def Y(val):
        return y0 - (val - 1.0) / 0.45 * (y0 - y1)

    # 坐标轴与刻度
    s.line(x0, y1, x0, y0, BLUE, 4)
    s.line(x0, y0, x1, y0, BLUE, 4)
    for tick in (1.0, 1.2, 1.4):
        s.text(x0 - 12, Y(tick) + 10, f"{tick:.1f}", 30, GRAY, "end")
    for d in (5, 20, 40, 60, 120):
        s.line(X(d), y0, X(d), y0 + 10, BLUE, 3)
        s.text(X(d), y0 + 44, str(d), 30, GRAY, "middle")

    # 生物学方差地板（绿虚线）
    s.line(x0, Y(1.0), x1, Y(1.0), GREEN, 5, dash="16 12")
    s.text(x1 - 10, Y(1.0) - 20, "生物学方差地板", 30, GREEN, "end", "bold")

    # v(d) 曲线（深蓝）
    pts = [(X(d), Y(v[d])) for d in depths]
    s.curve(pts, BLUE, 6)
    s.circle(X(5), Y(v[5]), 9, BLUE)
    s.text(X(5) + 24, Y(v[5]) - 24, "d=5 技术占 28.6%", 30, BLUE, "start", "bold")

    # 红色标注：20→40 M 仅降 4.5%（全图唯一红色）
    # 双向箭头挂在两个曲线点下方，文字放右上空区并以虚线引出，避开曲线
    s.darrow(X(20), 522, X(40), 522, RED, 5)
    s.line(X(20), 510, X(20), 528, RED, 5)
    s.line(X(40), 510, X(40), 528, RED, 5)
    s.line(330, 498, 468, 350, RED, 4, dash="12 10")
    s.text(480, 330, "20→40 M 仅降 4.5%", 30, RED, "start", "bold")

    s.save("08_variance_decomposition.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

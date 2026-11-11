#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_xlim_vs_coord.py — 生成 14_xlim_vs_coord.svg
（FIG-U02-14：标度截断 vs 坐标缩放）

方案：reviews/course/U02_FIGP_001.md §4 FIG-U02-14（P39，cols 一栏，viewBox 800×700）。
数据：10 行输入（x=1…10），xlim(2,5) 移除界外 6 行、coord_cartesian(xlim=c(2,5)) 不移除
——教材 §3.4.6 L209 本机核验（ggplot2 4.0.3），本任务已在 ta 复跑一致（见回执）。
红 1 处＝真删（× 标记 + Removed 6 rows 同场景）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 14_xlim_vs_coord.py
"""
from svghelp import *  # noqa: F401,F403

PTS = list(range(1, 11))          # x = 1..10，y = x
IN_WIN = {2, 3, 4, 5}             # 窗内 4 点
X0, X1 = 80, 720                  # x 数据 1..10 → 像素
Y_TOP, Y_BASE = 110, 300          # 上面板
Y_TOP2, Y_BASE2 = 460, 600        # 下面板


def xmap(v):
    return X0 + (v - 1) * (X1 - X0) / 9


def ymap(v, top=Y_TOP, base=Y_BASE):
    return base - (v - 1) * (base - top) / 9


def main():
    s = SVG(800, 700)
    wx1, wx2 = xmap(2), xmap(5)

    s.text(80, 64, "+ xlim(2, 5)", 32, INK, "start", "bold")
    s.text(720, 64, "真删", 32, RED, "end", "bold")
    s.rect(wx1, Y_TOP - 24, wx2 - wx1, Y_BASE - Y_TOP + 24, GREEN_TINT)
    s.line(X0, Y_TOP - 24, X0, Y_BASE, INK, 3)
    s.line(X0, Y_BASE, X1, Y_BASE, INK, 3)
    for v in PTS:
        x, y = xmap(v), ymap(v)
        if v in IN_WIN:
            s.circle(x, y, 10, GREEN)
        else:
            s.line(x - 12, y - 12, x + 12, y + 12, RED, 5)
            s.line(x - 12, y + 12, x + 12, y - 12, RED, 5)
    s.rect(80, 326, 640, 44, PANEL, rx=6)
    s.text(400, 357, "Removed 6 rows", 30, GRAY, "middle")

    s.text(80, 416, "+ coord_cartesian(xlim = c(2, 5))", 30, INK, "start", "bold")
    s.text(720, 416, "只裁视野", 32, GREEN, "end", "bold")
    s.rect(wx1, Y_TOP2 - 24, wx2 - wx1, Y_BASE2 - Y_TOP2 + 24, "none", GREEN, 5)
    s.line(X0, Y_TOP2 - 24, X0, Y_BASE2, INK, 3)
    s.line(X0, Y_BASE2, X1, Y_BASE2, INK, 3)
    for v in PTS:
        x, y = xmap(v), ymap(v, Y_TOP2, Y_BASE2)
        if v in IN_WIN:
            s.circle(x, y, 10, GREEN)
        else:
            s.circle(x, y, 10, "#C9C9C3")
    s.text(400, 678, "数据框都没动", 30, GRAY, "middle", "bold")
    s.save("14_xlim_vs_coord.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

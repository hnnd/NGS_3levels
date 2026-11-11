#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_repeat_spanning_geometry.py — 02_repeat_spanning_geometry.svg
（FIG-M02-03，P13，cols）：读长 L 与重复 R 的跨越几何与有效起点数【data-plot】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-03。数据（与 demos 现跑一致）：
demos/ch08_debruijn_repeat.py --selftest（R=100、侧翼 300、种子 20261102）：
L=80/90/100 → 0 起点；L=110→10、L=150→50、L=180→80（其余 L 按 L−R 复算）。
无网络；种子固定。用法：PYTHONDONTWRITEBYTECODE=1 python3 02_repeat_spanning_geometry.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch08_debruijn_repeat as demo  # noqa: E402

from svghelp import (BLUE, FONT, GRAY, GREEN, GREEN_TINT, INK, OUT, PAPER, RED,
                     RED_TINT, SVG, WHITE)

R = 100


def check_data():
    pts = {}
    for L in range(80, 181, 10):
        n = demo.spanning_starts(R, L)
        pts[L] = n
        assert n == max(0, L - R), (L, n)
    assert pts[80] == pts[90] == pts[100] == 0
    assert (pts[110], pts[150], pts[180]) == (10, 50, 80)
    print(f"check: L=80/90/100→0；110→{pts[110]}、150→{pts[150]}、"
          f"180→{pts[180]}（demos 复算）")
    return pts


def main():
    pts = check_data()

    s = SVG(800, 700)

    # 标题（左上）
    s.text(60, 96, "R=100 固定重复", 34, BLUE, "start", "bold")

    # 坐标区：x 轴 L∈[80,180] → px 60..740；y 轴 起点数∈[0,88] → py 560..129
    x0, x1, y0, y1 = 60.0, 740.0, 560.0, 129.0

    def px(L):
        return x0 + (L - 80) / 100.0 * (x1 - x0)

    def py(v):
        return y0 - v / 88.0 * (y0 - y1)

    # 底纹：L≤R 浅红警示区、L>R 浅绿可跨越区
    s.rect(x0, y1, px(100) - x0, y0 - y1, RED_TINT)
    s.rect(px(100), y1, x1 - px(100), y0 - y1, GREEN_TINT)

    # 坐标轴
    s.line(x0, y0, x1 + 14, y0, INK, 5)
    s.line(x0, y0, x0, y1 - 12, INK, 5)
    for L in (80, 100, 120, 140, 160, 180):
        s.line(px(L), y0, px(L), y0 + 10, INK, 4)
        s.text(px(L), y0 + 44, str(L), 30, INK, "middle")
    for v in (0, 20, 40, 60, 80):
        s.line(x0 - 10, py(v), x0, py(v), INK, 4)
        s.text(x0 - 18, py(v) + 11, str(v), 30, INK, "end")

    # 深蓝阶梯折线
    line = [(px(L), py(n)) for L, n in sorted(pts.items())]
    s.polyline(line, BLUE, 7)
    # 演示三点高亮
    for L in (110, 150, 180):
        s.circle(px(L), py(pts[L]), 11, WHITE, BLUE, 6)
        s.text(px(L), py(pts[L]) - 24, str(pts[L]), 30, BLUE, "middle", "bold")

    # 绿色双向箭头：L=150 处从 0 到 50，标注「L>R 起点 L−R」
    s.darrow(px(150) + 34, py(0), px(150) + 34, py(50), GREEN, 6)
    s.text(px(150) + 58, py(25), "L>R 起点 L−R", 30, GREEN, "start", "bold")

    # 红色警示文（区内恒 0）+ 指入箭头
    s.text(60, py(76), "L≤R 起点为 0：信息不存在", 30, RED, "start", "bold")
    s.arrow(240, py(76) + 14, 200, py(60) + 6, RED, 5)

    # 底部红字警示
    s.text(400, 656, "换算法也定不出连接", 34, RED, "middle", "bold")

    s.save("02_repeat_spanning_geometry.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

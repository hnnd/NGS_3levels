#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_elbowplot_vs_umap_topology.py — 生成 10_elbowplot_vs_umap_topology.svg
（FIG-P02-12：PCA 拐点截断信息预算，UMAP 只保局部拓扑、三禁推断）

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-12（Slide 29，cols 一栏，800×700）。
依据：教材 §17.4.5 L153–155。曲线形态为示意（特征值单调陡降），无数值断言；
无随机数、无网络。
图内汉字 = 方案指定整句逐字一致（30 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 10_elbowplot_vs_umap_topology.py
"""
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "拐点截断主成分，局部拓扑不保全局距离。禁推发育谱系与绝对群体大小。"


def main():
    s = SVG(800, 700, "PCA elbow cutoff vs UMAP local topology", plan=TEXT)

    # ---------- 上：PCA 拐点截断 ----------
    s.text(60, 96, "PCA", 32, BLUE, "start", "bold")
    X0, X1, YB = 110, 740, 290
    s.line(X0, 100, X0, YB, INK, 3)
    s.line(X0, YB, X1, YB, INK, 3)
    n, w = 15, (X1 - X0) / 15
    for i in range(1, n + 1):
        h = 12 + 170 * math.exp(-0.28 * i)
        x = X0 + w * (i - 1) + 4
        col = ORANGE if i <= 10 else PURPLE
        s.rect(x, YB - h, w - 8, h, col)
    for i in (1, 5, 10, 15):
        x = X0 + w * (i - 0.5)
        s.line(x, YB, x, YB + 8, INK, 3)
        s.text(x, YB + 42, str(i), 30, GRAY, "middle")
    # 截断线（信息预算）
    xc = X0 + w * 10
    s.line(xc, 100, xc, YB + 8, BLUE, 5, dash="12 8")
    s.text(xc, 92, "PC 10", 30, BLUE, "middle", "bold")

    # ---------- 下：UMAP 局部拓扑与三禁 ----------
    s.text(60, 386, "UMAP", 32, BLUE, "start", "bold")
    blobs = ((200, 455, 42, GREEN), (352, 405, 30, CYAN), (556, 455, 44, GREEN),
             (700, 410, 26, ORANGE))
    for cx, cy, r, col in blobs:
        s.cluster(cx, cy, r, 40, col, seed=cx // 7, rmin=3.5, rmax=6.0)

    # 距离 ≠ 发育谱系（红，唯一警示区）
    s.line(248, 450, 508, 456, GRAY, 4, dash="10 8")
    s.arrow(492, 456, 508, 456, GRAY, 4, 10)
    s.cross(378, 453, 17, RED, 8)

    # 半径 ≠ 群体大小、相邻 ≠ 祖先后代（灰叉，非警示色）
    s.arrow(556, 455, 556, 409, GRAY, 4, 10)
    s.cross(583, 432, 12, GRAY, 6)
    s.arrow(612, 442, 664, 420, GRAY, 4, 10)
    s.cross(638, 431, 12, GRAY, 6)

    s.caption(["拐点截断主成分，局部拓扑不保全局距离。",
               "禁推发育谱系与绝对群体大小。"], [INK, INK], 30, top=536)
    s.save("10_elbowplot_vs_umap_topology.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())

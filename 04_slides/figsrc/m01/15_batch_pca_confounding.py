#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_batch_pca_confounding.py — 生成 15_batch_pca_confounding.svg
（FIG-M01-17：平衡区组 vs 完全混杂 PCA 几何对比）【data-plot】

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-17（P41，cols 一栏，800×700）。
数据（合成设例，固定种子）：Rscript demos/ch13_batch_pca.R --selftest 现跑实测
平衡区组 PC1=70.8%, PC2=13.8%（两方向正交可拆）；完全混杂 PC1=82.0%,
PC2=3.3%（同方向无法分离，set.seed(1234)）。教材 §13.4.5 L258、§13.5.2 L355。
无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 15_batch_pca_confounding.py
"""
import numpy as np

from svghelp import *  # noqa: F401,F403

SEED = 42  # 固定种子（Python 侧设例点云；百分比标签为 R demo 现跑值）


def main():
    rng = np.random.default_rng(SEED)
    s = SVG(800, 700)
    s.text(400, 44, "PC1 70.8% vs 82.0%", 32, INK, "middle", "bold")

    # ---- 左面板：平衡区组（批次沿 PC1、处理沿 PC2，正交可拆） ----
    s.rect(40, 70, 340, 500, WHITE, PANEL, 3, rx=14)
    cx, cy = 210, 320
    s.darrow(cx - 115, cy, cx + 115, cy, GRAY, 4)
    s.darrow(cx, cy - 140, cx, cy + 140, GRAY, 4)
    for i in range(2):
        x = cx - 72 + rng.normal(0, 16)
        y1 = cy - 48 + rng.normal(0, 14)
        y2 = cy + 48 + rng.normal(0, 14)
        s.circle(x, y1, 12, BLUE)
        s.polygon([(x, y2 - 12), (x - 11, y2 + 8), (x + 11, y2 + 8)], BLUE)
        x = cx + 72 + rng.normal(0, 16)
        s.circle(x, y1 + rng.normal(0, 6), 12, ORANGE)
        s.polygon([(x, y2 - 12), (x - 11, y2 + 8), (x + 11, y2 + 8)], ORANGE)
    s.text(195, 425, "PC1 70.8%", 30, GRAY, "end")
    s.text(60, 108, "PC2 13.8%", 30, GRAY, "start")
    s.text(cx, 600, "平衡区组：两方向正交可拆", 30, GREEN, "middle", "bold")

    # ---- 右面板：完全混杂（批次≡处理，同方向无法分离） ----
    s.rect(420, 70, 340, 500, WHITE, PANEL, 3, rx=14)
    cx, cy = 590, 320
    s.darrow(cx - 115, cy, cx + 115, cy, GRAY, 4)
    s.darrow(cx, cy - 140, cx, cy + 140, GRAY, 4)
    for i in range(4):
        x1 = cx - 62 + rng.normal(0, 15)
        y1 = x1 * 0.9 + rng.normal(0, 12)
        s.circle(cx + x1 * 0.62, cy + y1 * 0.62, 12, BLUE)
        x2 = cx + 62 + rng.normal(0, 15)
        y2 = x2 * 0.9 + rng.normal(0, 12)
        s.polygon([(cx + x2 * 0.62, cy + y2 * 0.62 - 12),
                   (cx + x2 * 0.62 - 11, cy + y2 * 0.62 + 8),
                   (cx + x2 * 0.62 + 11, cy + y2 * 0.62 + 8)], ORANGE)
    # 红色双向箭头：同方向无法分离（全图唯一红色）
    s.darrow(457, 443, 687, 253, RED, 6)
    s.text(585, 415, "PC1 82.0%", 30, GRAY, "end")
    s.text(cx, 600, "完全混杂：同方向无法分离", 30, RED, "middle", "bold")

    s.text(755, 648, "设例", 30, GRAY, "end")

    s.save("15_batch_pca_confounding.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

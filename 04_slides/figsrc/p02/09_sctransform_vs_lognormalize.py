#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_sctransform_vs_lognormalize.py — 生成 09_sctransform_vs_lognormalize.svg
（FIG-P02-11：LogNormalize 与 SCTransform 的模型差异与残差边界）

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-11（Slide 28，cols 一栏，800×700）。
依据：教材 §17.4.5 L145–159（残差只供降维聚类，不得直接算倍数或做组间检验）。
纯示意：无数据、无随机数、无网络。
图内汉字 = 方案指定整句逐字一致（28 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 09_sctransform_vs_lognormalize.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "常规变换难齐方差，负二项回归取残差。残差仅供降维，禁直接算倍数。"
BOX = ((96, "COUNTS"), (182, "LIBRARY SIZE"), (268, "log1p(CPM)"))


def channel(s, cx, tint, stroke, boxes):
    for y, label in boxes:
        s.rect(cx - 150, y, 300, 56, tint, stroke, 4, rx=10)
        s.text(cx, y + 40, label, 32, INK, "middle")
    for i in range(len(boxes) - 1):
        s.arrow(cx, boxes[i][0] + 56, cx, boxes[i + 1][0], GRAY, 5, 13)


def main():
    s = SVG(800, 700, "LogNormalize vs SCTransform", plan=TEXT)

    s.text(60, 78, "A  LOGNORMALIZE", 32, BLUE, "start", "bold")
    s.text(440, 78, "B  SCTRANSFORM", 32, BLUE, "start", "bold")

    channel(s, 215, BLUE_TINT, BLUE, BOX)
    s.arrow(215, 324, 215, 356, GREEN, 5, 13)
    s.text(215, 404, "FOLD CHANGE", 32, GREEN, "middle", "bold")

    channel(s, 585, PURPLE_TINT, PURPLE,
            ((96, "COUNTS"), (182, "NB GLM"), (268, "RESIDUALS")))
    s.arrow(585, 324, 585, 346, GRAY, 5, 13)

    # 红色（1 处）：残差的边界——只给降维聚类，不给倍数与检验
    s.rect(435, 350, 300, 56, RED, None, 3, rx=10)
    s.text(585, 386, "DIM-RED ONLY", 32, WHITE, "middle", "bold")

    s.caption(["常规变换难齐方差，负二项回归取残差。",
               "残差仅供降维，禁直接算倍数。"], [INK, INK], 30, top=500)
    s.save("09_sctransform_vs_lognormalize.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_spatial_deconvolution_reference_dependency.py — 生成
17_spatial_deconvolution_reference_dependency.svg
（FIG-P02-21：空间去卷积给比例、依赖单细胞参考的完备性）

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-21（Slide 43，cols 一栏，800×700）。
依据：教材 §17.4.11 L268–270、图 17-1 面板②。纯示意：无数据、无随机数、
无网络；比例 60/25/15 为示意数字（不构成对任何真实样本的断言）。
图内汉字 = 方案指定整句逐字一致（27 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 17_spatial_deconvolution_reference_dependency.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "单细胞参考推算微区比例。图谱缺项时信号被分摊，无法凭空推断。"
ROWS = (GREEN, ORANGE, PURPLE)


def main():
    s = SVG(800, 700, "Spatial deconvolution needs a complete reference",
            plan=TEXT)

    # 左：单细胞参考矩阵（三类细胞的表达指纹）
    s.text(40, 100, "REFERENCE", 30, BLUE, "start", "bold")
    for i, col in enumerate(ROWS):
        for j in range(4):
            v = [GREEN_TINT, GREEN, GREEN, GREEN_TINT,
                 ORANGE_TINT, ORANGE, ORANGE, ORANGE_TINT,
                 PURPLE_TINT, PURPLE, PURPLE, PURPLE_TINT]
            s.rect(40 + j * 42, 124 + i * 42, 38, 38, v[i * 4 + j], col, 2,
                   rx=4)

    # 中：一个混合表达的 spot，送进去卷积算法
    s.circle(268, 208, 42, WHITE, BLUE, 5)
    for k, (dx, dy, col) in enumerate(((-14, -12, GREEN), (14, 6, ORANGE),
                                       (-4, 20, PURPLE))):
        s.circle(268 + dx, 208 + dy, 12, col)
    s.arrow(206, 190, 222, 196, BLUE, 4, 12)
    s.arrow(314, 208, 340, 208, BLUE, 4, 14)
    s.rect(344, 168, 116, 80, BLUE_TINT, BLUE, 4, rx=10)
    s.text(402, 218, "RCTD", 32, BLUE, "middle", "bold")

    # 右：推断出的细胞类型比例
    s.text(543, 108, "PROP", 30, BLUE, "middle", "bold")
    s.arrow(464, 208, 500, 208, BLUE, 4, 14)
    s.rect(506, 124, 74, 220, WHITE, BLUE, 3)
    s.rect(506, 124, 74, 132, GREEN)
    s.rect(506, 256, 74, 55, ORANGE)
    s.rect(506, 311, 74, 33, PURPLE)
    for y, lab in ((190, "60"), (283, "25"), (327, "15")):
        s.text(596, y, lab, 30, INK, "start", "bold")

    # 红色（1 处）：参考里没有的类型永远不会被算出来
    s.line(543, 352, 543, 380, RED, 4, dash="10 8")
    s.rect(400, 380, 300, 76, "none", RED, 5, rx=10, dash="12 8")
    s.text(550, 430, "MISSING TYPE", 32, RED, "middle", "bold")

    s.caption(["单细胞参考推算微区比例。",
               "图谱缺项时信号被分摊，无法凭空推断。"], [INK, INK], 30,
              top=500)
    s.save("17_spatial_deconvolution_reference_dependency.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""03_individual_vs_cell_structure.py — 生成 03_individual_vs_cell_structure.svg
（FIG-P02-04：3 个个体 → 同管解离 → 30,000 个细胞的观测单位与统计单位错位）

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-04（Slide 15，cols 一栏，800×700）。
依据：教材 §17.4.1 L77–85、§17.5.1 L298–305；deck P15「3 个个体，每个解离
10,000 个细胞／观测 30,000 个，独立个体仍是 3 个」。
纯示意：30,000 与 10,000 为 deck 与教材同口径的设例，非实测计数。
图内汉字 = 方案指定整句逐字一致（29 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 03_individual_vs_cell_structure.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "同管细胞共享微环境与批次。有效样本量取决于个体数，不是细胞总数。"
# 图内标签的中文译文（D135）；10,000 / 30,000 为设例数，n 为统计字段，保留数字与符号。
EXTRA = "个体同一管观测"
XS = (156, 400, 644)


def main():
    s = SVG(800, 700, "Three individuals vs 30,000 cells", plan=TEXT,
            extra=EXTRA)

    # 顶层：3 个独立个体（真实 n=3）
    for i, x in enumerate(XS):
        s.rect(x - 100, 62, 200, 88, BLUE_TINT, BLUE, 5, rx=12)
        s.text(x, 118, f"个体 {i + 1}", 34, BLUE, "middle", "bold")
        s.arrow(x, 154, x, 194, BLUE, 5, 14)

    # 中层：三路汇入同一根解离管（同管细胞共享微环境与批次）
    s.rect(96, 194, 608, 62, WHITE, BLUE, 5, rx=12)
    s.text(400, 235, "同一管", 34, BLUE, "middle", "bold")

    # 底层：每管 10,000 个液滴细胞，共 30,000 个观测
    for i, x in enumerate(XS):
        s.arrow(x, 258, x, 288, BLUE, 5, 14)
        s.cluster(x, 338, 46, 30, CYAN, seed=i + 3, rmin=4, rmax=6.5)
        s.text(x, 424, "10,000", 32, CYAN_DEEP, "middle", "bold")

    # 红色（1 处）：观测数 ≠ 有效样本量
    s.bracket(110, 690, 440, 10, RED, 5)
    s.text(400, 494, "30,000 观测  vs  n=3", 34, RED, "middle", "bold")

    s.caption(["同管细胞共享微环境与批次。",
               "有效样本量取决于个体数，不是细胞总数。"], [INK, INK], 30,
              top=524)
    s.save("03_individual_vs_cell_structure.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())

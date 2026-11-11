#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_annotation_three_defenses.py — 生成 13_annotation_three_defenses.svg
（FIG-P02-15：细胞类型注释的三道正交防线）

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-15（Slide 34，cols 一栏，800×700）。
依据：教材 §17.4.7 L173–189、图 17-3。纯示意：无数据、无随机数、无网络。
图内汉字 = 方案指定整句逐字一致（29 汉字）；条目名与图例用简短拉丁标签。
用法：PYTHONDONTWRITEBYTECODE=1 python3 13_annotation_three_defenses.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "两正交特征基因互证，组织学丰度数量级自洽，原位杂交空间成像闭环。"


def badge(s, cx, cy, n, color=BLUE):
    s.circle(cx, cy, 22, color)
    s.text(cx, cy + 12, str(n), 32, WHITE, "middle", "bold")


def main():
    s = SVG(800, 700, "Three orthogonal checks for annotation", plan=TEXT)

    rows = ((60, "2 MARKERS", GREEN), (190, "ABUNDANCE", ORANGE),
            (320, "IN SITU", CYAN_DEEP))
    for i, (y, head, col) in enumerate(rows):
        s.rect(40, y, 720, 108, WHITE, PANEL, 3, rx=12)
        badge(s, 82, y + 54, i + 1, col)
        s.text(122, y + 66, head, 34, col, "start", "bold")

    # ① 两个机制正交的特征基因在同一簇高、其他簇低
    for j, (x, h1, h2) in enumerate(((340, 44, 44), (420, 40, 40))):
        s.rect(x, 84, 56, 60, GREEN_TINT, GREEN, 3, rx=6)
        s.text(x + 28, 156, "G1" if j == 0 else "G2", 30, GREEN, "middle")
    s.check(516, 114, 20, GREEN, 7)

    # ② 组织学比例与聚类丰度数量级一致
    for j, h in enumerate((34, 62, 92)):
        s.rect(360 + j * 52, 288 - h, 40, h, ORANGE)
    s.line(352, 288, 516, 288, INK, 3)
    s.check(548, 244, 20, ORANGE, 7)

    # ③ 原位证据独立定位，与注释互相印证
    s.circle(404, 374, 34, WHITE, CYAN_DEEP, 4)
    s.circle(404, 374, 13, CYAN)
    s.line(452, 374, 512, 374, CYAN_DEEP, 4, dash="9 7")
    s.check(540, 374, 20, CYAN_DEEP, 7)

    # 红色（1 处）：序列同源不等于时空表达守恒
    s.rect(690, 60, 18, 368, RED, None, 0, rx=9)
    s.text(760, 468, "HOMOLOGY ≠ EXPR", 30, RED, "end", "bold")

    s.caption(["两正交特征基因互证，组织学丰度数量级自洽，",
               "原位杂交空间成像闭环。"], [INK, INK], 30, top=500)
    s.save("13_annotation_three_defenses.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())

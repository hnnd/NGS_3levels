#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_bulk_vs_singlecell_dilemma.py — 生成 01_bulk_vs_singlecell_dilemma.svg
（FIG-P02-01：bulk 匀浆平均 vs 单细胞拆开竞争解释）

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-01（Slide 09，cols 一栏，800×700）。
依据：教材 §17.1 L10–18、讲义 ③ 前言。纯示意：无数据、无随机数、无网络。
图内汉字 = 方案指定整句逐字一致（29 汉字）；面板名与图例只用拉丁字母与数字
（04_slides/README「图表标题 / 轴 / 图例用英文」）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 01_bulk_vs_singlecell_dilemma.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "组织匀浆给出平均值。单细胞区分比例变化与表达调控，拆开竞争解释。"
# 图内元素标签的中文译文（D135：说明性短语一律中文；工具名/字段名/数字保留英文）。
EXTRA = "匀浆液滴一条平均曲线比例表达拆开"

def main():
    s = SVG(800, 700, "Bulk average vs single-cell decomposition", plan=TEXT,
            extra=EXTRA)

    # ---------- 左：bulk 匀浆 ----------
    s.rect(36, 56, 336, 444, WHITE, PANEL, 3, rx=14)
    s.text(60, 100, "A  匀浆", 34, BLUE, "start", "bold")

    # 试管（多色细胞混在一起）
    s.path("M 108 130 L 108 250 Q 108 292 202 292 Q 296 292 296 250 L 296 130",
           BLUE, 5, fill=BLUE_TINT)
    s.line(108, 130, 296, 130, BLUE, 5)
    cells = [(136, 176, ORANGE, 17), (180, 164, PURPLE, 15), (224, 182, CYAN, 16),
             (266, 168, GREEN, 14), (146, 226, GREEN, 15), (192, 222, ORANGE, 17),
             (240, 236, PURPLE, 16), (278, 222, CYAN, 15)]
    for cx, cy, col, r in cells:
        s.circle(cx, cy, r, col)

    s.arrow(202, 300, 202, 336, GRAY, 5, 14)

    # 输出：一条平均曲线（比例变化与表达变化叠在同一条线上）
    curve = [(70, 420), (108, 392), (146, 384), (184, 404), (222, 424),
             (260, 396), (298, 388), (336, 414)]
    s.polyline(curve, BLUE, 6)
    s.text(202, 466, "一条平均曲线", 32, GRAY, "middle", "bold")

    # ---------- 右：单细胞拆分 ----------
    s.rect(428, 56, 336, 444, WHITE, PANEL, 3, rx=14)
    s.text(452, 100, "B  液滴", 34, BLUE, "start", "bold")

    # 喷头 + 三个液滴（每滴只装一个细胞）
    s.rect(470, 122, 252, 16, BLUE)
    for cx, col in ((508, ORANGE), (596, GREEN), (684, PURPLE)):
        s.path(f"M {cx} 138 L {cx} 168", BLUE, 3, dash="8 8")
        s.circle(cx, 202, 32, WHITE, BLUE, 4)
        s.circle(cx, 202, 11, col)
        s.arrow(cx, 238, cx, 262, BLUE, 4, 11)

    # 两条并行输出：比例 + 表达
    s.text(470, 288, "比例", 30, GREEN, "start", "bold")
    s.rect(470, 300, 96, 34, GREEN)
    s.rect(566, 300, 40, 34, ORANGE)
    s.rect(606, 300, 24, 34, PURPLE)
    s.rect(470, 300, 160, 34, "none", GREEN, 3)

    s.text(648, 288, "表达", 30, CYAN_DEEP, "start", "bold")
    for i in range(3):
        for j in range(3):
            v = (i * 3 + j) % 4
            s.rect(648 + j * 26, 300 + i * 26, 22, 22,
                   [GREEN_TINT, CYAN, CYAN_DEEP, BLUE][v])

    # 红色警示（1 处）：物理拆开才把两种解释分开（括住两条输出）
    s.path("M 486 386 L 486 374 L 706 374 L 706 386", RED, 5, fill="none")
    s.line(596, 374, 596, 404, RED, 5)
    s.badge(596, 432, "拆开", RED, WHITE, 32, "middle")

    s.caption(["组织匀浆给出平均值。",
               "单细胞区分比例变化与表达调控，拆开竞争解释。"], [INK, INK],
              30, top=520)
    s.save("01_bulk_vs_singlecell_dilemma.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())

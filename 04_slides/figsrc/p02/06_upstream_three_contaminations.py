#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_upstream_three_contaminations.py — 生成 06_upstream_three_contaminations.svg
（FIG-P02-08：上游三种静默污染与各自的假象）

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-08（Slide 22，cols 一栏，800×700）。
依据：教材 §17.4.3 L113–125（环境 RNA／3′ UTR 截断／双联体）。纯示意：
无数据、无随机数、无网络。三条通路各自「起因 → 机制 → 下游假象」。
图内汉字 = 方案指定整句逐字一致（30 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 06_upstream_three_contaminations.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "环境游离全图弥漫，截断丢失末端读段，双联体伪造中间态。流程皆不报警。"


def row(s, cy, left, right, color, icon):
    s.text(44, cy + 11, left, 30, BLUE, "start", "bold")
    s.arrow(248, cy, 300, cy, GRAY, 5, 13)
    icon(s, 360, cy)
    s.arrow(414, cy, 466, cy, GRAY, 5, 13)
    s.text(482, cy + 11, right, 30, color, "start", "bold")


def icon_ambient(s, cx, cy):
    """破损细胞：胞浆外溢成弥漫小点。"""
    s.path(f"M {cx - 26} {cy - 24} A 30 30 0 1 1 {cx + 20} {cy + 26}",
           BLUE, 5, fill=BLUE_TINT)
    for dx, dy in ((-34, -44), (12, -48), (44, -8), (-46, 30)):
        s.circle(cx + dx, cy + dy, 5, ORANGE)


def icon_truncated(s, cx, cy):
    """读段 3′ 端被截：实体部分 + 灰虚线残端。"""
    s.rect(cx - 44, cy - 13, 62, 26, CYAN, CYAN, 2, rx=4)
    s.rect(cx + 18, cy - 13, 26, 26, "none", GRAY, 3, rx=4, dash="7 7")


def icon_doublet(s, cx, cy):
    """一个液滴封进两个异质细胞。"""
    s.circle(cx, cy, 34, WHITE, BLUE, 4)
    s.circle(cx - 11, cy - 7, 11, ORANGE)
    s.circle(cx + 11, cy + 8, 11, PURPLE)


def main():
    s = SVG(800, 700, "Three silent upstream contaminations", plan=TEXT)

    # 红色（1 处）：流程正常退出，数据已被污染
    s.rect(40, 60, 720, 50, RED, None, 3, rx=10)
    s.text(400, 95, "EXIT 0 · NO ERROR", 32, WHITE, "middle", "bold")

    for cy, sep in ((190, 248), (305, 363), (420, 478)):
        s.line(40, sep, 760, sep, PANEL, 3, dash="10 10")

    row(s, 190, "AMBIENT RNA", "DIFFUSE", ORANGE, icon_ambient)
    row(s, 305, "TRUNCATED 3'", "FEW GENES", ORANGE, icon_truncated)
    row(s, 420, "DOUBLET", "FAKE MIDDLE", PURPLE, icon_doublet)

    s.caption(["环境游离全图弥漫，截断丢失末端读段，",
               "双联体伪造中间态。流程皆不报警。"], [INK, INK], 30, top=524)
    s.save("06_upstream_three_contaminations.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())

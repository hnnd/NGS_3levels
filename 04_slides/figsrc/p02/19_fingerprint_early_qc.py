#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_fingerprint_early_qc.py — 生成 19_fingerprint_early_qc.svg
（FIG-P02-23：早期质控与上游异常的三枚指纹）

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-23（Slide 55，cols 一栏，800×700）。
依据：教材 §17.4.3 L113–125、§17.5.2 L306–313、讲义 ⑥ 6.2。纯示意：
波形与图形为示意，无数据、无随机数、无网络。
图内汉字 = 方案指定整句逐字一致（30 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 19_fingerprint_early_qc.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "前缀失配指标全零，三端截断基因骤降，游离污染粗桥连簇。查行名与背景。"
CARDS = ((40, "ZERO", BLUE), (290, "DROP", ORANGE), (540, "BRIDGE", CYAN_DEEP))


def main():
    s = SVG(800, 700, "Early QC fingerprints", plan=TEXT)

    for x, head, col in CARDS:
        s.rect(x, 56, 220, 400, WHITE, PANEL, 3, rx=14)
        s.text(x + 110, 104, head, 32, col, "middle", "bold")

    # 指纹一：percent.mt 整列贴地全零（红色箭头，唯一警示区）
    s.line(62, 316, 238, 316, PANEL, 3, dash="8 8")
    s.line(62, 306, 238, 306, BLUE, 6)
    s.text(150, 376, "mt = 0", 32, BLUE, "middle", "bold")
    s.arrow(196, 222, 168, 292, RED, 5, 14)

    # 指纹二：3′ UTR 截断，nFeature 中位数骤降
    for j, h in enumerate((110, 96, 84)):
        s.rect(312 + j * 52, 330 - h, 36, h, ORANGE)
    s.line(304, 330, 500, 330, INK, 3)
    s.arrow(470, 158, 470, 200, ORANGE, 5, 14)
    s.text(400, 376, "genes ↓", 30, ORANGE, "middle", "bold")

    # 指纹三：环境 RNA 在簇间拉出粗大的游离桥
    for cx, cy in ((596, 168), (662, 212), (592, 256)):
        s.cluster(cx, cy, 24, 14, CYAN, seed=cx, rmin=3, rmax=5)
    s.polyline([(612, 190), (644, 204), (662, 212), (646, 234), (616, 248)],
               CYAN_DEEP, 12)
    s.text(650, 376, "bridge", 30, CYAN_DEEP, "middle", "bold")

    s.caption(["前缀失配指标全零，三端截断基因骤降，",
               "游离污染粗桥连簇。查行名与背景。"], [INK, INK], 30, top=500)
    s.save("19_fingerprint_early_qc.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())

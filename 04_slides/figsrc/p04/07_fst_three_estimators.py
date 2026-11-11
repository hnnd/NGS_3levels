#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_fst_three_estimators.py — 生成 07_fst_three_estimators.svg
（FIG-P04-07：第 20 页 cols 一栏「F_ST 三估计量内核与适用场景」）【new-svg】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-07（P20，cols，800×700）。
依据：教材 §20.4.2 的估计量表——Nei's G_ST 是频率方差比、未校正抽样方差，
小样本系统性高估；Weir & Cockerham 1984 是方差分量的无偏估计，也是
`vcftools --weir-fst-pop` 的内核；Hudson（Bhatia 2013）用 π 与 d_XY 构造比值，
亚群样本量不均衡时最稳健。三者同一批数据不给同一个数，跨文献先核内核与阈值。
图内中文严格取方案给定 29 字（4 句，逐句按 5–6 字折成两行放入卡片）；
G_ST / F_ST / W&C / Hudson 与数字属符号。
结构＝三张并列卡片（内核名 + 一句判读 + 一个小内核示意）＋底部一条核对提醒。
红只标 Nei 的小样本偏高一处，绿标两个「可信」内核。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 07_fst_three_estimators.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["频率方差比小样偏高", "方差分量内核无偏", "比值对不均稳健", "先核对内核"]
TEXT = "".join(PHRASES)

CARDS = [
    (32, "Nei G_ST", ORANGE, ORANGE_TINT, ("频率方差比", "小样偏高"), RED),
    (282, "W&C", BLUE, BLUE_TINT, ("方差分量内核", "无偏"), GREEN),
    (532, "Hudson", CYAN_DEEP, CYAN_TINT, ("比值对不均", "稳健"), GREEN),
]


def variance_icon(s, x, y, color, mode):
    """内核示意：方差比（左）、方差分量（中）、比值（右）。"""
    if mode == 0:                                    # 频率方差比：两峰 + 总方差
        s.line(x, y + 26, x + 150, y + 26, color, 4)
        for cx in (x + 40, x + 110):
            s.path(f"M {cx - 26} {y + 26} Q {cx} {y - 22} {cx + 26} {y + 26}",
                   color, 4)
    elif mode == 1:                                  # 方差分量：均方期望分解
        s.line(x, y + 26, x + 150, y + 26, color, 4)
        s.rect(x + 10, y + 2, 34, 24, "none", color, 4, rx=4)
        s.rect(x + 58, y + 2, 34, 24, "none", color, 4, rx=4)
        s.rect(x + 106, y + 2, 34, 24, "none", color, 4, rx=4)
    else:                                            # 比值：π 与 d_XY 两条线段之比
        s.line(x + 6, y + 22, x + 144, y + 22, color, 5)
        s.line(x + 6, y - 6, x + 96, y - 6, color, 5, dash="10 7")
        s.circle(x + 6, y + 22, 7, color)
        s.circle(x + 96, y - 6, 7, color)


def main():
    s = SVG(800, 700, "Three F_ST estimators, three kernels", plan=TEXT)

    for x, head, color, tint, lines, lcol in CARDS:
        s.rect(x, 56, 236, 470, tint, color, 4, rx=14)
        s.text(x + 118, 118, head, 34, color, "middle", "bold")
        s.line(x + 24, 140, x + 212, 140, PANEL, 3)
        variance_icon(s, x + 43, 232, color, CARDS.index((x, head, color, tint,
                                                          lines, lcol)))
        s.text(x + 118, 356, lines[0], 30, lcol, "middle", "bold")
        s.text(x + 118, 402, lines[1], 30, lcol, "middle", "bold")

    s.band(120, 576, 560, 78, PHRASES[3], BLUE, WHITE, 32)

    s.save("07_fst_three_estimators.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())

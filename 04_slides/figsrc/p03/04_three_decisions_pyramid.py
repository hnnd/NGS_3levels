#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_three_decisions_pyramid.py — 生成 04_three_decisions_pyramid.svg
（FIG-P03-04：第 15 页 cols 一栏「测序前三决策金字塔」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-04（P15，cols，800×700）。
依据：教材 §16.4.1 L77–80（结论上限在采样与建库那一刻被物理锁定，后面每一种算法
都只在这个上限之内工作）、§16.4.1.3 L129–134（对照完备性决定可识别性）。
图内中文严格取方案给定 27 字（4 句）。结构＝三层台阶金字塔：底层「深度倒推」
（基石，深蓝）→ 中层「建库兼容」（通道，青蓝）→ 顶层「对照」（边界，紫）；
底部红色横条 + 锁图标＝上限在测序前已被锁定。
配色：深蓝/青蓝/紫三层，红色只作「前置锁定上限」一处警示。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 04_three_decisions_pyramid.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["深度倒推算预算", "建库兼容保物种", "对照决定可问性", "前置锁定上限"]
TEXT = "".join(PHRASES)
# 自上而下：(上边宽, 下边宽, 主色, 淡色, 中文句)。顶层最窄、底层最宽。
LAYERS = [(300, 410, PURPLE, PURPLE_TINT, PHRASES[2]),
          (410, 510, CYAN, CYAN_TINT, PHRASES[1]),
          (510, 620, BLUE, BLUE_TINT, PHRASES[0])]


def main():
    s = SVG(800, 700, "Three decisions fixed before sequencing", plan=TEXT)

    # ---------- 三层台阶金字塔：自下而上收窄 ----------
    cx, h, gap = 400, 116, 6
    y_bottom = 84
    for i, (w_top, w_bot, main, tint, phrase) in enumerate(LAYERS):
        y = y_bottom + i * (h + gap)
        s.wedge(cx, y, w_top, w_bot, h, tint, main, 4)
        s.text(cx, y + h / 2 + 11, phrase, 30, main, "middle", "bold")

    # ---------- 底部：红线锁定的上限（唯一红色警示）----------
    s.rect(120, 500, 560, 2, GRAY, None, 0)
    s.lock(148, 592, 26, RED)
    s.text(190, 604, PHRASES[3], 32, RED, "start", "bold")
    s.path("M 148 560 L 148 520", RED, 4, dash="8 7")
    s.save("04_three_decisions_pyramid.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())

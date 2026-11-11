#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""30_failure_road_signs.py — FIG-M06-30 四大失效诊断路标

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-30（P54，cols 一栏
800×700，new-svg）。
教材依据：§18.5.1–18.5.6（结果不对时先在 track 表定位哪一列掉读段，再按四类病因排查）。
图内汉字 = 方案原句逐字，共 24 字（过滤塌查超长 / 合并塌查重叠 / 曲线散查批次 /
全缺失查引物）；其余标注为 track 表字段名与序号。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 30_failure_road_signs.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403
from svghelp import (BLUE, BLUE_TINT, GRAY, GREEN, INK, ORANGE, ORANGE_TINT,
                     RED, RED_TINT, SVG, WHITE)

ROWS = [("过滤塌查超长", "filtered", True),
        ("合并塌查重叠", "merged", False),
        ("曲线散查批次", "err_F.pdf", False),
        ("全缺失查引物", "taxonomy", False)]


def main():
    s = SVG(800, 700)
    YS = [150, 282, 414, 546]
    SPINE = 62

    # 路标主轴（深蓝）
    s.line(SPINE, YS[0] - 34, SPINE, YS[-1] + 40, BLUE, 5, cap="round")

    for i, (phrase, field, warn) in enumerate(ROWS):
        y = YS[i]
        # 序号牌（橙：诊断分支）
        s.circle(SPINE, y - 74, 25, ORANGE_TINT, ORANGE, 4)
        s.text(SPINE, y - 74 + 11, str(i + 1), 30, ORANGE_DEEP, "middle", "bold")

        # 路标牌
        if warn:
            s.rect(104, y - 33, 356, 66, RED_TINT, RED, 5, rx=12)
            ink = RED
        else:
            s.rect(104, y - 33, 356, 66, BLUE_TINT, BLUE, 5, rx=12)
            ink = BLUE
        s.text(282, y + 11, phrase, 32, ink, "middle", "bold")

        # 指向该列（绿：处置去向）
        s.arrow(478, y, 556, y, GREEN, 5, head=16)
        s.chip(664, y, field, 30, WHITE, GREEN, GREEN, sw=3)

    s.save("30_failure_road_signs.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_dplyr_verbs.py — 生成 07_dplyr_verbs.svg
（FIG-U02-07：五个 dplyr 动词各管一件事）

方案：reviews/course/U02_FIGP_001.md §4 FIG-U02-07（P25，cols 一栏，viewBox 800×700）。
数据：无数字。五动词依据教材 §3.4.3 L151；「每步核对行数」依据 §3.4.3 L160。
图内只出现 R 管道符（|>），与 shell 的 | 区分（§3.4.3 L151）。
红 1 处＝「每步核对行数」横幅。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 07_dplyr_verbs.py
"""
from svghelp import *  # noqa: F401,F403

VERBS = [
    ("filter()", "筛行"),
    ("mutate()", "增改列"),
    ("arrange()", "排序"),
    ("select()", "挑列"),
    ("group_by() + summarise()", "分组汇总"),
]


def main():
    s = SVG(800, 700)
    s.line(80, 70, 80, 490, CYAN, 8)
    for i, (code, role) in enumerate(VERBS):
        y = 60 + i * 88
        s.rect(140, y, 620, 72, BLUE, rx=12)
        s.text(170, y + 47, code, 32, WHITE, "start", "bold")
        s.text(730, y + 47, role, 32, ORANGE, "end", "bold")
        s.circle(80, y + 36, 9, WHITE, CYAN_DEEP, 4)
    s.text(70, 300, "%>%", 30, CYAN_DEEP, "end", "bold")
    s.text(70, 348, "|>", 30, CYAN_DEEP, "end", "bold")
    s.rect(140, 570, 620, 80, RED, rx=14)
    s.text(450, 623, "每步核对行数", 40, WHITE, "middle", "bold")
    s.save("07_dplyr_verbs.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_depth_denominators.py — 生成 13_depth_denominators.svg（FIG-U05-13：-a 与 -aa 分母）

方案：reviews/course/U05_FIGP_001.md §4 FIG-U05-13（P46，cols 一栏，viewBox 800×700）。
两条 contig（各 200 bp）：ctg1 半覆盖（绿 100 bp）、ctg2 全零（完全未使用）；
算式卡 depth -a → 100/200 = 0.5（橙，易错）vs depth -aa → 100/400 = 0.25（绿）；
红点＝空 contig 被删出分母。数字＝教材 §7.4.6 L254 设例（正文算术，手算可复核；
「本机实测，非课程 pin」口径由 deck 页面 ref 承载）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 13_depth_denominators.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    # 数据自检（教材 §7.4.6 L254 正文算术）
    assert 100 / 200 == 0.5 and 100 / 400 == 0.25
    print("check: 100/200=0.5（-a）；100/400=0.25（-aa）")

    s = SVG(800, 700)

    # 两条 contig 条带
    s.text(60, 76, "ctg1", 30, BLUE, "start", "bold")
    s.rect(60, 90, 480, 44, WHITE, BLUE, 4, rx=8)
    s.rect(60, 90, 240, 44, GREEN, rx=8)
    s.text(180, 120, "100 bp", 30, WHITE, "middle", "bold")
    s.rect(300, 90, 240, 44, PANEL, rx=8)

    s.text(60, 176, "ctg2", 30, BLUE, "start", "bold")
    s.rect(60, 190, 480, 44, PANEL, BLUE, 4, rx=8)
    s.text(580, 218, "完全未使用", 30, INK, "start", "bold")
    s.text(580, 118, "均值被抬高", 30, INK, "start", "bold")

    # 算式卡 A：depth -a（橙，易错）
    s.rect(60, 320, 320, 150, WHITE, ORANGE, 5, rx=14)
    s.text(90, 368, "depth -a", 32, ORANGE, "start", "bold")
    s.text(90, 408, "200 rows", 30, GRAY, "start", "bold")
    s.text(90, 446, "100 / 200 = 0.5", 30, INK, "start", "bold")
    s.circle(372, 328, 9, RED)
    s.line(372, 340, 372, 470, RED, 4, dash="8 8")

    # 算式卡 B：depth -aa（绿）
    s.rect(420, 320, 320, 150, WHITE, GREEN, 5, rx=14)
    s.text(450, 368, "depth -aa", 32, GREEN, "start", "bold")
    s.text(450, 408, "400 rows", 30, GRAY, "start", "bold")
    s.text(450, 446, "100 / 400 = 0.25", 30, INK, "start", "bold")

    # 红点注记（唯一红）
    s.text(220, 512, "空 contig 被删出分母", 30, INK, "middle", "bold")

    s.save("13_depth_denominators.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

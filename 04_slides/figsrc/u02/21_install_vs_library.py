#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""21_install_vs_library.py — 生成 21_install_vs_library.svg
（FIG-U02-21：装了 ≠ 加载了）

方案：reviews/course/U02_FIGP_001.md §4 FIG-U02-21（P63，cols 一栏，viewBox 800×700）。
数据：无数字。依据：教材 §3.4.6 L205（装了不等于加载了）、§2.5.3
（第 2 章 conda 管装一次，library() 管当前会话）。报错形态留 deck 页面文字。
红 1 处＝口诀。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 21_install_vs_library.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    s.rect(150, 70, 500, 150, WHITE, CYAN_DEEP, 5, rx=14)
    s.text(400, 160, "会话", 44, CYAN_DEEP, "middle", "bold")

    s.rect(150, 430, 500, 210, WHITE, BLUE, 5, rx=14)
    s.text(400, 488, "环境（conda）", 38, BLUE, "middle", "bold")
    for x in (215, 330, 445):
        s.rect(x, 512, 90, 90, ORANGE, rx=10)

    s.arrow(64, 384, 200, 504, ORANGE, 7)
    s.text(60, 364, "装：一次", 32, ORANGE, "start", "bold")

    s.arrow(230, 424, 230, 230, CYAN, 6)
    s.arrow(575, 230, 575, 424, CYAN, 6)
    s.text(390, 334, "加载：每个会话", 32, CYAN_DEEP, "middle", "bold")

    s.text(385, 396, "装了不等于加载了", 38, RED, "middle", "bold")
    s.save("21_install_vs_library.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""22_quality_diagnosis.py — 生成 22_quality_diagnosis.svg（FIG-U03-22：质量异常三形态）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-22（P58，cols 一栏，800×700）。
教材依据：chapters/ch04/manuscript.qmd §4.5.1、§4.5.2。
三栏诊断：① 3′ 端单调衰减（正常，可修剪）② 中段塌陷（气泡/试剂事故）
③ 同聚物区错误率不随深度降（系统偏差，多数票无效）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 22_quality_diagnosis.py
"""
from svghelp import *  # noqa: F401,F403


def panel(s, x, col):
    s.rect(x, 140, 230, 420, WHITE, PANEL, 3, rx=14)
    s.line(x + 30, 200, x + 30, 500, GRAY, 3)
    s.line(x + 30, 500, x + 205, 500, GRAY, 3)


def main():
    s = SVG(800, 700)
    s.text(400, 50, "末端衰减正常修剪", 36, BLUE, "middle", "bold")
    s.text(400, 92, "中段塌陷气泡故障，同聚偏差无效", 30, GRAY, "middle",
           "bold")

    # 栏 ①：3′ 端单调衰减（绿，正常）
    panel(s, 40, GREEN)
    pts = [(70 + i * 16, 230 + (i * 18) ** 1.35 / 22 + i * 2) for i in range(11)]
    s.curve(pts, GREEN, 7)
    s.text(155, 600, "可修剪", 30, GREEN, "middle", "bold")

    # 栏 ②：中段局部塌陷（红，气泡/试剂事故）
    panel(s, 285, RED)
    pts = [(315 + i * 16, 240 + i * 8) for i in range(5)]
    pts += [(395, 430), (411, 470), (427, 380)]
    pts += [(443 + i * 16, 330 + i * 9) for i in range(5)]
    s.curve(pts, RED, 7)
    s.text(400, 600, "气泡", 30, RED, "middle", "bold")

    # 栏 ③：同聚物高深度错（红，系统偏差）
    panel(s, 530, RED)
    s.line(560, 300, 710, 300, RED, 7)
    for i in range(6):
        s.circle(570 + i * 26, 300, 7, RED)
    s.text(620, 270, "AAAA", 28, RED, "middle", "bold")
    s.text(645, 600, "无效", 30, RED, "middle", "bold")

    s.save("22_quality_diagnosis.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

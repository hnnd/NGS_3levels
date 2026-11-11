#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_biological_vs_technical_replicate.py — 生成 07_biological_vs_technical_replicate.svg
（FIG-M01-09：生物学重复 vs 技术重复判别树）

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-09（P23，cols 一栏，800×700）。
依据：教材 §13.4.2 L106–122, L141；讲义 ④4.4、⑤5.1。无数字、无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 07_biological_vs_technical_replicate.py
"""
from svghelp import *  # noqa: F401,F403


def plant(s, cx, cy, color):
    s.line(cx, cy + 22, cx, cy, color, 5)
    s.circle(cx, cy - 12, 12, color)


def tube(s, cx, cy, color):
    s.rect(cx - 10, cy - 22, 20, 44, "none", color, 5, rx=6)


def main():
    s = SVG(800, 700)

    # 顶部提问徽章
    s.rect(130, 56, 540, 84, BLUE, rx=16)
    s.text(400, 112, "换掉它，另一个会变吗？", 36, WHITE, "middle", "bold")
    s.arrow(280, 140, 220, 202, BLUE, 6)
    s.arrow(520, 140, 580, 202, BLUE, 6)

    # 左分支：不会变 → 独立个体（绿）
    s.rect(60, 208, 320, 200, GREEN_TINT, GREEN, 5, rx=16)
    s.text(220, 262, "不会：", 34, GREEN, "middle", "bold")
    plant(s, 130, 330, GREEN)
    plant(s, 220, 330, GREEN)
    plant(s, 310, 330, GREEN)
    s.text(220, 392, "独立个体，", 30, INK, "middle", "bold")
    s.text(298, 392, "进 n", 30, GREEN, "start", "bold")

    # 右分支：会变 → 技术重复（橙底；「不进 n」为全图唯一红色）
    s.rect(420, 208, 320, 200, ORANGE_TINT, ORANGE, 5, rx=16)
    s.text(580, 262, "会变：", 34, INK, "middle", "bold")
    tube(s, 540, 330, ORANGE)
    tube(s, 580, 330, ORANGE)
    tube(s, 620, 330, ORANGE)
    s.text(560, 392, "技术重复，", 30, INK, "middle", "bold")
    s.text(643, 392, "不进 n", 30, RED, "start", "bold")

    # 底部附注：先查层级
    s.rect(130, 460, 540, 84, BLUE, rx=16)
    s.text(400, 514, "先查层级", 34, WHITE, "middle", "bold")
    s.text(400, 586, "check run → experiment → biosample", 30, GRAY,
           "middle")

    s.save("07_biological_vs_technical_replicate.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

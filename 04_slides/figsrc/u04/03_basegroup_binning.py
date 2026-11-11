#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""03_basegroup_binning.py — 生成 03_basegroup_binning.svg（FIG-U04-03：BaseGroup 分组）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-03（P15，cols 一栏，viewBox 800×700）。
标尺：1–9 位青蓝单碱基格、10–99 位深蓝每 2 位一组、第 100 位橙；
大括号「100 bp 共 55 组」；右侧向下箭头「组内平均后再判」。
数据来源：demos/ch06_perbase_quality.py Part A（base_groups：9 + 45 + 1 = 55）。
依据：教材 §6.4.2 L70–74。图内汉字 19，红色 0 处。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 03_basegroup_binning.py
"""
from svghelp import *


def main():
    s = SVG(800, 700)
    X0, PX = 60, 6.8          # 标尺起点、每 bp 像素
    YT, HB = 420, 60          # 标尺顶、格高

    # 1–9 位：单碱基青蓝格
    for bp in range(1, 10):
        s.rect(X0 + (bp - 1) * PX, YT, PX - 0.8, HB, CYAN)
    # 10–99 位：每 2 位一组，深蓝格
    x = X0 + 9 * PX
    for g in range(45):
        s.rect(x + g * 2 * PX, YT, 2 * PX - 0.8, HB, BLUE)
    # 第 100 位：橙
    s.rect(X0 + 99 * PX, YT, PX - 0.8, HB, ORANGE)
    # 基线
    s.line(X0 - 6, YT + HB + 4, X0 + 100 * PX + 6, YT + HB + 4, INK, sw=4)

    # 大括号与总数
    xe = X0 + 100 * PX
    s.path(f"M {X0} 356 C {X0} 336 {xe} 336 {xe} 356", INK, sw=4)
    s.line(X0, 356, X0, 372, INK, sw=4)
    s.line(xe, 356, xe, 372, INK, sw=4)
    s.text(400, 316, "100 bp 共 55 组", 32, INK, "middle", "bold")

    s.text(150, 262, "1–9 位独立成组", 30, CYAN_DEEP, "middle", "bold")
    s.text(430, 262, "10–99 位每 2 位一组", 30, BLUE, "middle", "bold")

    # 右侧向下箭头 → 组内平均
    s.arrow(xe - 4, YT + 30, 682, 566, BLUE, sw=6)
    s.rect(560, 580, 232, 60, BLUE, rx=12)
    s.text(676, 621, "组内平均后再判", 30, WHITE, "middle", "bold")

    s.save("03_basegroup_binning.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

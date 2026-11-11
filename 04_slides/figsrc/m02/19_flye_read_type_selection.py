#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_flye_read_type_selection.py — 19_flye_read_type_selection.svg
（FIG-M02-25，P48，cols）：Flye 读长类型三分支选型【new-svg】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-25。
依据：讲义 ⑤ 5.3、⑨ 9.4；脚本 02_assembly_pipeline.sh L30。无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 19_flye_read_type_selection.py
"""
from svghelp import (BLUE, CYAN, GRAY, GREEN, INK, PURPLE, RED, SVG, WHITE)


def main():
    s = SVG(800, 700)
    s.text(790, 44, "lecture ⑤ 5.3 (schematic)", 30, GRAY, "end")

    # 中心输入框
    s.rect(280, 70, 240, 84, BLUE, rx=16)
    s.text(400, 124, "长读长数据", 36, WHITE, "middle", "bold")

    branches = [
        (30, GREEN, "主线 MinION", "选 --nano-raw", True),
        (285, CYAN, "HiFi", "选 --pacbio-hifi", False),
        (540, PURPLE, "高精度 ONT", "选 --nano-hq", False),
    ]
    for x, color, l1, l2, main_line in branches:
        sw = 8 if main_line else 5
        s.arrow(400, 158, x + 115, 268, color, sw)
        s.rect(x, 272, 230, 150, WHITE, color, sw, rx=16)
        s.text(x + 115, 340, l1, 32, INK, "middle", "bold")
        s.text(x + 115, 392, l2, 30, color, "middle", "bold")

    # 底部红色警告
    s.rect(200, 596, 400, 64, RED, rx=14)
    s.text(400, 640, "参数错配致组装失败", 34, WHITE, "middle", "bold")

    s.save("19_flye_read_type_selection.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

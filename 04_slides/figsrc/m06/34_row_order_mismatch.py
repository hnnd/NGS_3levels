#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""34_row_order_mismatch.py — FIG-M06-34 距离矩阵与元数据行序错配静默失真

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-34（P58，cols 一栏
800×700，new-svg）。
教材依据：§18.5.6（距离矩阵与元数据行序错配不会报错，只会把标签静默洗乱，
统计照样跑出「显著」；跑检验前必须先比对行名）。
图内汉字 = 方案原句逐字，共 22 字（行名错位静默配错 / 统计假显著无报错 /
必须比对行名）；其余标注为样本行名、表名字段与核验代码。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 34_row_order_mismatch.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403
from svghelp import (BLUE, BLUE_TINT, CYAN, CYAN_DEEP, CYAN_TINT, GRAY, GREEN,
                     GREEN_TINT, INK, RED, SVG, WHITE)

N = 5
SAMPLES = [f"s{i:02d}" for i in range(1, N + 1)]
LEFT_X, RIGHT_X, PANEL_W = 96, 470, 236
ROW_H, PITCH, TOP = 44, 56, 152


def main():
    s = SVG(800, 700)

    # 左：距离矩阵 d（行名 s01..s05）
    s.text(LEFT_X + PANEL_W / 2, 118, "d", 32, BLUE, "middle", "bold")
    s.rect(LEFT_X, TOP - 12, PANEL_W, N * PITCH + 12, WHITE, BLUE, 4, rx=14)
    for i, smp in enumerate(SAMPLES):
        y = TOP + i * PITCH
        s.rect(LEFT_X + 14, y, PANEL_W - 28, ROW_H, BLUE_TINT, rx=8)
        s.text(LEFT_X + 30, y + 30, smp, 30, CYAN_DEEP, "start", "bold")

    # 右：元数据 meta（行序倒置 s05..s01）
    s.text(RIGHT_X + PANEL_W / 2, 118, "meta", 32, BLUE, "middle", "bold")
    s.rect(RIGHT_X, TOP - 12, PANEL_W, N * PITCH + 12, WHITE, BLUE, 4, rx=14)
    for i, smp in enumerate(SAMPLES[::-1]):
        y = TOP + i * PITCH
        s.rect(RIGHT_X + 14, y, PANEL_W - 28, ROW_H, CYAN_TINT, rx=8)
        s.text(RIGHT_X + 30, y + 30, smp, 30, CYAN_DEEP, "start", "bold")

    # 红色交叉连接：左第 i 行 ↔ 右第 (N-1-i) 行（单条 path，一处红）
    d = ""
    for i in range(N):
        lx = LEFT_X + PANEL_W - 6
        ly = TOP + i * PITCH + ROW_H / 2
        rx = RIGHT_X + 6
        ry = TOP + (N - 1 - i) * PITCH + ROW_H / 2
        d += f"M {lx} {ly} L {rx} {ry} "
    s.path(d, RED, 4, dash="9 7")

    # 红：结论（方案原句整句一行，红只用这一处 + 交叉线）
    s.text(400, 506, "行名错位静默配错 统计假显著无报错", 30, RED, "middle",
           "bold")

    # 绿：核验动作
    s.rect(212, 548, 376, 60, GREEN_TINT, GREEN, 4, rx=14)
    s.text(400, 588, "必须比对行名", 32, GREEN, "middle", "bold")
    s.text(400, 658, "all(rownames(d) == meta$sample)", 30, GRAY, "middle")

    s.save("34_row_order_mismatch.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

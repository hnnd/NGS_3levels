#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_adapter_content_curve.py — 生成 08_adapter_content_curve.svg
（FIG-U04-08：Adapter Content 累积曲线读法【算法/判读】）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-08（P22，cols 一栏，viewBox 800×700）。
S 型累积曲线（深蓝）：抬升点 = 测穿起始（橙），终点高度 = 带接头占比；
底部红条「不能直读为片段分布」——显式否定旧口径（W12）。
依据：教材 §6.4.4 L118–122。图内汉字 24，红色 1 处。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 08_adapter_content_curve.py
"""
from svghelp import *


def main():
    s = SVG(800, 700)
    X0, X1, Y0, Y1 = 100, 740, 90, 560    # 绘图区（Y0=100%，Y1=0%）
    PMAX = 160                             # 横轴 0–160 bp

    def gx(p):
        return X0 + p * (X1 - X0) / PMAX

    def gy(f):
        return Y1 - f * (Y1 - Y0)

    # 轴与刻度
    s.line(X0, Y0, X0, Y1, INK, sw=4)
    s.line(X0, Y1, X1, Y1, INK, sw=4)
    for p in (0, 50, 100, 150):
        s.text(gx(p), Y1 + 42, str(p), 30, GRAY, "middle")
    for f in (0.0, 0.5, 1.0):
        s.text(X0 - 12, gy(f) + 10, f"{f:.1f}", 30, GRAY, "end")
    s.text_rot(40, (Y0 + Y1) / 2, "Cumulative adapter", -90)

    # 累积曲线：120 bp 前为 0，120–150 线性抬升，之后持平
    s.path(f"M {gx(0)} {gy(0)} L {gx(120)} {gy(0)} "
           f"C {gx(132)} {gy(0)} {gx(138)} {gy(0.75)} {gx(150)} {gy(1.0)} "
           f"L {gx(160)} {gy(1.0)}", BLUE, sw=6)

    # 抬升点（橙）与终点高度（橙）
    s.circle(gx(120), gy(0.02), 12, ORANGE_DEEP)
    s.text(345, 470, "抬升点：测穿起始", 30, ORANGE_DEEP, "middle", "bold")
    s.line(390, 462, gx(120) - 10, gy(0.02) - 6, ORANGE_DEEP, sw=4)
    s.text(560, 140, "高度：带接头占比", 30, ORANGE_DEEP, "middle", "bold")
    s.line(648, 150, gx(150) - 6, gy(0.97), ORANGE_DEEP, sw=4)

    # 底部红条（唯一红色处）
    s.rect(100, 606, 660, 64, RED_TINT, rx=12)
    s.text(430, 649, "不能直读为片段分布", 32, RED, "middle", "bold")

    s.save("08_adapter_content_curve.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

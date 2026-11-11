#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_annotation_troubleshooting_flow.py — 生成 18_annotation_troubleshooting_flow.svg（FIG-U07-18：注释异常现象排查树）

方案：reviews/course/U07_FIGP_001.md §4.2 FIG-U07-18（P56，cols 一栏，viewBox 800×700）。
数据：无量字数字。偏多查短序列 / 偏少查断裂塌缩 / 假定高查类群移码；
总原则先查输入后查生物（教材 §9.4.5 L240–248、§9.5.1、§9.6）。
入口标签「注释质检结果偏离预期」超出方案汉字清单（29+10>30），入口用 QC 英文。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 18_annotation_troubleshooting_flow.py
"""
from svghelp import *  # noqa: F401,F403

BRANCHES = [
    (15, 265, CYAN_DEEP, "偏多查短序列", "CDS high"),
    (275, 525, PURPLE, "偏少查断裂塌缩", "CDS low · rRNA~0"),
    (535, 785, BLUE, "假定高查类群移码", "hypo high"),
]


def main():
    s = SVG(800, 700)

    # 顶部入口（QC 质检结果节点）
    s.rect(300, 50, 200, 70, BLUE, rx=12)
    s.text(400, 96, "QC", 36, WHITE, "middle", "bold")
    s.arrow(400, 124, 400, 162, GRAY, 6)

    # 分流
    s.line(140, 176, 660, 176, GRAY, 5)
    for x0, x1, color, name, hint in BRANCHES:
        cx = (x0 + x1) / 2
        s.line(cx, 176, cx, 208, GRAY, 5)
        s.rect(x0, 208, x1 - x0, 118, WHITE, color, 6, rx=14)
        s.text(cx, 272, name, 30, color, "middle", "bold")
        s.text(cx, 374, hint, 30, GRAY, "middle")

    # 底部红色总原则条（唯一红色）
    s.rect(190, 470, 420, 60, RED, rx=12)
    s.text(400, 512, "先查输入后查生物", 34, WHITE, "middle", "bold")

    s.save("18_annotation_troubleshooting_flow.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

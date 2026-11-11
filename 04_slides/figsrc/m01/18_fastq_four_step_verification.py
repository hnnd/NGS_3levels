#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_fastq_four_step_verification.py — 生成 18_fastq_four_step_verification.svg
（FIG-M01-21：FASTQ 验收四道防线流程）

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-21（P50，cols 一栏，800×700）。
依据：教材 §13.4.6 L303–313（四步验收判据）；讲义 ⑤5.4。无数字、无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 18_fastq_four_step_verification.py
"""
from svghelp import *  # noqa: F401,F403

STEPS = [
    (50, 470, "① MD5", "字节匹配"),
    (230, 374, "② 片段数", "除以 4"),
    (410, 278, "③ 双端", "行数对齐"),
    (590, 182, "④ 读长", "碱基对账"),
]


def shield(s, cx, cy, r, color):
    pts = [(cx, cy - r), (cx + r * 0.85, cy - r * 0.45),
           (cx + r * 0.7, cy + r * 0.4), (cx, cy + r),
           (cx - r * 0.7, cy + r * 0.4), (cx - r * 0.85, cy - r * 0.45)]
    s.polygon(pts, color)


def main():
    s = SVG(800, 700)

    for x, y, l1, l2 in STEPS:
        s.rect(x, y, 170, 96, BLUE_TINT, BLUE, 4, rx=14)
        s.text(x + 85, y + 42, l1, 30, INK, "middle", "bold")
        s.text(x + 85, y + 80, l2, 30, INK, "middle", "bold")
        shield(s, x + 20, y - 6, 16, GREEN)

    # 递进箭头
    s.arrow(140, 462, 224, 416, CYAN, 7)
    s.arrow(320, 366, 404, 320, CYAN, 7)
    s.arrow(500, 270, 584, 224, CYAN, 7)

    # 底部红色警示（全图唯一红色）
    s.rect(170, 600, 460, 64, RED, rx=14)
    s.text(400, 644, "缺一不可", 36, WHITE, "middle", "bold")

    s.save("18_fastq_four_step_verification.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

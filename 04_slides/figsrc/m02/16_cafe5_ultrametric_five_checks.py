#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_cafe5_ultrametric_five_checks.py — 16_cafe5_ultrametric_five_checks.svg
（FIG-M02-21，P41，cols）：CAFE5 超度量树五步自检防线【new-svg】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-21。
依据：教材 §11.4.6、§11.5.4；讲义 ⑨ 9.3。无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 16_cafe5_ultrametric_five_checks.py
"""
from svghelp import (BLUE, GREEN, GRAY, INK, RED, SVG, WHITE)


def main():
    s = SVG(800, 700)

    cards = [
        ("①", "严格二叉", BLUE),
        ("②", "有根树", BLUE),
        ("③", "超度量 叶到根等长", GREEN),
        ("④", "时间单位", BLUE),
        ("⑤", "校准点", BLUE),
    ]
    y, h, w, gap = 140, 190, 140, 13
    for i, (num, lab, color) in enumerate(cards):
        x = 20 + i * (w + gap)
        s.rect(x, y, w, h, WHITE, color, 6, rx=16)
        s.circle(x + w / 2, y + 62, 30, color)
        s.text(x + w / 2, y + 74, num, 36, WHITE, "middle", "bold")
        if i < 4:
            s.arrow(x + w + 2, y + h / 2, x + w + gap - 2, y + h / 2, GRAY, 5)
        # 标签行（卡下，居中；宽标签不超出卡宽太多）
        if lab == "超度量 叶到根等长":
            head, tail = lab.split(" ", 1)
            s.text(x + w / 2, 400, head, 30, INK, "middle", "bold")
            s.text(x + w / 2, 442, tail, 30, INK, "middle", "bold")
        else:
            s.text(x + w / 2, 400, lab, 30, INK, "middle", "bold")

    # 超度量天平 glyph（第③卡标签下方）
    bx = 20 + 2 * (w + gap) + w / 2
    s.line(bx, 470, bx, 520, GREEN, 6)
    s.line(bx - 40, 484, bx + 40, 484, GREEN, 6)
    s.line(bx - 40, 484, bx - 50, 508, GREEN, 4)
    s.line(bx - 40, 484, bx - 30, 508, GREEN, 4)
    s.line(bx + 40, 484, bx + 30, 508, GREEN, 4)
    s.line(bx + 40, 484, bx + 50, 508, GREEN, 4)
    s.path(f"M {bx - 56} 508 L {bx - 24} 508 L {bx - 40} 524 Z", GREEN,
           fill=GREEN)
    s.path(f"M {bx + 24} 508 L {bx + 56} 508 L {bx + 40} 524 Z", GREEN,
           fill=GREEN)

    # 底部红色拦截盾牌
    s.polygon([(400, 560), (530, 590), (530, 640), (400, 676), (270, 640),
               (270, 590)], RED)
    s.text(400, 634, "报错拦截非绕过", 34, WHITE, "middle", "bold")

    s.save("16_cafe5_ultrametric_five_checks.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

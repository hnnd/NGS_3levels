#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_red_light_three_questions.py — 生成 10_red_light_three_questions.svg
（FIG-U04-10：红灯诊断三问决策树【流程/决策】）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-10（P24，cols 一栏，viewBox 800×700）。
三级递进：一问成因查文献（青蓝）→ 二问定性防污染（橙）→ 三问下游定决策（绿）；
底部红色终止符「切忌盲目修剪」。
依据：教材 §6.4.1 L62、§6.4.3 L86–90。图内汉字 27，红色 1 处。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 10_red_light_three_questions.py
"""
from svghelp import *


def main():
    s = SVG(800, 700)
    steps = [("一问成因查文献", CYAN_DEEP), ("二问定性防污染", ORANGE_DEEP),
             ("三问下游定决策", GREEN_DEEP)]
    for i, (lab, color) in enumerate(steps):
        y = 84 + i * 168
        s.rect(150, y, 500, 100, color, rx=18)
        s.circle(196, y + 50, 26, WHITE)
        s.text(196, y + 61, str(i + 1), 30, color, "middle", "bold")
        s.text(430, y + 63, lab, 34, WHITE, "middle", "bold")
        if i < 2:
            s.arrow(400, y + 104, 400, y + 162, GRAY, sw=7)

    s.rect(200, 586, 400, 76, RED, rx=18)
    s.text(400, 636, "切忌盲目修剪", 34, WHITE, "middle", "bold")

    s.save("10_red_light_three_questions.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

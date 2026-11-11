#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_four_stage_chain.py — 生成 02_four_stage_chain.svg
（FIG-U02-02：一条可审计的链，四段各挂检查点）

方案：reviews/course/U02_FIGP_001.md §4 FIG-U02-02（P11，cols 一栏，viewBox 800×700）。
数据：无量字数字。四段与检查点依据：教材 §3.4.1 L71（输入→变换→图→导出）、
§3.4.2（读表看类型）、§3.4.3 L160（每步核行数）、§3.4.11（轴名带单位、记版本）。
红 1 处＝「出错不报错」横幅（§3.4.1 L71）。图内汉字 30，恰好满额，不得再加字。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 02_four_stage_chain.py
"""
from svghelp import *  # noqa: F401,F403

STAGES = [
    ("输入", "读表看类型"),
    ("变换", "每步核行数"),
    ("图", "轴名带单位"),
    ("导出", "记版本"),
]


def main():
    s = SVG(800, 700)
    for i, (name, check) in enumerate(STAGES):
        x = 30 + i * 195
        s.rect(x, 170, 170, 110, BLUE, rx=16)
        s.text(x + 85, 240, name, 44, WHITE, "middle", "bold")
        s.text(x + 85, 335, check, 30, GRAY, "middle")
        if i < 3:
            s.arrow(x + 176, 225, x + 189, 225, CYAN, 7)
    s.rect(40, 520, 720, 96, RED, rx=14)
    s.text(400, 586, "出错不报错", 46, WHITE, "middle", "bold")
    s.save("02_four_stage_chain.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

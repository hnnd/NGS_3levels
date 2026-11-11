#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_three_concepts_hierarchy.py — FIG-M08-02 三个概念的单向依赖阶梯（P10，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-02（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.1（可重复性是计算工程问题，可复制性与可推广性属生物学；
可重复是后两者的必要非充分条件，方向不可逆）。
图内汉字 = 方案原句逐字，共 30 字（可重复：计算工程基石 / 可复制：独立样本验证 /
可推广：跨物种生境 / 单向依赖）；其余只有层号与箭头。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 02_three_concepts_hierarchy.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

# 由宽到窄的三层阶梯：(图内文字, 底色, 边色, x, y, w)
STEPS = [
    ("可重复：计算工程基石", CYAN_TINT, CYAN, 60, 520, 640),
    ("可复制：独立样本验证", GREEN_TINT, GREEN, 140, 380, 480),
    ("可推广：跨物种生境", WHITE, GREEN, 220, 240, 320),
]
BH = 108


def main():
    s = SVG()

    for i, (txt, fill, ink, x, y, w) in enumerate(STEPS):
        s.rect(x, y, w, BH, fill, ink, 4, rx=16)
        s.text(x + w / 2, y + BH / 2 + 13, txt, 33, INK, "middle", "bold")
        s.text(x + 6, y - 12, f"{i + 1}", 30, ink, "start", "bold")

    # 层间向上箭头（青蓝，只从中轴穿过空白处）
    for y0, y1 in ((518, 492), (378, 352)):
        s.arrow(400, y0, 400, y1, CYAN, 6, 16)

    # 右侧红色不可逆单向箭头与标签（唯一红色处）
    s.arrow(740, 636, 740, 214, RED, 6, 20)
    s.text(700, 668, "单向依赖", 34, RED, "middle", "bold")

    return s.save("02_three_concepts_hierarchy.svg")


if __name__ == "__main__":
    raise SystemExit(main())

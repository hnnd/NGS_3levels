#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_parameterized_anatomy.py — FIG-M08-05 参数化脚本的四处变量解耦骨架（P15，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-05（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.1（四处变量化与双端成对映射；`${名字:-默认值}` 兜底、
`${1:?用法}` 必填断言——后者是唯一被红字标出的防线）。
图内汉字 = 方案原句逐字，共 27 字（四处变量：路径样本线程阈值 / 双端成对映射 /
默认值兜底 / 必填断言）；其余只有 ASCII 变量名与命令行开关。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 05_parameterized_anatomy.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

VARS = [("路径", "$INDIR"), ("样本", "$SAMPLE"), ("线程", "$THREADS"), ("阈值", "$QUAL")]


def main():
    s = SVG()

    # 顶部：四处变量 + 标题（12 汉字拆成标题 4 + 四枚变量名各 2）
    s.text(400, 62, "四处变量", 34, BLUE, "middle", "bold")
    for i, (name, var) in enumerate(VARS):
        cx = 118 + i * 190
        s.rect(cx - 84, 92, 168, 116, BLUE_TINT, BLUE, 4, rx=14)
        s.text(cx, 140, name, 32, BLUE, "middle", "bold")
        s.text(cx, 182, var, 30, GRAY, "middle")

    # 中部：双端成对映射（-i/-o、-I/-O）
    s.text(400, 268, "双端成对映射", 33, BLUE, "middle", "bold")
    pairs = [("-i", "-o", 60), ("-I", "-O", 404)]
    for a, b, x in pairs:
        s.rect(x, 292, 128, 78, WHITE, CYAN, 4, rx=12)
        s.text(x + 64, 344, a, 32, CYAN_DEEP, "middle", "bold")
        s.arrow(x + 134, 331, x + 200, 331, CYAN, 5, 16)
        s.rect(x + 208, 292, 128, 78, WHITE, CYAN, 4, rx=12)
        s.text(x + 272, 344, b, 32, CYAN_DEEP, "middle", "bold")

    # 底部：默认值兜底（绿）与必填断言（红，唯一警示）
    s.rect(60, 424, 330, 128, GREEN_TINT, GREEN, 4, rx=14)
    s.text(225, 470, "默认值兜底", 32, GREEN, "middle", "bold")
    s.text(225, 518, "${THREADS:-4}", 30, INK, "middle")

    s.rect(420, 424, 330, 128, RED_TINT, RED, 5, rx=14)
    s.text(585, 470, "必填断言", 32, RED, "middle", "bold")
    s.text(585, 518, "${1:?用法}", 30, RED, "middle")

    return s.save("05_parameterized_anatomy.svg")


if __name__ == "__main__":
    raise SystemExit(main())

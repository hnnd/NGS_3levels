#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_rule_all_anchor.py — FIG-M08-11 `rule all` 终点契约与 expand 展开（P27，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-11（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.2（`rule all` 把「我到底想要什么」写成文件；expand 批量展开四样本；
中间产物进终点会让删中间文件触发过度重跑）。
图内汉字 = 方案原句逐字，共 27 字（求值终点契约 / 批量展开四样本 /
中间产物勿进终点 / 防止过度重跑）；其余只有 ASCII 文件名与样本名。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 11_rule_all_anchor.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

samples = ["CK_1", "CK_2", "TR_1", "TR_2"]


def main():
    s = SVG()

    # 顶部：rule all 汇聚根（深蓝）
    s.rect(150, 22, 500, 104, BLUE_TINT, BLUE, 4, rx=16)
    s.text(400, 66, "rule all", 34, BLUE, "middle", "bold")
    s.text(400, 106, "counts_matrix.tsv + report.html", 30, GRAY, "middle")

    # 中部：expand 展开四样本（青蓝），箭头走卡片之间的空档
    for i, name in enumerate(samples):
        cx = 130 + i * 180
        s.arrow(cx, 130, cx, 178, CYAN, 5, 14)
        s.rect(cx - 66, 184, 132, 76, WHITE, CYAN, 4, rx=12)
        s.text(cx, 232, name, 30, CYAN_DEEP, "middle", "bold")

    # 展开语义注记：放在样本行下方，不压箭头
    s.text(400, 300, "批量展开四样本", 32, BLUE, "middle", "bold")

    # 底部左侧：终点契约（绿）
    s.rect(36, 336, 356, 208, GREEN_TINT, GREEN, 4, rx=16)
    s.text(214, 392, "求值终点契约", 32, GREEN, "middle", "bold")
    s.text(214, 444, "quant.sf 不进 all", 30, GRAY, "middle")
    s.text(214, 500, "防止过度重跑", 30, GREEN, "middle")

    # 底部右侧：唯一警示（红）
    s.rect(424, 336, 340, 208, RED_TINT, RED, 5, rx=16)
    s.text(594, 400, "中间产物", 32, RED, "middle", "bold")
    s.text(594, 452, "勿进终点", 32, RED, "middle", "bold")
    s.text(594, 508, "else rerun all", 30, GRAY, "middle")

    return s.save("11_rule_all_anchor.svg")


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""27_dryrun_output_dissection.py — FIG-M08-27 终端 -n 空跑输出四字段剖析（P54，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-27（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.2 L125、§23.4.3 L160（-n 输出里 wildcards 是通配符反解结果，
reason 是重跑触发依据，其余字段不必细读）。
图内汉字 = 方案原句逐字，共 26 字（空跑输出四字段 / 通配符反解查贪婪 /
触发原因查依据 / 必查两处）；字段名与命令行用 ASCII。红 1 处标「必查两处」。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 27_dryrun_output_dissection.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402


def main():
    s = SVG()

    s.text(400, 64, "空跑输出四字段", 36, BLUE, "middle", "bold")

    # 终端外框（一条 -n 输出记录）
    s.rect(40, 96, 720, 366, WHITE, BLUE, 4, rx=14)
    s.text(72, 148, "rule fastp:", 30, INK, "start")
    s.text(72, 192, "jobid: 1", 30, INK, "start")

    # 高亮 ①：wildcards（青蓝＝通配符反解，查是否贪婪吞了斜杠）
    s.rect(60, 216, 680, 62, CYAN_TINT, CYAN, 4, rx=12)
    s.text(400, 258, "wildcards: sample=CK_1", 30, CYAN_DEEP, "middle")
    s.text(400, 316, "通配符反解查贪婪", 30, CYAN_DEEP, "middle", "bold")

    # 高亮 ②：reason（绿色＝触发依据，查为什么重跑）
    s.rect(60, 342, 680, 62, GREEN_TINT, GREEN, 4, rx=12)
    s.text(400, 384, "reason: Updated input files", 30, GREEN, "middle")
    s.text(400, 436, "触发原因查依据", 30, GREEN, "middle", "bold")

    # 唯一警示：四字段里只精读这两处
    s.chip(400, 556, "必查两处", 34, RED_TINT, RED, RED)

    return s.save("27_dryrun_output_dissection.svg")


if __name__ == "__main__":
    raise SystemExit(main())

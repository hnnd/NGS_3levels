#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_bash_three_shields.py — FIG-M08-06 Bash 三道防护与一处留证（P16，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-06（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.1（-e 非零即停、-u 未定义变量报错、pipefail 补管道盲区；
2>&1 不算防护，只保证停下时有据可查）。
图内汉字 = 方案原句逐字，共 25 字（三道防护闸门 / 非零即停 / 未定义报错 /
管道穿透 / 留证防吞报错）；其余只有 ASCII 开关名与命令。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 06_bash_three_shields.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

GATES = [("set -e", "非零即停", 166), ("set -u", "未定义报错", 400),
         ("pipefail", "管道穿透", 634)]


def main():
    s = SVG()

    s.text(400, 62, "三道防护闸门", 36, BLUE, "middle", "bold")

    # 管道本体（深蓝）
    s.rect(46, 108, 708, 62, BLUE, rx=14)
    s.text(400, 150, "fastp | bwa mem | samtools sort", 30, WHITE, "middle")

    # 三道串联闸门：管道 → 竖线 → 绿色横闸 → 卡片
    for flag, han, cx in GATES:
        s.line(cx, 170, cx, 218, CYAN, 5)
        s.line(cx - 78, 220, cx + 78, 220, GREEN, 8)
        s.rect(cx - 106, 240, 212, 112, WHITE, GREEN, 4, rx=14)
        s.text(cx, 282, flag, 32, GREEN, "middle", "bold")
        s.text(cx, 330, han, 30, INK, "middle", "bold")

    # 留证通道（红＝唯一强调的易错点）：2>&1 与裸 > log 左右对照
    s.rect(96, 396, 372, 148, RED_TINT, RED, 5, rx=16)
    s.text(282, 458, "2>&1", 40, RED, "middle", "bold")
    s.text(282, 514, "留证防吞报错", 32, RED, "middle", "bold")
    # 裸重定向对照（灰＝没有留证，只丢 stdout）
    s.rect(508, 396, 236, 148, WHITE, GRAY, 4, rx=16)
    s.text(626, 458, "> log", 36, GRAY, "middle", "bold")
    s.text(626, 514, "only stdout", 30, GRAY, "middle")

    return s.save("06_bash_three_shields.svg")


if __name__ == "__main__":
    raise SystemExit(main())

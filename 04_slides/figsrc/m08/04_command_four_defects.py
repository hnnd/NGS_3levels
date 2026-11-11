#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_command_four_defects.py — FIG-M08-04 命令行直接执行的四大工程缺陷（P14，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-04（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.1（前三个缺陷属「参数写死」，第四个属「没有检查」）。
图内汉字 = 方案原句逐字，共 30 字（路径硬编码：换机失效 / 样本名写死：批量易错 /
阈值藏匿：不可审计 / 下游空跑）；其余只有 ASCII 命令、路径与退出码。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 04_command_four_defects.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

DEFECTS = [
    ("路径硬编码：换机失效", "/data/old/ref.fa", WHITE, ORANGE, INK),
    ("样本名写死：批量易错", "for s in CK_1 CK_2", WHITE, ORANGE, INK),
    ("阈值藏匿：不可审计", "--qual 20", WHITE, ORANGE, INK),
    ("下游空跑", "exit 0", RED_TINT, RED, RED),
]
CY = [66, 216, 366, 516]


def main():
    s = SVG()

    # 左侧命令卡（深蓝）：两行手敲命令
    s.rect(20, 286, 330, 140, BLUE, rx=16)
    s.text(175, 340, "run_fastp.sh CK_1", 30, WHITE, "middle", "bold")
    s.text(175, 390, "bwa mem | sort", 30, CYAN_TINT, "middle")

    # 右侧四张缺陷卡
    for y, (txt, hint, fill, ink, tink) in zip(CY, DEFECTS):
        s.rect(386, y, 386, 118, fill, ink, 4, rx=14)
        s.text(579, y + 54, txt, 32, tink, "middle", "bold")
        s.text(579, y + 98, hint, 30, GRAY, "middle")
        s.arrow(348, 356, 380, y + 59, CYAN, 5, 16)

    return s.save("04_command_four_defects.svg")


if __name__ == "__main__":
    raise SystemExit(main())

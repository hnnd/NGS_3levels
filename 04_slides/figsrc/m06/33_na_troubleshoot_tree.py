#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""33_na_troubleshoot_tree.py — FIG-M06-33 注释大片 NA 排查分支树

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-33（P57，cols 一栏
800×700，new-svg）。
教材依据：§18.5.3（大片 NA 的三大病因按概率排序：训练集不匹配第一，引物未切除第二，
读段反向互补第三；各有对应排查与修复动作）。
图内汉字 = 方案原句逐字，共 23 字（训练集不匹配首因 / 引物残留干扰分词 / 序列反向无匹配）；
其余标注为分支序号、根节点 NA 与机制字段名（reference、primer、8-mer、revcomp、direction）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 33_na_troubleshoot_tree.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403
from svghelp import (BLUE, GRAY, GREEN, INK, ORANGE, ORANGE_TINT, RED,
                     RED_TINT, SVG, WHITE)

ROOT_CX, ROOT_Y = 420, 106
BUS_X, CARD_X, CARD_W, CARD_H = 126, 162, 512, 104
ROWS = [286, 428, 570]
BRANCHES = [("训练集不匹配首因", "reference"),
            ("引物残留干扰分词", "primer / 8-mer"),
            ("序列反向无匹配", "revcomp / direction")]


def main():
    s = SVG(800, 700)

    # 根部：大片 NA 警告（红：全图唯一警示）
    s.rect(ROOT_CX - 152, ROOT_Y - 48, 304, 96, RED_TINT, RED, 5, rx=16)
    s.text(ROOT_CX, ROOT_Y + 12, "NA", 34, RED, "middle", "bold")

    # 主干（深蓝）：根 → 分支母线
    s.line(ROOT_CX, ROOT_Y + 48, ROOT_CX, 212, BLUE, 5)
    s.line(BUS_X, 212, ROOT_CX, 212, BLUE, 5)
    s.line(BUS_X, 212, BUS_X, ROWS[-1], BLUE, 5)
    for y in ROWS:
        s.line(BUS_X, y, CARD_X, y, BLUE, 5)
        s.circle(BUS_X, y, 8, BLUE)

    for i, (phrase, field) in enumerate(BRANCHES):
        y = ROWS[i]
        # 分支牌（橙：排查三项）
        s.rect(CARD_X, y - CARD_H / 2, CARD_W, CARD_H, ORANGE_TINT, ORANGE, 4,
               rx=14)
        s.text(CARD_X + 28, y - 8, phrase, 32, INK, "start", "bold")
        # 修复去向（绿）：机制字段名
        s.text(CARD_X + 28, y + 36, field, 30, GREEN, "start", "bold")
        # 序号
        s.text(CARD_X + CARD_W - 28, y + 12, str(i + 1), 34, ORANGE_DEEP,
               "end", "bold")

    s.save("33_na_troubleshoot_tree.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

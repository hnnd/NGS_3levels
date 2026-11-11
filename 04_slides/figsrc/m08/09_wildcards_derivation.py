#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_wildcards_derivation.py — FIG-M08-09 通配符逆向推导四步机制（P23，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-09（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.2（以目标文件为起点，匹配输出模式反解通配符，代回 input 递归向上；
文件存在即叶子，找不到报 MissingInputException；绝不扫描目录）。
图内汉字 = 方案原句逐字，共 29 字（目标文件名出发 / 模式匹配反解变量 /
代回输入递归向上 / 绝不扫描目录）；其余只有 ASCII 路径、文件名与报错代号。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 09_wildcards_derivation.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402


def card(s, y, han, ascii_lines, tint, stroke=CYAN):
    s.rect(40, y, 640, 118, tint, stroke, 4, rx=14)
    s.text(66, y + 38, han, 32, INK, "start", "bold")
    s.label(66, y + 82, ascii_lines, 30, GRAY, "start", leading=1.1)


def main():
    s = SVG()

    card(s, 24, "目标文件名出发", ["results/clean/CK_1_1.fq.gz"], CYAN_TINT)
    card(s, 150, "模式匹配反解变量",
         ["{sample}_1.fq.gz", "sample=CK_1"], WHITE)
    card(s, 276, "代回输入递归向上", ["data/reads/CK_1_1.fq.gz"], CYAN_TINT)

    # 竖向递归箭头（严格落在卡片间隙）
    for y0, y1 in ((142, 148), (268, 274), (394, 400)):
        s.arrow(56, y0, 56, y1, CYAN, 5, 12)

    # ④ 判定分叉：exists → run（绿）；缺失 → 报错（红）
    s.rect(40, 412, 300, 104, GREEN_TINT, GREEN, 4, rx=14)
    s.text(190, 456, "exists", 32, GREEN, "middle", "bold")
    s.text(190, 496, "run job", 30, GRAY, "middle")
    s.rect(380, 412, 300, 104, WHITE, RED, 4, rx=14)
    s.text(530, 456, "MissingInput", 32, RED, "middle", "bold")
    s.text(530, 496, "Exception", 30, RED, "middle")

    # 底部：前提纪律（红）
    s.text(400, 600, "绝不扫描目录", 36, RED, "middle", "bold")

    return s.save("09_wildcards_derivation.svg")


if __name__ == "__main__":
    raise SystemExit(main())

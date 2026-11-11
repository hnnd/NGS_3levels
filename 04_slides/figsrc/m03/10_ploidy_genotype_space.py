#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_ploidy_genotype_space.py — 生成 10_ploidy_genotype_space.svg
（FIG-M03-13：单倍体 vs 二倍体基因型空间与似然乘积）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-13（P26，cols 一栏，800×700）。
图内中文按方案（单倍体 仅参考或变异 二倍体 杂合状态 细菌设单倍体）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文，工具名/字段名/
命令/参数保留英文，字数不再按 ≤30 字核验。依据：教材 §10.4.1（L92–98）、
§10.4.4。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 48, "基因型空间", 36, INK, "middle", "bold")

    # 左：单倍体
    s.rect(40, 76, 340, 430, WHITE, CYAN, 4, rx=16)
    s.text(210, 122, "单倍体", 34, CYAN_DEEP, "middle", "bold")
    s.text(210, 162, "-ploidy 1", 30, GRAY, "middle")
    s.rect(90, 200, 110, 80, BLUE_TINT, BLUE, 4, rx=12)
    s.text(145, 254, "0", 38, BLUE, "middle", "bold")
    s.rect(230, 200, 110, 80, GREEN_TINT, GREEN, 4, rx=12)
    s.text(285, 254, "1", 38, GREEN, "middle", "bold")
    s.text(210, 350, "仅参考或变异", 32, INK, "middle", "bold")
    s.line(110, 440, 310, 440, PANEL, 6)
    s.polygon([(140, 440), (175, 440), (175, 396), (140, 396)], CYAN)
    s.polygon([(245, 440), (280, 440), (280, 382), (245, 382)], GREEN)
    s.text(210, 486, "似然×先验，2 状态", 30, GRAY, "middle")

    # 右：二倍体
    s.rect(420, 76, 340, 430, WHITE, PURPLE, 4, rx=16)
    s.text(590, 122, "二倍体", 34, PURPLE, "middle", "bold")
    s.text(590, 162, "-ploidy 2", 30, GRAY, "middle")
    s.rect(445, 200, 90, 80, BLUE_TINT, BLUE, 4, rx=12)
    s.text(490, 252, "0/0", 32, BLUE, "middle", "bold")
    s.rect(550, 200, 90, 80, RED_TINT, RED, 4, rx=12)
    s.text(595, 252, "0/1", 32, RED, "middle", "bold")
    s.rect(655, 200, 90, 80, GREEN_TINT, GREEN, 4, rx=12)
    s.text(700, 252, "1/1", 32, GREEN, "middle", "bold")
    s.text(595, 350, "杂合状态", 32, RED, "middle", "bold")
    s.text(595, 392, "细菌伪杂合", 30, RED, "middle")
    s.line(445, 440, 745, 440, PANEL, 6)
    s.polygon([(470, 440), (500, 440), (500, 400), (470, 400)], PURPLE)
    s.polygon([(555, 440), (585, 440), (585, 414), (555, 414)], RED)
    s.polygon([(640, 440), (670, 440), (670, 388), (640, 388)], ORANGE)
    s.text(595, 486, "3 状态，搜索更宽", 30, GRAY, "middle")

    # 底部结论
    s.rect(40, 556, 720, 60, GREEN_TINT, GREEN, 4, rx=12)
    s.text(400, 598, "细菌设单倍体：-ploidy 1 消除伪杂合", 32, GREEN,
           "middle", "bold")
    s.text(400, 664, "先验空间与输出格式随倍性而定", 30, GRAY,
           "middle")
    s.save("10_ploidy_genotype_space.svg")


if __name__ == "__main__":
    main()

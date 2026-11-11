#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""29_allele_dropout_directional_bias.py — 生成 29_allele_dropout_directional_bias.svg
（FIG-M03-30：低深度杂合等位丢失 Allele Dropout 系统性偏差）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-30（P56，cols 一栏，800×700）。
图内中文按方案（真实杂合 抽样波动 变异丢失 假纯合 杂合度 系统低估）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文；基因型记号
（GT 0/1、HWE 等）保留英文，字数不再按 ≤30 字核验。依据：教材 §10.4.6
（L190–198）。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 44, "等位基因丢失", 36, INK, "middle", "bold")

    # ① 真实杂合
    s.rect(40, 68, 720, 110, WHITE, PANEL, 3, rx=14)
    s.text(150, 108, "真实杂合", 32, INK, "middle", "bold")
    s.text(150, 146, "GT 0/1", 30, GRAY, "middle")
    s.rect(270, 88, 200, 34, CYAN, None, rx=6)
    s.text(370, 114, "chr ...A...", 30, WHITE, "middle")
    s.rect(270, 130, 200, 34, ORANGE, None, rx=6)
    s.text(370, 156, "chr ...G...", 30, "#33332E", "middle")
    s.text(630, 126, "两条染色体等量", 30, GRAY, "middle")

    # ② 抽样波动
    s.arrow(400, 178, 400, 214, GRAY, 6)
    s.rect(40, 218, 720, 120, WHITE, PANEL, 3, rx=14)
    s.text(150, 258, "抽样波动", 32, INK, "middle", "bold")
    s.text(150, 296, "d=8", 30, GRAY, "middle")
    for i in range(8):
        s.rect(290 + i * 56, 232, 48, 30, CYAN, None, rx=4)
    s.text(610, 298, "8/8 全 REF：0.39%", 30, ORANGE, "middle", "bold")
    s.text(610, 330, "或仅 1 ALT：3.5%", 30, GRAY, "middle")

    # ③ 假纯合
    s.arrow(400, 338, 400, 374, RED, 6)
    s.rect(40, 378, 720, 110, RED_TINT, RED, 4, rx=14)
    s.text(150, 418, "假纯合", 32, RED, "middle", "bold")
    s.text(150, 456, "变异丢失", 30, RED, "middle")
    s.rect(300, 400, 200, 44, WHITE, BLUE, 4, rx=8)
    s.text(400, 432, "GT = 0/0", 32, BLUE, "middle", "bold")
    s.text(610, 432, "判为纯合参考", 30, GRAY, "middle")

    # ④ 群体后果
    s.arrow(400, 488, 400, 524, GRAY, 6)
    s.rect(40, 528, 720, 130, WHITE, PANEL, 3, rx=14)
    s.text(230, 570, "杂合度 系统低估", 32, RED, "middle", "bold")
    s.text(230, 610, "丢失的总是杂合子", 30, GRAY, "middle")
    s.line(430, 590, 700, 590, BLUE, 5)
    s.arrow(430, 590, 660, 590, ORANGE, 5)
    s.text(565, 636, "偏离 HWE", 30, ORANGE, "middle", "bold")
    s.save("29_allele_dropout_directional_bias.svg")


if __name__ == "__main__":
    main()

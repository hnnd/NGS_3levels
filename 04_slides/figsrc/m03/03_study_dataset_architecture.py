#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""03_study_dataset_architecture.py — 生成 03_study_dataset_architecture.svg
（FIG-M03-04：12 株主线数据与 CIX2779 内建自比架构）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-04（P13，cols 一栏，800×700）。
图内中文按方案（参考基因组 11株重测序 发现变异 自比阴性对照 变异近零）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文，工具名/字段名/
命令/参数保留英文，字数不再按 ≤30 字核验。依据：教材 §10.1、§10.6。
无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 左：参考源
    s.rect(40, 110, 220, 320, BLUE_TINT, BLUE, 5, rx=16)
    s.text(150, 162, "参考基因组", 32, BLUE, "middle", "bold")
    s.text(150, 210, "CIX2779", 32, INK, "middle")
    s.text(150, 252, "GCA_024981335", 30, GRAY, "middle")
    s.text(150, 292, "4.77 Mb", 30, INK, "middle")
    s.line(70, 370, 230, 370, BLUE, 8)
    s.circle(70, 370, 9, BLUE)
    s.circle(230, 370, 9, BLUE)

    # 中上：11 株异源菌株
    s.rect(320, 80, 220, 230, WHITE, CYAN, 5, rx=16)
    s.text(430, 124, "11株重测序", 32, CYAN_DEEP, "middle", "bold")
    s.text(430, 160, "PRJEB100987", 30, GRAY, "middle")
    for r in range(3):
        for c in range(4):
            if r == 2 and c == 3:
                continue
            s.rect(342 + c * 46, 178 + r * 36, 36, 30, CYAN, None, rx=6)
    s.text(430, 298, "发现变异", 32, CYAN_DEEP, "middle", "bold")

    # 右上：多态矩阵
    s.rect(580, 80, 190, 230, WHITE, PANEL, 3, rx=16)
    s.text(675, 124, "0/1 矩阵", 30, INK, "middle", "bold")
    for r in range(5):
        for c in range(7):
            x = 600 + c * 22
            y = 150 + r * 26
            col = WHITE if (r * 7 + c) % 3 else CYAN
            s.rect(x, y, 18, 22, col, PANEL, 2)

    # 中下：同源自比
    s.rect(320, 400, 220, 130, GREEN_TINT, GREEN, 5, rx=16)
    s.text(430, 444, "自比阴性对照", 32, GREEN, "middle", "bold")
    s.text(430, 484, "ERR15732332", 30, INK, "middle")
    s.text(430, 516, "CIX2779 本株", 30, GRAY, "middle")

    # 右下：判读标尺
    s.rect(580, 400, 190, 130, WHITE, PANEL, 3, rx=16)
    s.text(675, 444, "变异近零", 32, GREEN, "middle", "bold")
    s.text(675, 486, "≈ 0", 30, INK, "middle")
    s.text(675, 518, ">0 → 核查", 30, RED, "middle")

    s.arrow(260, 220, 320, 200, BLUE, 6)
    s.arrow(540, 200, 580, 200, CYAN, 6)
    s.arrow(260, 350, 320, 460, BLUE, 6)
    s.arrow(540, 465, 580, 465, GREEN, 6)

    s.text(400, 596, "12 样本 = 11 发现变异 + 1 自比核查", 30, GRAY,
           "middle")
    s.text(400, 652, "内建答案：自比变异 ≈ 0", 30, GRAY, "middle")
    s.save("03_study_dataset_architecture.svg")


if __name__ == "__main__":
    main()

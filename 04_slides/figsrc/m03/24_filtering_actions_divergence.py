#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""24_filtering_actions_divergence.py — 生成 24_filtering_actions_divergence.svg
（FIG-M03-27：过滤动作三岔路：打标签/物理删行/置缺失）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-27（P49，cols 一栏，800×700）。
图内中文按方案（打标签 保留全记录 物理删行 位点消失 置缺失 个体留空）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文；工具名与命令
（VariantFiltration/bcftools view -f PASS/bcftools filter -S .）保留英文，
字数不再按 ≤30 字核验。依据：教材 §10.4.8（L243–258）。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 44, "三种过滤动作", 36, INK, "middle", "bold")

    s.rect(280, 68, 240, 76, BLUE_TINT, BLUE, 4, rx=14)
    s.text(400, 100, "一个变异位点", 30, INK, "middle", "bold")
    s.text(400, 130, "12 样本 × GT", 30, GRAY, "middle")

    branches = [
        (50, "打标签", ("Variant", "Filtration"), GREEN, GREEN_TINT,
         "FILTER", "QD2;FS", "保留全记录"),
        (290, "物理删行", ("bcftools", "view -f PASS"), ORANGE, ORANGE_TINT,
         "删除", "行消失", "位点消失"),
        (530, "置缺失", ("bcftools", "filter -S ."), PURPLE, PURPLE_TINT,
         "s05: GT=.", "其余保留", "个体留空"),
    ]
    for x, t1, en, col, fill, r1, r2, t2 in branches:
        s.arrow(400, 144, x + 105, 196, GRAY, 6)
        s.rect(x, 200, 210, 320, WHITE, col, 5, rx=16)
        s.text(x + 105, 246, t1, 32, col, "middle", "bold")
        s.text(x + 105, 284, en[0], 30, GRAY, "middle")
        s.text(x + 105, 318, en[1], 30, GRAY, "middle")
        s.rect(x + 25, 344, 160, 100, fill, col, 3, rx=8)
        s.text(x + 105, 386, r1, 30, col, "middle", "bold")
        s.text(x + 105, 422, r2, 30, INK, "middle")
        s.text(x + 105, 486, t2, 30, col, "middle", "bold")

    s.rect(50, 540, 210, 58, GREEN_TINT, GREEN, 3, rx=10)
    s.text(155, 579, "可逆", 30, GREEN, "middle")
    s.rect(290, 540, 210, 58, RED_TINT, RED, 3, rx=10)
    s.text(395, 579, "证据丢失", 30, RED, "middle")
    s.rect(530, 540, 210, 58, PURPLE_TINT, PURPLE, 3, rx=10)
    s.text(635, 579, "位点保留", 30, PURPLE, "middle")

    s.text(400, 650, "单倍体缺失 = 单点 .（二倍体 ./.）", 30,
           RED, "middle", "bold")
    s.save("24_filtering_actions_divergence.svg")


if __name__ == "__main__":
    main()

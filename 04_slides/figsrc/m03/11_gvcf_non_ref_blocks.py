#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_gvcf_non_ref_blocks.py — 生成 11_gvcf_non_ref_blocks.svg
（FIG-M03-14：单样本稀疏 VCF vs gVCF <NON_REF> 连续参考块）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-14（P27，cols 一栏，800×700）。
图内中文按方案（单样本稀疏 参考块 最小深度 区分未测到 与无变异）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文，工具名/字段名/
命令/参数保留英文，字数不再按 ≤30 字核验。依据：教材 §10.4.5（L156–176）、
§10.5.4。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 48, "VCF 与 gVCF", 36, INK, "middle", "bold")

    # 上：单样本普通 VCF
    s.rect(40, 72, 720, 240, WHITE, PANEL, 3, rx=14)
    s.text(170, 114, "单样本稀疏", 32, INK, "middle", "bold")
    s.text(470, 114, "仅变异位点有行", 30, GRAY, "middle")
    s.line(80, 250, 720, 250, BLUE, 5)
    for i in range(11):
        s.line(90 + i * 60, 240, 90 + i * 60, 260, BLUE, 3)
    for x in (150, 390, 630):
        s.rect(x - 30, 140, 60, 70, RED_TINT, RED, 4, rx=8)
        s.text(x, 172, "SNP", 30, RED, "middle", "bold")
        s.text(x, 204, "行", 30, GRAY, "middle")
        s.line(x, 210, x, 250, RED, 3)
    # 盲区问号
    for cx in (265, 510):
        s.circle(cx, 172, 32, "none", RED, 5, dash="9 9")
        s.text(cx, 184, "?", 38, RED, "middle", "bold")
    s.text(400, 296, "深覆盖纯合参考与零覆盖：看上去一样", 30,
           RED, "middle")

    # 下：gVCF
    s.rect(40, 340, 720, 250, WHITE, PANEL, 3, rx=14)
    s.text(140, 382, "gVCF", 32, CYAN_DEEP, "middle", "bold")
    s.text(215, 382, "<NON_REF> 块：END / MIN_DP / GQ", 30, GRAY,
           "start")
    s.line(80, 520, 720, 520, BLUE, 5)
    for i in range(11):
        s.line(90 + i * 60, 510, 90 + i * 60, 530, BLUE, 3)
    for x in (150, 630):
        s.rect(x - 30, 410, 60, 70, RED_TINT, RED, 4, rx=8)
        s.text(x, 442, "SNP", 30, RED, "middle", "bold")
        s.line(x, 480, x, 520, RED, 3)
    # NON_REF 参考块
    s.rect(200, 410, 190, 70, CYAN, None, rx=8)
    s.text(295, 442, "<NON_REF>", 30, WHITE, "middle", "bold")
    s.text(295, 492, "END=20450", 30, CYAN_DEEP, "middle")
    s.rect(420, 410, 170, 70, GREEN, None, rx=8)
    s.text(505, 442, "<NON_REF>", 30, WHITE, "middle", "bold")
    s.text(505, 492, "MIN_DP=3", 30, GREEN, "middle")
    s.text(200, 566, "参考块", 30, CYAN_DEEP, "middle", "bold")
    s.text(330, 566, "最小深度", 30, INK, "middle", "bold")

    # 底部结论
    s.rect(40, 610, 720, 60, BLUE_TINT, BLUE, 4, rx=12)
    s.text(400, 651, "区分未测到与无变异", 34, BLUE, "middle", "bold")
    s.save("11_gvcf_non_ref_blocks.svg")


if __name__ == "__main__":
    main()

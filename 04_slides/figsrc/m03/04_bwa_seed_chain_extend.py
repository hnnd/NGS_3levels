#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_bwa_seed_chain_extend.py — 生成 04_bwa_seed_chain_extend.svg
（FIG-M03-06：种子—链化—延伸与变异密集区种子脱落）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-06（P18，cols 一栏，800×700）。
图内中文按方案（读段 种子匹配 延伸打分 密集变异 种子脱落比对失败）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文，工具名/字段名/
命令/参数保留英文，字数不再按 ≤30 字核验。依据：教材 §7.4.4、§10.4.1。
无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def ref_axis(s, y):
    s.line(60, y, 740, y, BLUE, 6)
    for i in range(11):
        s.line(70 + i * 62, y - 10, 70 + i * 62, y + 10, BLUE, 3)


def main():
    s = SVG(800, 700)
    s.text(400, 50, "种子 → 链化 → 延伸", 36, INK, "middle", "bold")

    # 上：正常区域
    s.rect(40, 74, 720, 240, WHITE, PANEL, 3, rx=14)
    s.text(130, 114, "正常区域", 30, BLUE, "middle", "bold")
    ref_axis(s, 150)
    s.rect(110, 180, 250, 34, CYAN, None, rx=4)
    s.rect(420, 180, 230, 34, CYAN, None, rx=4)
    s.text(235, 206, "种子 ≥19bp", 30, WHITE, "middle", "bold")
    s.text(535, 206, "种子 ≥19bp", 30, WHITE, "middle", "bold")
    s.polyline([(360, 197), (420, 197)], PURPLE, 6, dash="12 9")
    s.text(390, 240, "链化", 30, PURPLE, "middle", "bold")
    s.arrow(650, 197, 720, 197, GREEN, 6)
    s.text(610, 252, "SW 延伸打分", 30, GREEN, "middle", "bold")
    s.rect(560, 270, 170, 36, GREEN_TINT, GREEN, 4, rx=8)
    s.text(645, 297, "MAPQ 60", 30, GREEN, "middle", "bold")

    # 下：变异密集区
    s.rect(40, 350, 720, 260, WHITE, PANEL, 3, rx=14)
    s.text(170, 392, "密集变异", 30, ORANGE, "middle", "bold")
    s.text(470, 392, "错配 / 微小 InDel", 30, GRAY, "middle")
    ref_axis(s, 430)
    for i, x in enumerate(range(120, 700, 44)):
        col = ORANGE if i % 2 else PURPLE
        s.line(x, 412, x, 448, col, 7)
    # 读段碎片
    s.rect(120, 470, 90, 28, CYAN, None, rx=4)
    s.rect(240, 470, 70, 28, CYAN, None, rx=4)
    s.rect(340, 470, 80, 28, CYAN, None, rx=4)
    s.rect(450, 470, 60, 28, CYAN, None, rx=4)
    s.text(280, 540, "读段", 30, GRAY, "middle", "bold")
    s.text(470, 540, "碎片均 <19bp", 30, GRAY, "middle", "bold")
    # 脱落
    s.polygon([(560, 462), (680, 462), (680, 504), (560, 504)], RED_TINT,
              RED, 4)
    s.text(620, 492, "读段", 30, RED, "middle", "bold")
    s.arrow(620, 508, 620, 556, RED, 6)
    s.rect(200, 560, 330, 40, RED_TINT, RED, 4, rx=8)
    s.text(365, 589, "种子脱落比对失败", 32, RED, "middle", "bold")
    s.text(620, 640, "无链化 → 无延伸", 30, GRAY, "middle")
    s.save("04_bwa_seed_chain_extend.svg")


if __name__ == "__main__":
    main()

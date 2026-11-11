#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_flag_163.py — 生成 17_flag_163.svg（FIG-U03-17：FLAG 163 位掩码与双端几何）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-17（P44，cols 一栏，800×700）。
教材依据：chapters/ch04/manuscript.qmd §5.4.5、demos/ch05_flag_cigar.py。
163 = 128(READ2) + 32(MREVERSE) + 2(PROPER_PAIR) + 1(PAIRED)；
几何：R1 正链向右、R2 负链向左（相对朝向）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 17_flag_163.py
"""
from svghelp import *  # noqa: F401,F403

TERMS = [("128", "READ2", False), ("32", "MREVERSE", False),
         ("2", "PROPER_PAIR", True), ("1", "PAIRED", False)]


def main():
    s = SVG(800, 700)
    s.text(400, 50, "位掩码分解四位", 36, BLUE, "middle", "bold")
    s.text(400, 92, "双端相对朝向几何合理不保无错", 30, GRAY, "middle",
           "bold")

    # 算式条：163 = 128 + 32 + 2 + 1（位名两行交错，避免相邻长标签重叠）
    s.rect(60, 120, 680, 96, WHITE, PANEL, 3, rx=14)
    s.text(90, 176, "163 =", 38, BLUE, "start", "bold")
    x = 268
    for i, (val, name, hot) in enumerate(TERMS):
        s.text(x, 168, val, 36, RED if hot else INK, "middle", "bold")
        s.text(x, 198 if i % 2 == 0 else 214, name, 22,
               RED if hot else GRAY, "middle", "bold")
        x += 118
        if i < 3:
            s.text(x - 60, 168, "＋", 32, GRAY, "middle", "bold")

    # 红色焦点：PROPER_PAIR 的语义边界
    s.rect(150, 236, 500, 54, RED, rx=12)
    s.text(400, 273, "PROPER_PAIR：几何合理 ≠ 无错配", 30, WHITE, "middle",
           "bold")

    # 双端几何：参考双链 + R1 向右、R2 向左
    s.line(80, 420, 740, 420, GRAY, 4)
    s.line(80, 452, 740, 452, GRAY, 4)
    # R1：正链，箭头向右
    s.rect(140, 470, 240, 40, CYAN, rx=8)
    s.polygon([(380, 470), (420, 490), (380, 510)], CYAN)
    s.text(260, 498, "R1", 34, WHITE, "middle", "bold")
    # R2：负链，箭头向左
    s.rect(540, 540, 230, 40, PURPLE, rx=8)
    s.polygon([(540, 540), (500, 560), (540, 580)], PURPLE)
    s.text(660, 568, "R2", 34, WHITE, "middle", "bold")
    # 配对虚线
    s.line(400, 510, 520, 548, GRAY, 4, dash="12 10")

    # FLAG 归属标注
    s.text(400, 640, "R1 → FLAG 64 ｜ R2 → FLAG 128 ｜ R2 反向 → 32", 28,
           INK, "middle", "bold")

    s.save("17_flag_163.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

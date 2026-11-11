#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_pl_gq_calculation.py — 生成 20_pl_gq_calculation.svg
（FIG-M03-23：PL 归一化与 GQ 手算标尺）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-23（P45，cols 一栏，800×700）。
图内中文按方案（似然归一 最优归零 次小即质量 错误率对数 封顶九十九）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文；字段名与公式
（PL/GQ/GT、-10·log10 等）保留英文原样，字数不再按 ≤30 字核验。依据：
教材 §10.4.1（L99–106）。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403

PL = {"0/0": 0, "0/1": 91, "1/1": 220}


def main():
    s = SVG(800, 700)
    s.text(400, 46, "PL → GQ 标尺", 36, INK, "middle", "bold")

    # 左：PL 标尺
    s.rect(40, 76, 460, 470, WHITE, PANEL, 3, rx=14)
    s.text(270, 118, "似然归一", 32, INK, "middle", "bold")
    s.text(270, 156, "最优归零", 30, GRAY, "middle")
    base = 470
    s.line(80, base, 470, base, BLUE, 4)
    s.line(80, 190, 80, base, BLUE, 4)
    for v in (0, 100, 200):
        x = 100 + v / 240 * 330
        s.line(x, base - 6, x, base + 6, GRAY, 3)
        s.text(x, base + 40, str(v), 30, GRAY, "middle")
    s.text(275, base + 84, "PL = -10·log10(P/Pmax)", 30, GRAY, "middle")
    for gt, pl in PL.items():
        x = 100 + pl / 240 * 330
        col = GREEN if pl == 0 else (ORANGE if pl == 91 else PANEL)
        h = 190 if pl == 0 else (110 if pl == 91 else 56)
        s.rect(x - 30, base - h, 60, h, col, None, rx=6)
        s.text(x, base - h - 14, str(pl), 30,
               GREEN if pl == 0 else (ORANGE if pl == 91 else GRAY),
               "middle", "bold")
        s.text(x, 592, gt, 30, INK, "middle")
    s.text(215, 250, "最优 PL=0", 30, GREEN, "middle", "bold")
    s.text(330, 318, "次小即质量", 30, ORANGE, "middle", "bold")

    # 右：GQ 对数标尺
    s.rect(540, 76, 220, 470, WHITE, PANEL, 3, rx=14)
    s.text(650, 118, "错误率对数", 32, INK, "middle", "bold")
    for gq, err in [(20, "1%"), (30, "0.1%"), (50, "0.001%")]:
        y = 200 + (gq - 20) / 30 * 200
        s.line(565, y, 600, y, ORANGE, 5)
        s.text(680, y + 10, f"GQ{gq} = {err}", 30, ORANGE, "middle")
    s.text(650, 460, "P(err)=10^(-GQ/10)", 30, GRAY, "middle")
    s.rect(570, 486, 160, 48, RED_TINT, RED, 4, rx=8)
    s.text(650, 520, "封顶九十九", 30, RED, "middle", "bold")

    s.text(400, 644, "GQ = 次小 PL（前提：最优 GT 正确）", 30, INK,
           "middle", "bold")
    s.text(400, 682, "PL = 0, 91, 220  →  GQ = 91", 30, GRAY, "middle")
    s.save("20_pl_gq_calculation.svg")


if __name__ == "__main__":
    main()

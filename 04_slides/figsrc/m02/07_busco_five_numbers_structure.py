#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_busco_five_numbers_structure.py — 07_busco_five_numbers_structure.svg
（FIG-M02-11，P27，cols）：BUSCO C=S+D 与 C+F+M=100% 堆叠条与基准分母 n【new-svg】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-11。数据（与 demos 现跑一致）：
demos/ch08_n50_vs_completeness.py --selftest 算例 4（bacteria_odb10，n=124；
示例 C:98.4%[S:97.6%,D:0.8%]，1 基因 = 0.81 pp）。
无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 07_busco_five_numbers_structure.py
"""
from svghelp import (BLUE, CYAN, GRAY, INK, ORANGE, PANEL, PURPLE, RED, SVG,
                     WHITE)

# 示例值（demos 算例 4）：S=97.6、D=0.8、F=0.9、M=0.7（和 100）
S, D, F, M = 97.6, 0.8, 0.9, 0.7
assert abs(S + D + F + M - 100) < 1e-9
N_BUSCO = 124


def main():
    s = SVG(800, 700)

    # 基准分母 n 卡片（红框）
    s.rect(470, 70, 300, 150, WHITE, RED, 7, rx=16)
    s.text(620, 132, f"n = {N_BUSCO}", 46, BLUE, "middle", "bold")
    s.text(620, 188, "先报库名与分母 n", 32, RED, "middle", "bold")

    # 堆叠条（示意宽度，段上标数值）
    x0, y0, bw, bh = 60, 300, 680, 100
    segs = [(S, CYAN, INK, "S"), (D, ORANGE, INK, "D"),
            (F, PURPLE, WHITE, "F"), (M, PANEL, INK, "M")]
    cx = x0
    for val, fill, tcol, lab in segs:
        w = bw * val / 100.0
        s.rect(cx, y0, w, bh, fill, WHITE, 3)
        if lab == "S":
            s.text(cx + w / 2, y0 + 62, f"{lab} {val}%", 30, tcol, "middle",
                   "bold")
        cx += w

    # C=S+D 上括号（深蓝）
    s.line(x0, y0 - 26, x0 + bw * (S + D) / 100, y0 - 26, BLUE, 6)
    s.line(x0, y0 - 26, x0, y0 - 8, BLUE, 6)
    s.line(x0 + bw * (S + D) / 100, y0 - 26, x0 + bw * (S + D) / 100, y0 - 8,
           BLUE, 6)
    s.text(x0 + bw * (S + D) / 200, y0 - 44, "完整 C = 单拷贝 S + 多拷贝 D",
           32, BLUE, "middle", "bold")

    # 段内只标 S；D/F/M 以图例行给出（段太窄，避免文字叠压）
    legend = [("D", D, ORANGE, INK), ("F", F, PURPLE, WHITE),
              ("M", M, PANEL, INK)]
    lx = 220
    for lab, val, fill, tcol in legend:
        s.rect(lx, 442, 22, 22, fill, GRAY, 2)
        s.text(lx + 32, 463, f"{lab} {val}%", 30, tcol if tcol != WHITE
               else INK, "start", "bold")
        lx += 150
    s.text(400, 516, "碎片 F 与缺失 M", 32, GRAY, "middle", "bold")
    s.text(400, 578, "C + F + M = 100%", 36, INK, "middle", "bold")
    s.text(400, 646, "只报 C 无法解读", 34, INK, "middle", "bold")

    s.save("07_busco_five_numbers_structure.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

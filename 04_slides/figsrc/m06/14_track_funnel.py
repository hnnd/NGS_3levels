#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_track_funnel.py — FIG-M06-14 track 表五步保留漏斗（data-plot）

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-14（P26，cols 一栏
800×700，data-plot）。
数据来源：教材 §18.4.3 的设例 track 表算式，脚本内现算并断言（见 main 里的 assert）：
input 37 400 → filtered 33 660 → denoised 30 294 → merged 30 294 → nonchim 27 265，
filtered/input 与 denoised/filtered、nonchim/merged 各 90.0%，总保留 72.9%。
右侧自查线 >70% / >60% / >55% 是**本课程练习自查线**，不是文献阈值、也不是实测结果，
故图面只写数字，不加解释性文字（解释在 deck 说明行）。
图内汉字 = 方案原句逐字，共 18 字（各步九成保留 / 总保留七成三 / 自查线作参照）；
其余标注为工具字段名与数字。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 14_track_funnel.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403
from svghelp import (BLUE, CYAN, GRAY, GREEN, GREEN_TINT, INK, ORANGE, SVG,
                     WHITE)

INPUT, FILTERED, DENOISED, MERGED, NONCHIM = 37400, 33660, 30294, 30294, 27265

X0, MAXW = 200, 460          # 满格 = input
NAME_X = X0 - 18             # 字段名列（bar 左侧，右对齐）
PCT_X = 630                  # 保留率列
BH, PITCH, TOP = 40, 92, 96

ROWS = [("input", INPUT, "", BLUE),
        ("filtered", FILTERED, "90.0%", CYAN),
        ("denoised", DENOISED, "90.0%", CYAN),
        ("merged", MERGED, "", GREEN),           # 设例中合并不掉读段，故不标「九成」
        ("nonchim", NONCHIM, "90.0%", GREEN)]
# 课程自查线：只挂在对应那一步
CHECKS = [(">70%", 1, 0.70), (">60%", 3, 0.60), (">55%", 4, 0.55)]


def main():
    r_filt = FILTERED / INPUT
    r_deno = DENOISED / FILTERED
    r_nonchim = NONCHIM / MERGED
    r_total = NONCHIM / INPUT
    assert abs(r_filt - 0.90) < 1e-12, r_filt
    assert abs(r_deno - 0.90) < 1e-12, r_deno
    assert abs(r_nonchim - 0.90) < 5e-4, r_nonchim           # 27265/30294 = 0.9000…
    assert abs(r_total - 0.729) < 5e-4, r_total              # 显示 72.9%
    assert f"{r_total * 100:.1f}" == "72.9", r_total
    assert MERGED == DENOISED
    print(f"check: 各步保留 {r_filt*100:.1f}% / {r_deno*100:.1f}% / "
          f"{r_nonchim*100:.1f}%，总保留 {r_total*100:.1f}%（教材 §18.4.3 设例）")

    s = SVG(800, 700)

    s.text(400, 62, "各步九成保留", 32, INK, "middle", "bold")

    geo = {}
    for i, (name, cnt, pct, color) in enumerate(ROWS):
        y = TOP + i * PITCH
        w = MAXW * cnt / INPUT
        geo[i] = (y, w)
        s.text(NAME_X, y + BH / 2 + 11, name, 30, INK, "end", "bold")
        s.rect(X0, y, w, BH, color, rx=8)
        s.text(X0 + 18, y + BH / 2 + 11, f"{cnt:,}".replace(",", " "),
               30, WHITE, "start", "bold")
        if pct:
            s.text(PCT_X, y + BH / 2 + 11, pct, 30, GRAY, "start", "bold")

    # 课程自查线：橙色虚线，落在该步 bar 的中段空白处
    for lab, row, frac in CHECKS:
        y, _ = geo[row]
        x = X0 + MAXW * frac
        s.line(x, y - 10, x, y + BH + 10, ORANGE, 5, dash="11 8")
        s.text(x, y - 16, lab, 30, ORANGE, "middle", "bold")

    # 自查线图例（数字 + 原句）
    lx = 96
    for lab, _, _ in CHECKS:
        s.line(lx, 540, lx + 32, 540, ORANGE, 5, dash="11 8")
        s.text(lx + 42, 550, lab, 30, ORANGE, "start", "bold")
        lx += 148
    s.text(540, 550, "自查线作参照", 30, GRAY, "start")

    # 总保留
    s.rect(196, 592, 470, 62, GREEN_TINT, GREEN, 4, rx=14)
    s.text(300, 633, "总保留七成三", 30, INK, "middle", "bold")
    s.text(566, 633, f"{r_total * 100:.1f}%", 32, GREEN, "middle", "bold")

    s.save("14_track_funnel.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

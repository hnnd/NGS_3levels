#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""37_rarefaction_sample_loss.py — FIG-M06-37 抽平深度定界与低深度样本取舍

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-37（P65，cols 一栏
800×700，new-svg）。
教材依据：§18.4.9（抽平要先把深度阈值定下来：降阈值可保住全部样本但牺牲稀有种
检测力；维持推荐深度则要剔除低深度样本，且必须写明名单与理由，禁止静默剔除）。
图内汉字 = 方案原句逐字，共 22 字（降低深度保全样本 / 维持深度严格披露 /
禁止静默剔除）；其余标注为设例深度、样本序号与保留样本数。
设例深度值仅为示意（教材把 10 000 明确列为示例值，非实测），脚本内现算保留样本数并断言。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 37_rarefaction_sample_loss.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403
from svghelp import (BLUE, CYAN, CYAN_DEEP, CYAN_TINT, GRAY, GREEN, GREEN_TINT,
                     INK, ORANGE, ORANGE_DEEP, ORANGE_TINT, RED, RED_TINT, SVG,
                     WHITE)

# 设例：12 个样本的读段数，抽平阈值 10 000
DEPTHS = [12400, 13600, 11800, 10400, 9800, 9200,
          15100, 13900, 10200, 8600, 12700, 7800]
THRESH = 10000
YTOP, YBASE = 132, 372                 # 柱顶上限 = VMAX
VMAX = 16000
X0, BARW, GAP = 66, 44, 8


def main():
    keep = sum(1 for d in DEPTHS if d >= THRESH)
    lose = len(DEPTHS) - keep
    assert keep + lose == len(DEPTHS)
    assert lose == 4, lose            # 9800 / 9200 / 8600 / 7800
    print(f"check: 设例 {len(DEPTHS)} 个样本，阈值 {THRESH}，"
          f"低于阈值 {lose} 个 → 保留 {keep}")

    s = SVG(800, 700)

    # ---------------- 上：样本深度柱（达到阈值深蓝、低于阈值橙） ----------------
    def ytop_of(d):
        return YBASE - d / VMAX * (YBASE - YTOP)

    s.line(40, YBASE, 764, YBASE, GRAY, 4)
    for i, d in enumerate(DEPTHS):
        x = X0 + i * (BARW + GAP)
        top = ytop_of(d)
        s.rect(x, top, BARW, YBASE - top,
               ORANGE if d < THRESH else BLUE, rx=6)
        s.text(x + BARW / 2, YBASE + 36, str(i + 1), 30, GRAY, "middle")

    # 红：抽平阈值（全图唯一警示线，水平）
    ty = ytop_of(THRESH)
    s.line(40, ty, 770, ty, RED, 5, dash="12 9")
    s.text(776, ty - 20, "10000", 30, GRAY, "end", "bold")

    # ---------------- 下：两条取舍路径 ----------------
    CY, CH, CW = 448, 148, 346
    LX, RX = 32, 422

    # 左：降阈值保样本（青蓝）
    s.rect(LX, CY, CW, CH, WHITE, BLUE, 4, rx=16)
    s.text(LX + CW / 2, CY + 52, "降低深度保全样本", 31, INK, "middle", "bold")
    s.rect(LX + 32, CY + 84, CW - 64, 12, CYAN_TINT, rx=6)
    s.rect(LX + 32, CY + 84, CW - 64, 12, CYAN, rx=6)
    s.text(LX + CW / 2, CY + 126, f"n = {len(DEPTHS)}", 30, CYAN_DEEP, "middle",
           "bold")

    # 右：维持阈值、严格披露剔除名单（橙）
    s.rect(RX, CY, CW, CH, WHITE, BLUE, 4, rx=16)
    s.text(RX + CW / 2, CY + 52, "维持深度严格披露", 31, INK, "middle", "bold")
    s.rect(RX + 32, CY + 84, CW - 64, 12, ORANGE_TINT, rx=6)
    s.rect(RX + 32, CY + 84, (CW - 64) * keep / len(DEPTHS), 12, ORANGE, rx=6)
    s.text(RX + CW / 2, CY + 126, f"n = {len(DEPTHS)} → {keep}", 30, ORANGE_DEEP,
           "middle", "bold")

    # 红：禁止静默剔除（警示条，与阈值线共 2 处红）
    s.rect(178, 614, 444, 60, RED_TINT, PANEL, 4, rx=12)
    s.text(400, 654, "禁止静默剔除", 32, RED, "middle", "bold")

    s.save("37_rarefaction_sample_loss.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

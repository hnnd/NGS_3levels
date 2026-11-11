#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""35_merge_fallback_options.py — FIG-M06-35 合并失败的两条退路

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-35（P63，cols 一栏
800×700，new-svg）。
教材依据：§18.5.1（重叠不足时合并会崩，而 track 表不报错）与 §18.7 习题 3
（两条退路：justConcatenate 插 N 强接、只用 R1 单端跑）。
图内汉字 = 方案原句逐字，共 24 字（插氮连接不可建树 / 单端运行损失分辨 /
两条退路皆有代价）；其余标注为参数名、读段结构与 A/B 标记。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 35_merge_fallback_options.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403
from svghelp import (BLUE, CYAN, CYAN_DEEP, CYAN_TINT, GRAY, INK, ORANGE,
                     ORANGE_DEEP, ORANGE_TINT, PANEL, RED, RED_TINT, SVG,
                     WHITE)

CARD_W, CARD_H = 330, 440
LX, RX, CY, HDR = 46, 424, 124, 78


def head(s, x, tag, tint, stroke, ink):
    """卡片 + 顶部色带（上圆角、下平直）。"""
    s.rect(x, CY, CARD_W, CARD_H, WHITE, BLUE, 4, rx=16)
    d = (f"M {x} {CY + HDR} L {x} {CY + 16} Q {x} {CY} {x + 16} {CY} "
         f"L {x + CARD_W - 16} {CY} Q {x + CARD_W} {CY} {x + CARD_W} {CY + 16} "
         f"L {x + CARD_W} {CY + HDR} Z")
    s.path(d, stroke, 4, tint)
    s.text(x + CARD_W / 2, CY + 54, tag, 32, ink, "middle", "bold")


def main():
    s = SVG(800, 700)

    # ---------------- 方案 A：justConcatenate 插 10 个 N 强接（橙） -------------
    head(s, LX, "A", ORANGE_TINT, ORANGE, ORANGE_DEEP)

    y = 246
    s.rect(LX + 32, y, 96, 34, CYAN, rx=6)
    s.text(LX + 80, y + 25, "R1", 30, WHITE, "middle", "bold")
    s.rect(LX + 136, y, 78, 34, ORANGE, rx=6)
    s.text(LX + 175, y + 25, "10N", 30, WHITE, "middle", "bold")
    s.rect(LX + 222, y, 96, 34, CYAN, rx=6)
    s.text(LX + 270, y + 25, "R2", 30, WHITE, "middle", "bold")

    s.text(LX + CARD_W / 2, 340, "justConcatenate", 30, INK, "middle", "bold")
    s.text(LX + CARD_W / 2, 400, "插氮连接不可建树", 32, INK, "middle", "bold")

    # 红：建树失效（全图唯一警示，只有一对叉线）
    s.cross(LX + CARD_W / 2, 472, 26, RED, 8)
    s.text(LX + CARD_W / 2, 536, "no tree", 30, GRAY, "middle")

    # ---------------- 方案 B：只用 R1 单端（青蓝） -------------
    head(s, RX, "B", CYAN_TINT, CYAN, CYAN_DEEP)
    s.rect(RX + 32, y, 96, 34, CYAN, rx=6)
    s.text(RX + 80, y + 25, "R1", 30, WHITE, "middle", "bold")
    s.rect(RX + 136, y, 96, 34, PANEL, rx=6)
    s.text(RX + 184, y + 25, "R2", 30, GRAY, "middle", "bold")
    s.line(RX + 140, y + 17, RX + 228, y + 17, GRAY, 4)

    s.text(RX + CARD_W / 2, 340, "R1 only", 30, INK, "middle", "bold")
    s.text(RX + CARD_W / 2, 400, "单端运行损失分辨", 32, INK, "middle", "bold")

    s.rect(RX + CARD_W / 2 - 92, 440, 184, 56, CYAN_TINT, CYAN, 4, rx=12)
    s.text(RX + CARD_W / 2, 479, "merge = 0", 30, CYAN_DEEP, "middle", "bold")
    s.text(RX + CARD_W / 2, 536, "single-end", 30, GRAY, "middle")

    # 结论（方案原句第 3 段）
    s.text(400, 644, "两条退路皆有代价", 32, BLUE, "middle", "bold")

    s.save("35_merge_fallback_options.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

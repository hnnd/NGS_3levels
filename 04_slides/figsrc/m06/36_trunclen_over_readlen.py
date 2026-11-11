#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""36_trunclen_over_readlen.py — FIG-M06-36 truncLen 超读长两种现场

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-36（P64，cols 一栏
800×700，new-svg）。
教材依据：§18.5.5（truncLen 超过实际读长时：全样本超长 → 全部过滤为 0、写出精简
track 表后报错退出；个别低质量样本超长 → 部分为 0、下游跳过留 NA、不报总错）。
图内汉字 = 方案原句逐字，共 25 字（全样本超长报错退出 / 个别超长静默留空 /
先看警告后查表格）；其余标注为 track 表字段名、0/NA 值与程序动作。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 36_trunclen_over_readlen.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403
from svghelp import (BLUE, CYAN, CYAN_DEEP, CYAN_TINT, GRAY, GREEN, GREEN_TINT,
                     INK, ORANGE, ORANGE_DEEP, ORANGE_TINT, PANEL, RED, SVG,
                     WHITE)

CY, CARD_W, CARD_H = 112, 344, 392
LX, RX = 34, 422


def main():
    s = SVG(800, 700)

    def table(x, y, name, value, ink, fill, stroke=None):
        s.rect(x + 24, y, CARD_W - 48, 46, fill, stroke, 3, rx=8)
        s.text(x + 42, y + 31, name, 30, INK, "start", "bold")
        s.text(x + CARD_W - 42, y + 31, value, 30, ink, "end", "bold")

    # ---------------- 现场 1：全样本超长 → 报错退出 ----------------
    s.rect(LX, CY, CARD_W, CARD_H, WHITE, BLUE, 4, rx=16)
    s.text(LX + CARD_W / 2, CY + 44, "1", 32, ORANGE_DEEP, "middle", "bold")
    s.text(LX + CARD_W / 2, CY + 100, "全样本超长报错退出", 30, INK, "middle",
           "bold")
    table(LX, CY + 132, "reads.in", "0", INK, PANEL)
    table(LX, CY + 192, "reads.out", "0", INK, PANEL)

    # 红：报错退出 —— 全图唯一警示（叉 2 笔）
    s.cross(LX + CARD_W / 2, CY + 288, 28, RED, 8)
    s.text(LX + CARD_W / 2, CY + 360, "stop", 30, GRAY, "middle", "bold")

    # ---------------- 现场 2：个别超长 → 静默留 NA ----------------
    s.rect(RX, CY, CARD_W, CARD_H, WHITE, BLUE, 4, rx=16)
    s.text(RX + CARD_W / 2, CY + 44, "2", 32, ORANGE_DEEP, "middle", "bold")
    s.text(RX + CARD_W / 2, CY + 100, "个别超长静默留空", 30, INK, "middle",
           "bold")
    table(RX, CY + 132, "reads.out", "0", ORANGE_DEEP, ORANGE_TINT, ORANGE)
    table(RX, CY + 192, "sample", "NA", CYAN_DEEP, CYAN_TINT, CYAN)

    # 静默：虚线 + skip（不警示，灰）
    s.line(RX + 60, CY + 274, RX + CARD_W - 60, CY + 274, GRAY, 4, dash="10 8")
    s.text(RX + CARD_W / 2, CY + 320, "skip", 30, GRAY, "middle", "bold")
    s.text(RX + CARD_W / 2, CY + 360, "no error", 30, GRAY, "middle")

    # 排查动作（绿）
    s.rect(158, 542, 484, 68, GREEN_TINT, GREEN, 4, rx=14)
    s.text(400, 587, "先看警告后查表格", 32, GREEN, "middle", "bold")

    s.text(400, 662, "truncLen > read length", 30, GRAY, "middle")

    s.save("36_trunclen_over_readlen.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_one_table_two_plots.py — 生成 01_one_table_two_plots.svg
（FIG-U02-01：同一张表，两张图——设例场景）

方案：reviews/course/U02_FIGP_001.md §4 FIG-U02-01（P10，cols 一栏，viewBox 800×700）。
数据（全部教材 §3.1 L10 设例）：12 行表、两组各 6 行、q30 有 3 个 NA、
散点剩 9 个点（控制台 Removed 3 rows）、柱图均值用 na.rm 跳过缺失、
显式 levels=c("treat","control") 组序调头。柱高为设例均值（control 5 个非缺失、
treat 4 个非缺失），仅示意「看着正常」。
红 2 处（满额）：NA 格红底 + 缺失点位红描边。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 01_one_table_two_plots.py
"""
from svghelp import *  # noqa: F401,F403

ROWS = [
    ("control", "32.5"), ("control", "31.8"), ("control", "NA"),
    ("control", "33.1"), ("control", "30.9"), ("control", "32.2"),
    ("treat", "34.0"), ("treat", "NA"), ("treat", "33.5"),
    ("treat", "NA"), ("treat", "34.2"), ("treat", "33.8"),
]
NA_IDX = {i for i, r in enumerate(ROWS) if r[1] == "NA"}
CTRL_VALS = [32.5, 31.8, 33.1, 30.9, 32.2]
TREAT_VALS = [34.0, 33.5, 34.2, 33.8]
CTRL_MEAN = sum(CTRL_VALS) / len(CTRL_VALS)      # 32.1（设例）
TREAT_MEAN = sum(TREAT_VALS) / len(TREAT_VALS)   # 33.875（设例）


def table(s):
    s.text(150, 52, "设例 12 行", 32, BLUE, "middle", "bold")
    s.rect(24, 76, 276, 40, BLUE)
    s.text(90, 105, "group", 30, WHITE, "middle", "bold")
    s.text(228, 105, "q30", 30, WHITE, "middle", "bold")
    for i, (g, v) in enumerate(ROWS):
        y = 116 + i * 38
        fill = WHITE if i % 2 == 0 else BLUE_TINT
        s.rect(24, y, 276, 38, fill)
        s.line(156, y, 156, y + 38, PANEL, 2)
        s.text(90, y + 28, g, 30, INK, "middle")
        if i in NA_IDX:
            s.rect(158, y + 3, 140, 32, RED)
            s.text(228, y + 28, "NA", 30, WHITE, "middle", "bold")
        else:
            s.text(228, y + 28, v, 30, INK, "middle")
    s.rect(24, 116, 276, 456, "none", BLUE, 3)
    s.text(150, 620, "3 个缺失", 32, INK, "middle", "bold")


def ymap(v):
    return 300 - (v - 29.5) * 31.25


def scatter(s):
    s.text(564, 52, "散点：剩 9 个点", 32, INK, "middle", "bold")
    s.rect(352, 76, 424, 264, WHITE, BLUE, 4, rx=8)
    s.line(392, 96, 392, 300, INK, 3)
    s.line(392, 300, 748, 300, INK, 3)
    for v in (30, 32, 34, 36):
        y = ymap(v)
        s.line(384, y, 392, y, INK, 3)
        s.text(376, y + 10, str(v), 30, GRAY, "end")
    for gx, name in ((480, "control"), (640, "treat")):
        s.text(gx, 332, name, 30, GRAY, "middle")
    jit = [-30, 0, 30, -15, 15]
    for j, v in enumerate(CTRL_VALS):
        s.circle(480 + jit[j], ymap(v), 11, GREEN)
    for j, v in enumerate(TREAT_VALS):
        s.circle(640 + jit[j], ymap(v), 11, GREEN)
    for gx, dx in ((480, -30), (480, 30), (640, 0)):
        s.circle(gx + dx, ymap(32.9), 11, "none", RED, 3, dash="7 6")
    s.rect(352, 352, 424, 44, PANEL, rx=6)
    s.text(564, 383, "Removed 3 rows", 30, GRAY, "middle")


def bars(s):
    s.text(470, 436, "柱图：均值看着正常", 32, INK, "middle", "bold")
    s.text(706, 436, "组序调头", 32, ORANGE, "middle", "bold")
    s.rect(352, 456, 424, 184, WHITE, BLUE, 4, rx=8)
    s.line(392, 610, 748, 610, INK, 3)
    base, scale = 610, 4.28
    bw = 90
    for gx, mean, name in ((455, CTRL_MEAN, "control"), (645, TREAT_MEAN, "treat")):
        h = mean * scale
        s.rect(gx - bw / 2, base - h, bw, h, ORANGE)
        s.text(gx, base - h + 34, "na.rm", 30, WHITE, "middle", "bold")
        s.text(gx, 646, name, 30, GRAY, "middle")
    s.arrow(592, 540, 508, 540, ORANGE, 6)
    s.arrow(508, 540, 592, 540, ORANGE, 6)


def main():
    assert len(ROWS) == 12 and len(NA_IDX) == 3
    assert len(CTRL_VALS) + len(TREAT_VALS) == 9
    s = SVG(800, 700)
    table(s)
    scatter(s)
    bars(s)
    s.save("01_one_table_two_plots.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

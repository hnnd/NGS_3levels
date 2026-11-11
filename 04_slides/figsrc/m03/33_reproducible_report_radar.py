#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""33_reproducible_report_radar.py — 生成 33_reproducible_report_radar.svg
（FIG-M03-33：可复核变异检测报告八项要素雷达卡）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-33（P68，cols 一栏，800×700）。
图内中文按方案（八项要素 登录号 倍性 去重率 可判定区 计数 自比对照）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文；参数与指标名
（-ploidy 1、PERCENT_DUP、Ts/Tv）保留英文，字数不再按 ≤30 字核验。
依据：教材 §10.6（L386–411）。无网络、无随机数。
"""
import math

from svghelp import *  # noqa: F401,F403

ITEMS = [
    ("登录号", "参考登录号"),
    ("", "工具版本"),
    ("倍性", "-ploidy 1"),
    ("去重率", "PERCENT_DUP"),
    ("可判定区", "可判定比例"),
    ("计数", "过滤计数"),
    ("", "Ts/Tv"),
    ("自比对照", "自比核查"),
]


def main():
    s = SVG(800, 700)
    s.text(400, 46, "八项要素", 38, INK, "middle", "bold")

    cx, cy, R = 400, 360, 180
    for r in (0.33, 0.66, 1.0):
        pts = [(cx + R * r * math.cos(-math.pi / 2 + i * math.pi / 4),
                cy + R * r * math.sin(-math.pi / 2 + i * math.pi / 4))
               for i in range(8)]
        s.polygon(pts + [pts[0]], "none", PANEL, 3)
    pts = [(cx + R * 0.85 * math.cos(-math.pi / 2 + i * math.pi / 4),
            cy + R * 0.85 * math.sin(-math.pi / 2 + i * math.pi / 4))
           for i in range(8)]
    s.polygon(pts + [pts[0]], GREEN_TINT, GREEN, 5)
    for i, (zh, en) in enumerate(ITEMS):
        ang = -math.pi / 2 + i * math.pi / 4
        x1, y1 = cx + R * math.cos(ang), cy + R * math.sin(ang)
        s.line(cx, cy, x1, y1, PANEL, 3)
        lx, ly = cx + (R + 66) * math.cos(ang), cy + (R + 56) * math.sin(ang)
        anchor = "middle"
        if math.cos(ang) > 0.4:
            anchor = "start"
        elif math.cos(ang) < -0.4:
            anchor = "end"
        if zh:
            s.text(lx, ly, zh, 30, BLUE, anchor, "bold")
            s.text(lx, ly + 30, en, 30, GRAY, anchor)
        else:
            s.text(lx, ly + 12, en, 30, GRAY, anchor)
        s.circle(pts[i][0], pts[i][1], 8, GREEN)

    s.circle(cx, cy, 54, WHITE, GREEN, 5)
    s.text(cx, cy - 2, "✓", 42, GREEN, "middle", "bold")
    s.text(cx, cy + 28, "PASS", 30, GREEN, "middle", "bold")

    s.rect(40, 650, 720, 44, RED_TINT, RED, 4, rx=14)
    s.text(400, 682, "缺任一项 = 不可复核", 30, RED, "middle",
           "bold")
    s.save("33_reproducible_report_radar.svg")


if __name__ == "__main__":
    main()

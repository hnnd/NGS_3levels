#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_three_accounts_funnel.py — 生成 11_three_accounts_funnel.svg
（FIG-M01-13：深度规划三本账漏斗结构）

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-13（P31，cols 一栏，800×700）。
依据：教材 §13.4.4 L203, L236；讲义 ④4.7。无数字、无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 11_three_accounts_funnel.py
"""
from svghelp import *  # noqa: F401,F403

LAYERS = [
    (90, [(100, 90), (700, 90), (640, 230), (160, 230)], BLUE,
     "① 覆盖度账：测到了吗", "e^(−C)", 685),
    (250, [(160, 250), (640, 250), (580, 390), (220, 390)], CYAN_DEEP,
     "② 共识账：测对了吗", "Bin(d, ε)", 625),
    (410, [(220, 410), (580, 410), (520, 550), (280, 550)], PURPLE,
     "③ 换算账：下单多少", "Gb", 570),
]


def main():
    s = SVG(800, 700)
    for ytop, pts, color, label, side, sx in LAYERS:
        s.polygon(pts, color)
        cy = ytop + 70
        s.text(400, cy + 12, label, 32, WHITE, "middle", "bold")
        s.text(sx, cy + 12, side, 30, GRAY, "start")

    # 红色警示（全图唯一红色）
    s.rect(170, 592, 460, 64, RED, rx=14)
    s.text(400, 636, "三本账不可顶替", 34, WHITE, "middle", "bold")

    s.save("11_three_accounts_funnel.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

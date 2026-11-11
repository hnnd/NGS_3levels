#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_zmw_smrtbell.py — 生成 04_zmw_smrtbell.svg（FIG-U03-04：ZMW 与 SMRTbell）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-04（P21，cols 一栏，800×700）。
教材依据：chapters/ch04/manuscript.qmd §4.4.3。
上半：零模波导孔剖面（金属膜微孔 + 衰减波只照孔底纳米薄层）；
下半：SMRTbell 双端发夹接头闭合成环，聚合酶绕环多圈重读。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 04_zmw_smrtbell.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 50, "零模微孔照孔底，发夹闭合成环", 34, BLUE, "middle", "bold")
    s.text(400, 92, "绕环多圈重读", 30, GRAY, "middle", "bold")

    # ── 上半：ZMW 剖面 ──
    s.rect(40, 120, 720, 250, WHITE, PANEL, 3, rx=16)
    s.text(70, 162, "零模波导孔（ZMW）", 30, BLUE, "start", "bold")
    # 激光光锥（纯色橙）
    s.polygon([(300, 180), (500, 180), (430, 250), (370, 250)], ORANGE)
    # 金属膜（带孔）
    s.rect(60, 250, 680, 44, GRAY, rx=6)
    s.rect(370, 244, 60, 56, PAPER)  # 孔洞（透出纸底色）
    # DNA 链穿过孔底 + 锚定的聚合酶
    s.polyline([(400, 210), (400, 284)], CYAN_DEEP, 6)
    s.circle(400, 290, 12, CYAN_DEEP)
    # 孔底观测区（红框）
    s.rect(310, 308, 180, 46, RED_TINT, RED, 4, rx=8)
    s.text(400, 341, "观测体积 20 zL", 30, RED, "middle", "bold")

    # ── 下半：SMRTbell 环化重读 ──
    s.rect(40, 400, 720, 270, WHITE, PANEL, 3, rx=16)
    s.text(70, 442, "SMRTbell", 30, BLUE, "start", "bold")
    # 哑铃状文库：两端发夹接头（橙）+ 双链 DNA（青）
    s.rect(150, 520, 70, 40, ORANGE, rx=18)
    s.rect(580, 520, 70, 40, ORANGE, rx=18)
    s.rect(215, 528, 370, 24, CYAN, rx=10)
    # 绕环多圈箭头
    s.path("M 620 500 C 700 440, 110 440, 170 502", None, 0)
    s.path("M 616 494 C 690 436, 120 436, 174 496",
           GREEN, 7, dash="2 14")
    s.polygon([(170, 502), (200, 500), (184, 524)], GREEN)
    # subreads 标记
    for i, lab in enumerate(["R1", "R2", "R3"]):
        s.rect(310 + i * 110, 590, 80, 44, BLUE_TINT, BLUE, 3, rx=10)
        s.text(350 + i * 110, 622, lab, 30, BLUE, "middle", "bold")
    s.text(90, 622, "subreads →", 28, GRAY, "start", "bold")

    s.save("04_zmw_smrtbell.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

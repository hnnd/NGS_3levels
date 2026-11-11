#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_tech_timeline_two_baselines.py — 生成 18_tech_timeline_two_baselines.svg
（FIG-P02-22：技术代际分水岭与两条不变的底线）

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-22（Slide 44，cols 一栏，800×700）。
依据：教材 §17.4.12 L278–288、图 17-7。纯示意：平台名与技术代际取教材口径，
不标具体年份（年份拿不准就不写）；无数据、无随机数、无网络。
图内汉字 = 方案指定整句逐字一致（27 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 18_tech_timeline_two_baselines.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "全转录组探索，靶向成像验证。模型变大，统计单位与注释底线不变。"


def track(s, y, chips, color):
    s.line(60, y, 740, y, color, 4)
    for cx, label in chips:
        s.chip(cx, y, label, 30, WHITE, color, color, pad=14, anchor="middle")


def main():
    s = SVG(800, 700, "Two technology tracks and two fixed baselines", plan=TEXT)

    s.text(40, 96, "SPATIAL", 30, BLUE, "start", "bold")
    track(s, 150, ((180, "Visium"), (400, "Stereo-seq"), (620, "Xenium")), BLUE)

    s.text(40, 236, "SINGLE CELL", 30, BLUE, "start", "bold")
    track(s, 290, ((180, "Drop-seq"), (400, "Chromium"), (620, "scGPT")),
          CYAN_DEEP)

    for cx, lab in ((70, "2015"), (400, "2020"), (730, "2026")):
        s.text(cx, 350, lab, 30, GRAY, "middle")

    # 两条底线（不随技术代际变化）
    s.rect(40, 386, 460, 52, BLUE_TINT, BLUE, 3, rx=10)
    s.text(56, 421, "UNIT = INDIVIDUAL", 30, BLUE, "start", "bold")
    s.rect(40, 456, 460, 52, BLUE_TINT, BLUE, 3, rx=10)
    s.text(56, 491, "ANNOT = SPECIES PRIOR", 30, BLUE, "start", "bold")

    # 红色（1 处）：两条底线不随模型变大而改变
    s.line(546, 378, 546, 514, RED, 5)
    s.line(536, 378, 556, 378, RED, 5)
    s.line(536, 514, 556, 514, RED, 5)
    s.text(574, 454, "UNCHANGED", 32, RED, "start", "bold")

    s.caption(["全转录组探索，靶向成像验证。",
               "模型变大，统计单位与注释底线不变。"], [INK, INK], 30, top=540)
    s.save("18_tech_timeline_two_baselines.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())

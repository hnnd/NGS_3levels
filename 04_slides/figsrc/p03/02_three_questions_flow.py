#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_three_questions_flow.py — 生成 02_three_questions_flow.svg
（FIG-P03-02：第 11 页 cols 一栏「三大科学问题逻辑有向链」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-02（P11，cols，800×700）。
依据：教材 §16.1 L138–144——归谁（竞争比对分流读段）→ 怎么归一（两个独立容器
各自建模）→ 能问什么（时序共线与相对比较边界），三步有严格逻辑依赖，颠倒则上游
错误在下游成倍放大。
图内中文严格取方案给定 24 字（4 句）；序号用阿拉伯数字，不放英文说明文字；
「上游错误越往下游越放大」用三级加粗的同向箭头来表达，不另加中文。
配色：青蓝→深蓝→紫示逻辑进阶，红色只标「顺序不可颠倒」一处警示。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 02_three_questions_flow.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["一查歧义归属", "二分归一分母", "三限时序边界", "顺序不可颠倒"]
TEXT = "".join(PHRASES)
STEPS = [(CYAN, CYAN_DEEP, CYAN_TINT), (BLUE, BLUE, BLUE_TINT),
         (PURPLE, PURPLE, PURPLE_TINT)]


def card(s, x, y, num, phrase, main, deep, tint):
    s.panel(x, y, 214, 200, tint, main, 4)
    s.rect(x, y, 214, 14, main)
    s.circle(x + 107, y + 76, 32, WHITE, main, 4)
    s.text(x + 107, y + 88, num, 32, deep, "middle", "bold")
    s.text(x + 107, y + 166, phrase, 30, deep, "middle", "bold")


def thick(s, x0, x1, y, w):
    """扁平粗箭头（杆 + 三角头），粗细由 w 决定：读作「越往下游越被放大」。"""
    half, head = w / 2, max(14, 1.9 * w)
    s.polygon([(x0, y - half), (x1 - head, y - half), (x1 - head, y - 1.7 * head),
              (x1, y), (x1 - head, y + 1.7 * head), (x1 - head, y + half),
              (x0, y + half)], BLUE)


def main():
    s = SVG(800, 700, "Three questions in strict order", plan=TEXT)

    # ---------- 三段串联：归谁 → 怎么归一 → 能问什么 ----------
    xs = (36, 293, 550)
    for x, num, ph, (main, deep, tint) in zip(xs, "123", PHRASES[:3], STEPS):
        card(s, x, 70, num, ph, main, deep, tint)
    for x0, x1 in ((250, 293), (507, 550)):
        s.arrow(x0, 170, x1, 170, BLUE, 6, 15)

    # ---------- 上游错误沿链条被放大：三支同向箭头，一支比一支粗 ----------
    for i, x in enumerate(xs):
        thick(s, x + 12, x + 200, 356, 7 + 8 * i)

    # ---------- 反向红色虚线：顺序一旦颠倒，下游全部失效 ----------
    s.path("M 764 430 Q 400 508 40 436", RED, 5, dash="12 9")
    s.polygon([(40, 436), (62, 415), (58, 446)], RED)

    s.band(150, 540, 500, 74, PHRASES[3], RED, WHITE, 32)
    s.save("02_three_questions_flow.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 24, TEXT
    raise SystemExit(main())

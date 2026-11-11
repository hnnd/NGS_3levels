#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_blue_vs_blup_shrinkage.py — 生成 04_blue_vs_blup_shrinkage.svg
（FIG-P05-04：P17「BLUE 还是 BLUP：差别在收缩」，cols 左栏）【new-svg】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-04（800×700，中文共 26 字）。
依据：教材 §21.4.2——BLUE 把基因型当固定效应，不做收缩，保留物理量纲，但
低重复时噪声大；BLUP 把基因型当随机效应，向群体均值 μ 收缩，抗噪但压缩了
品种间方差，等于轻微降功效。
图内中文严格取方案给定两句（10 + 16 = 26 字），后半句拆成两行，末行
「但压缩方差」标红（方案指定的红标位置）；散点为示意值，不含实测数字。
配色：青蓝＝BLUE 无收缩估计，橙＝BLUP 收缩估计；红色只标「压缩方差」一处。
无网络；不涉及随机数（点位写死，仅作几何示意）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 04_blue_vs_blup_shrinkage.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["固定效应无收缩保量纲",                    # 10
           "随机效应向均值收缩抗噪但压缩方差"]         # 16
TEXT = "".join(PHRASES)
R1, R2 = "随机效应向均值收缩抗噪", "但压缩方差"       # 合起来＝PHRASES[1]

# 5 个品种的示意观测值（无单位；仅用来画收缩方向）
OBS = [100, 180, 340, 400]


def main():
    s = SVG(800, 700, "BLUE versus BLUP shrinkage", plan=TEXT)
    mu = 260.0                       # 群体均值 μ（示意）

    # ---------- 左面板：BLUE，固定效应，不收缩 ----------
    s.rect(40, 60, 330, 370, CYAN_TINT, CYAN, 5, rx=16)
    s.text(205, 106, "BLUE", 32, CYAN_DEEP, "middle", "bold")
    for i, y in enumerate(OBS):
        cx = 96 + i * 62
        s.line(cx, 424, cx, y + 14, CYAN, 3, dash="8 6")
        s.circle(cx, y, 13, WHITE, CYAN, 5)
    s.line(70, 430, 340, 430, CYAN_DEEP, 4)

    # ---------- 右面板：BLUP，随机效应，向 μ 收缩 ----------
    s.rect(430, 60, 330, 370, ORANGE_TINT, ORANGE, 5, rx=16)
    s.text(595, 106, "BLUP", 32, ORANGE, "middle", "bold")
    s.line(456, mu, 734, mu, GRAY, 4, dash="12 8")
    s.text(468, mu - 16, "μ", 30, GRAY, "start", "bold")
    shrunk = [mu + (y - mu) * 0.35 for y in OBS]
    for i, (y, ys) in enumerate(zip(OBS, shrunk)):
        cx = 512 + i * 62
        s.line(cx, 424, cx, max(y, ys) + 14, ORANGE, 3, dash="8 6")
        s.circle(cx, y, 13, WHITE, ORANGE, 5)
        s.arrow(cx, y + (16 if ys > y else -16),
                cx, ys + (-17 if ys > y else 17), "#C86A4D", 4, 13)
        s.circle(cx, ys, 8, ORANGE)
    s.line(456, 430, 734, 430, ORANGE, 4)

    # ---------- 两句结论 ----------
    s.text(205, 486, PHRASES[0], 32, CYAN_DEEP, "middle", "bold")
    s.text(595, 486, R1, 32, ORANGE, "middle", "bold")
    w = s.seg(595, 542, [(R2, RED)], 32, "middle", "bold")

    # ---------- 决策提示（只用工具名与数字，不占汉字预算）----------
    s.chip(190, 618, "balanced → BLUE", 30, WHITE, CYAN, CYAN_DEEP,
           anchor="middle")
    s.chip(510, 618, "unbalanced → BLUP", 30, WHITE, ORANGE,
           "#C86A4D", anchor="middle")
    s.save("04_blue_vs_blup_shrinkage.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 26, TEXT
    assert R1 + R2 == PHRASES[1]
    raise SystemExit(main())

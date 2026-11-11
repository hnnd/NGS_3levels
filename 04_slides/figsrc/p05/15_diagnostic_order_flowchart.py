#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_diagnostic_order_flowchart.py — 生成 15_diagnostic_order_flowchart.svg
（FIG-P05-15：P33「诊断顺序不能反：QQ → λ → 曼哈顿」，cols 左栏）【new-svg】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-15（800×700，中文共 26 字）。
依据：教材 §21.4.5——诊断三图的阅读顺序是先看分位图（QQ）贴合度、再算膨胀
因子 λ 量化整体抬升，前两步过关才允许看曼哈顿图找峰；反过来「先挑峰再倒查
QQ」会在整体抬升时把满屏假峰当成发现（教材 §21.5.2 的失效模式）。
图内中文严格取方案给定三句（11 + 7 + 8 = 26 字），第一句拆成两步。
配色：青蓝＝正向顺序流，绿＝合格放行；红色只标「逆向挑峰」这条错路一处。
无网络；不涉及随机数（纯流程示意，无计算结果）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 15_diagnostic_order_flowchart.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["先读分位图再算膨胀因子",   # 11
           "过关方看曼哈顿",          # 7
           "逆向挑峰全盘皆错"]         # 8
TEXT = "".join(PHRASES)
S1, S2 = "先读分位图", "再算膨胀因子"      # 合起来＝PHRASES[0]


def qq_icon(s, cx, cy):
    """QQ 图小图标：对角线 + 贴合点 + 尾部翘起点。"""
    s.line(cx - 34, cy + 34, cx + 34, cy - 34, GRAY, 3, dash="7 6")
    for i in range(4):
        s.circle(cx - 24 + i * 16, cy + 24 - i * 16, 4, CYAN_DEEP)
    s.circle(cx + 22, cy - 30, 5, ORANGE)


def lambda_icon(s, cx, cy):
    """λ 图标：一条基准线与一个抬起的刻度。"""
    s.line(cx - 40, cy + 20, cx + 40, cy + 20, GRAY, 3)
    s.line(cx - 40, cy - 16, cx + 40, cy - 16, CYAN, 3, dash="8 6")
    s.text(cx + 4, cy + 8, "λ", 30, CYAN_DEEP, "middle", "bold")


def manhattan_icon(s, cx, cy):
    """曼哈顿图小图标：连片峰 + 阈值线。"""
    s.line(cx - 44, cy + 26, cx + 44, cy + 26, GRAY, 3)
    s.line(cx - 44, cy - 18, cx + 44, cy - 18, GREEN, 3, dash="8 6")
    for i, h in enumerate((6, 12, 20, 30, 38, 30, 20, 12, 6)):
        s.rect(cx - 40 + i * 10, cy + 26 - h, 6, h, CYAN, None, 0)


def main():
    s = SVG(800, 700, "Diagnostic reading order", plan=TEXT)

    # ---------- 三步正向流程 ----------
    steps = [(PHRASES[1][:0] + S1, BLUE, qq_icon),
             (S2, BLUE, lambda_icon),
             (PHRASES[1], GREEN, manhattan_icon)]
    for i, (label, col, icon) in enumerate(steps):
        top = 50 + i * 145
        s.rect(96, top, 520, 112, WHITE, col, 5, rx=14)
        icon(s, 176, top + 56)
        s.text(240, top + 70, label, 34, col, "start", "bold")
        if i < 2:
            s.arrow(356, top + 112, 356, top + 145, CYAN_DEEP, 5, 13)

    # ---------- 逆向挑峰：红叉拦截（唯一红色警示）----------
    s.path("M 640 420 C 706 400 706 190 640 106", RED, 5, dash="14 9")
    s.polygon([(640, 106), (662, 128), (622, 130)], RED)
    s.cross(700, 262, 26, RED)
    s.text(400, 596, PHRASES[2], 32, RED, "middle", "bold")

    s.save("15_diagnostic_order_flowchart.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 26, TEXT
    assert S1 + S2 == PHRASES[0]
    raise SystemExit(main())

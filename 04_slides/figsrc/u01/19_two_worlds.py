#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_two_worlds.py — 生成 19_two_worlds.svg
（FIG-U01-19：同一脚本，两个世界——交互终端 vs qsub 作业）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-19（P56，cols 一栏，800×700）。
数据：无数字。
依据：教材 §1.5.2 L273（调度器以新 shell 拉起，不重放终端状态）、
§1.5.2 后果段（命中系统旧版，能看但不对）；修复两行见 deck P47 代码。
层级控制：不画 BASH_ENV/-V 细节（§1.4.10 博士块不上屏）。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 19_two_worlds.py
"""
from svghelp import *  # noqa: F401,F403


def check(s, x, y, col):
    s.line(x, y, x + 13, y + 13, col, 7, cap="round")
    s.line(x + 13, y + 13, x + 36, y - 17, col, 7, cap="round")


def cross(s, x, y, col):
    s.line(x, y, x + 26, y + 26, col, 7, cap="round")
    s.line(x + 26, y, x, y + 26, col, 7, cap="round")


def main():
    s = SVG(800, 700)

    # 标题
    s.text(400, 56, "终端有的，作业未必有", 38, BLUE, "middle", "bold")

    # 左栏：交互终端（绿勾列；拉丁小标签 login shell）
    s.rect(50, 96, 330, 400, WHITE, GREEN, 5, rx=14)
    s.text(215, 140, "login shell", 30, GREEN, "middle", "bold", family=MONO)
    for yy, label in ((200, "激活"), (320, "PATH"), (440, "命中")):
        check(s, 90, yy, GREEN)
        s.text(150, yy + 24, label, 32, INK, "bold")

    # 右栏：qsub 作业（红叉列；拉丁小标签 qsub job）
    s.rect(420, 96, 330, 400, WHITE, RED, 5, rx=14)
    s.text(585, 140, "qsub job", 30, RED, "middle", "bold", family=MONO)
    for yy, label in ((200, "无激活"), (320, "PATH 初始"), (440, "旧版")):
        cross(s, 460, yy, RED)
        s.text(520, yy + 24, label, 32, INK, "bold")
    # 红色小标签：旧版更险（红第 2 处）
    s.rect(618, 420, 150, 44, RED, rx=8)
    s.text(693, 451, "旧版更险", 30, WHITE, "middle", "bold")

    # 底部绿色描边横幅 = 修复出口
    s.rect(120, 560, 560, 84, GREEN_TINT, GREEN, 5, rx=14)
    s.text(400, 612, "显式激活＋真跑", 36, GREEN, "middle", "bold")

    s.save("19_two_worlds.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

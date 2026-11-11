#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_redirect_order.py — 生成 05_redirect_order.svg
（FIG-U01-05：重定向的顺序决定效果——两行命令的 fd 走向对照）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-05（P20，cols 一栏，800×700）。
数据：无数字（行为示意）。
依据：教材 §1.4.4 L99–109（`命令 > run.log 2>&1` vs `命令 2>&1 > run.log`）。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 05_redirect_order.py
"""
from svghelp import *  # noqa: F401,F403


def file_icon(s, x, y, ok):
    """run.log 文件图标；ok=True 加绿色勾。"""
    s.rect(x, y, 130, 100, WHITE, BLUE, 4, rx=8)
    s.text(x + 65, y + 42, "run.log", 30, INK, "middle", family=MONO)
    s.line(x + 16, y + 56, x + 114, y + 56, PANEL, 3)
    s.line(x + 16, y + 68, x + 96, y + 68, PANEL, 3)
    if ok:
        s.line(x + 38, y + 84, x + 52, y + 94, GREEN, 6, cap="round")
        s.line(x + 52, y + 94, x + 82, y + 66, GREEN, 6, cap="round")


def screen_icon(s, x, y):
    """终端屏幕图标（红框=报错仍在此）。"""
    s.rect(x, y, 140, 100, WHITE, RED, 5, rx=8)
    s.text(x + 70, y + 46, "终端屏幕", 30, RED, "middle", "bold")
    s.line(x + 20, y + 64, x + 66, y + 64, RED, 4, cap="round")
    s.line(x + 20, y + 80, x + 98, y + 80, RED, 4, cap="round")


def fd_dot(s, x, y, n, color):
    s.circle(x, y, 19, color)
    s.text(x, y + 11, str(n), 30, WHITE, "middle", "bold")


def main():
    s = SVG(800, 700)

    # 顶部红色警示标题
    s.text(400, 56, "顺序反了，报错不进日志", 38, RED, "middle", "bold")

    # ===== 上行：命令 > run.log 2>&1（正确序）=====
    s.rect(40, 96, 330, 56, INK, rx=8)
    s.text(58, 134, "命令 > run.log 2>&1", 30, WHITE)
    file_icon(s, 596, 92, ok=True)
    # 1 号（深蓝）先直指文件
    fd_dot(s, 402, 124, 1, BLUE)
    s.arrow(424, 124, 590, 124, BLUE, 6)
    # 2 号（橙）中途汇入 1 号
    fd_dot(s, 402, 192, 2, ORANGE)
    s.line(424, 192, 470, 192, ORANGE, 6, cap="round")
    s.line(470, 192, 470, 124, ORANGE, 6, cap="round")
    s.arrow(470, 124, 536, 124, ORANGE, 6)
    s.text(660, 226, "两条都进文件", 32, GREEN, "middle", "bold")

    # ===== 下行：命令 2>&1 > run.log（错误序）=====
    s.rect(40, 380, 330, 56, INK, rx=8)
    s.text(58, 418, "命令 2>&1 > run.log", 30, WHITE)
    screen_icon(s, 250, 470)
    file_icon(s, 596, 470, ok=False)
    # 2 号（橙）先跟屏幕（向下）
    fd_dot(s, 402, 408, 2, ORANGE)
    s.arrow(402, 432, 402, 464, ORANGE, 6)
    s.line(402, 464, 400, 470, ORANGE, 6, cap="round")
    s.polygon([(400, 478), (390, 462), (410, 462)], ORANGE)
    # 1 号（蓝）后指文件（斜向）
    fd_dot(s, 452, 408, 1, BLUE)
    s.arrow(472, 420, 590, 500, BLUE, 6)
    s.text(320, 636, "报错仍在屏幕", 32, RED, "middle", "bold")

    s.save("05_redirect_order.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

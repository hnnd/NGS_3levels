#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_transfer_direction.py — 生成 18_transfer_direction.svg
（FIG-U01-18：传输的方向——来源在前，目标在后）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-18（P42，cols 一栏，800×700）。
数据：无数字。
依据：教材 §1.4.11 L253（命令语法「来源 目标」，回拉需在本地终端执行）；
deck P42 bullet（传输工具搬数据，会话工具只保会话）。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 18_transfer_direction.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 标题
    s.text(400, 56, "来源在前，目标在后", 40, BLUE, "middle", "bold")

    # 两端方框：本地电脑 / 集群
    s.rect(70, 120, 230, 110, BLUE_TINT, BLUE, 5, rx=14)
    s.text(185, 172, "本地电脑", 34, BLUE, "middle", "bold")
    s.rect(500, 120, 230, 110, BLUE_TINT, BLUE, 5, rx=14)
    s.text(615, 172, "集群", 34, BLUE, "middle", "bold")

    # 两条方向弧：绿=本地→集群（推），青=集群→本地（拉，须在本地敲）
    s.path("M 300 165 C 360 105, 440 105, 496 158", GREEN, 6)
    s.polygon([(500, 165), (482, 146), (478, 168)], GREEN)
    s.text(400, 108, "scp / rsync →", 30, GREEN, "middle", "bold",
           family=MONO)
    s.path("M 500 205 C 440 268, 360 268, 304 212", CYAN_DEEP, 6)
    s.polygon([(300, 205), (322, 208), (306, 224)], CYAN_DEEP)
    s.text(400, 292, "← 在本地敲命令", 30, CYAN_DEEP, "middle", "bold")

    # 错向警示：红叉箭头
    s.line(320, 420, 480, 420, RED, 6, cap="round")
    s.polygon([(480, 420), (462, 408), (462, 432)], RED)
    s.line(360, 396, 440, 444, RED, 6, cap="round")
    s.line(440, 396, 360, 444, RED, 6, cap="round")
    s.text(400, 492, "方向反＝覆盖", 34, RED, "middle", "bold")

    # 底部灰色一行
    s.text(400, 640, "tmux 只保会话", 32, GRAY, "middle", "bold")

    s.save("18_transfer_direction.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

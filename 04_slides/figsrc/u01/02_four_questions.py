#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_four_questions.py — 生成 02_four_questions.svg
（FIG-U01-02：一条命令的四个问题——whoami/hostname/pwd/#!）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-02（P14，cols 一栏，800×700）。
数据：无数字。
依据：教材 §1.4.1 L56–64（四问均可直接获取；L64 提示符会骗人，输出才算数）。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 02_four_questions.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 标题
    s.text(400, 58, "一条命令，四个问题", 40, BLUE, "middle", "bold")

    # 中央终端窗口轮廓（深蓝描边 + 标题栏）
    s.rect(90, 100, 620, 400, WHITE, BLUE, 5, rx=14)
    s.rect(90, 100, 620, 52, BLUE, rx=14)
    s.rect(90, 130, 620, 22, BLUE)  # 补齐标题栏下方圆角
    for i in range(3):
        s.circle(128 + i * 34, 126, 9, PANEL, GRAY, 3)
    s.text(400, 136, "terminal", 30, WHITE, "middle", family=MONO)

    # 四条问题徽章 2×2
    badges = [
        (170, 210, "谁", "whoami"),
        (440, 210, "哪台", "hostname"),
        (170, 380, "哪目录", "pwd"),
        (440, 380, "解释器", "#!"),
    ]
    bw, bh = 190, 120
    for bx, by, zh, en in badges:
        s.rect(bx, by, bw, bh, BLUE_TINT, BLUE, 4, rx=12)
        s.text(bx + bw / 2, by + 52, zh, 34, BLUE, "middle", "bold")
        s.text(bx + bw / 2, by + 94, en, 30, INK, "middle", family=MONO)

    # 底部红色横幅（唯一警示）
    s.rect(90, 560, 620, 90, RED_TINT, RED, 4, rx=12)
    s.text(400, 616, "提示符会骗人，输出才算数", 36, RED, "middle", "bold")

    s.save("02_four_questions.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

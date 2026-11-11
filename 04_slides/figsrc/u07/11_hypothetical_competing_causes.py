#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_hypothetical_competing_causes.py — 生成 11_hypothetical_competing_causes.svg（FIG-U07-11：假定蛋白偏高四类竞争解释）

方案：reviews/course/U07_FIGP_001.md §4.2 FIG-U07-11（P31，cols 一栏，viewBox 800×700）。
数据：无量字数字。类群选错 / 上游移码 / 短重叠群截断 / 真实新颖无近缘参考，
假定蛋白是排查触发器不是质量分数（教材 §9.4.5 L234–248、§9.5.1，D064 不设健康带）。
第 4 类原因汉字超限（方案清单未含），用英文标注。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 11_hypothetical_competing_causes.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 顶部橙色报警框
    s.rect(250, 52, 300, 72, ORANGE, rx=14)
    s.text(400, 99, "假定蛋白偏高", 34, INK, "middle", "bold")

    # 分叉连线
    s.line(400, 124, 400, 176, GRAY, 5)
    s.line(190, 176, 610, 176, GRAY, 5)
    boxes = [
        (60, 190, CYAN_DEEP, ["类群选错"]),
        (440, 190, PURPLE, ["上游移码"]),
        (60, 350, BLUE, ["短重叠群截断"]),
        (440, 350, GREEN, ["novel genes", "no near ref"]),
    ]
    for x, y, color, lines in boxes:
        s.line(x + 130, 176 if y == 190 else 310, x + 130, y, GRAY, 5)
        s.rect(x, y, 260, 120, WHITE, color, 6, rx=14)
        n = len(lines)
        for j, ln in enumerate(lines):
            yy = y + 60 + (j - (n - 1) / 2) * 40 + 10
            s.text(x + 130, yy, ln, 30, color if j == 0 else GRAY, "middle",
                   "bold" if j == 0 else None)

    # 底部红色行动横幅（唯一红色：审查非打分）
    s.rect(200, 560, 400, 60, RED, rx=12)
    s.text(400, 602, "审查非打分", 34, WHITE, "middle", "bold")

    s.save("11_hypothetical_competing_causes.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

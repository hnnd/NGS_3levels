#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_accept_four_steps.py — 生成 14_accept_four_steps.svg
（FIG-U01-14：验收四步——定位→版本→导入→真跑）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-14（P33，cols 一栏，800×700）。
数据：无数字（fastqc 0.12.1 等 pin 值留在 deck 文字，不进图）。
依据：教材 §2.4.3 L158–163（两层验证）、§2.4.8 L265–311（两类实测坑）、§2.5.3 L353–360。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 14_accept_four_steps.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 标题
    s.text(400, 56, "验收四步，一步不缺", 40, BLUE, "middle", "bold")

    # 四级台阶（自左下向右上；第④级绿描边=完成态）
    steps = [
        (30, 460, "① 定位", "command -v", BLUE, BLUE_TINT),
        (215, 390, "② 版本", "--version", BLUE, BLUE_TINT),
        (400, 320, "③ 导入", None, BLUE, BLUE_TINT),
        (585, 250, "④ 真跑", None, GREEN, GREEN_TINT),
    ]
    tw, th = 180, 78
    for sx, sy, name, hint, col, tint in steps:
        last = col == GREEN
        s.rect(sx, sy, tw, th, tint, col, 5 if last else 4, rx=12)
        s.text(sx + tw / 2, sy + 40, name, 32, col, "middle", "bold")
        if hint:
            s.text(sx + tw / 2, sy + 68, hint, 30, GRAY, "middle",
                   family=MONO)
        elif last:
            # 完成角标：绿圆白勾（不压文字）
            s.circle(sx + 164, sy + 14, 15, GREEN)
            s.line(sx + 158, sy + 14, sx + 162, sy + 19, WHITE, 4,
                   cap="round")
            s.line(sx + 162, sy + 19, sx + 170, sy + 7, WHITE, 4,
                   cap="round")
        else:
            s.polygon([(sx + 86, sy + 46), (sx + 86, sy + 66),
                       (sx + 102, sy + 56)], col)

    # 序列说明条
    s.rect(70, 556, 660, 52, WHITE, PANEL, 3, rx=10)
    s.text(400, 592, "定位→版本→导入→真跑", 32, INK, "middle", "bold")

    # 底部红色横幅
    s.rect(170, 622, 460, 58, RED_TINT, RED, 4, rx=12)
    s.text(400, 662, "缺真跑＝没验收", 34, RED, "middle", "bold")

    s.save("14_accept_four_steps.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

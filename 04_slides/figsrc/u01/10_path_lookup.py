#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_path_lookup.py — 生成 10_path_lookup.svg
（FIG-U01-10：PATH 依次去问——函数→内建→PATH，命中即停）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-10（P28，cols 一栏，800×700）。
数据：无数字。
依据：教材 §1.4.3 L90（查找顺序：函数内建优先、PATH 靠前优先）、L92（找到≠能跑）。
边界：bin/ 前插由 P30 图承载，本图不画（同概念一张图）。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 10_path_lookup.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 标题
    s.text(400, 56, "先函数，再内建，再 PATH", 38, BLUE, "middle", "bold")

    # 顶部节点：输入命令名
    s.rect(300, 92, 200, 64, BLUE, rx=12)
    s.text(400, 134, "输入命令名", 32, WHITE, "middle", "bold")

    # 查找链：函数？（灰）→ 内建？（灰）→ PATH 目录队列
    s.arrow(400, 160, 400, 208, GRAY, 5)
    s.rect(310, 214, 180, 60, PANEL, GRAY, 4, rx=10)
    s.text(400, 254, "函数？", 32, GRAY, "middle", "bold")
    s.line(512, 238, 538, 264, GRAY, 5, cap="round")
    s.line(538, 238, 512, 264, GRAY, 5, cap="round")

    s.arrow(400, 280, 400, 328, GRAY, 5)
    s.rect(310, 334, 180, 60, PANEL, GRAY, 4, rx=10)
    s.text(400, 374, "内建？", 32, GRAY, "middle", "bold")
    s.line(512, 358, 538, 384, GRAY, 5, cap="round")
    s.line(538, 358, 512, 384, GRAY, 5, cap="round")

    # PATH 目录队列：三个目录方块从左到右，首个命中绿勾
    s.arrow(400, 400, 400, 446, GRAY, 5)
    s.text(400, 486, "PATH：从左到右，命中即停", 30, INK, "middle")
    dirs = ["~/bin", "/opt/bin", "/usr/bin"]
    dx = [120, 330, 540]
    for i, (d, x) in enumerate(zip(dirs, dx)):
        hit = i == 1
        s.rect(x, 516, 160, 76, WHITE, GREEN if hit else BLUE, 5, rx=10)
        s.text(x + 80, 564, d, 30, INK, "middle", family=MONO)
        if hit:
            # 命中角标：绿圆白勾（不压文字）
            s.circle(x + 158, 512, 16, GREEN)
            s.line(x + 151, 512, x + 156, 518, WHITE, 4, cap="round")
            s.line(x + 156, 518, x + 165, 505, WHITE, 4, cap="round")
    s.arrow(284, 554, 324, 554, GRAY, 4)
    s.arrow(494, 554, 534, 554, GRAY, 4)

    # 底部红色横幅
    s.rect(200, 622, 400, 60, RED_TINT, RED, 4, rx=12)
    s.text(400, 664, "找到≠能跑", 34, RED, "middle", "bold")

    s.save("10_path_lookup.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

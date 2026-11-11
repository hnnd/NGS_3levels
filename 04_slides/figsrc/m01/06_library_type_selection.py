#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_library_type_selection.py — 生成 06_library_type_selection.svg
（FIG-M01-08：文库类型选择与转录本捕获/丢失）

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-08（P22，cols 一栏，800×700）。
依据：教材 §13.4.4 L240、§13.4.1 L90；讲义 ④4.3。无数字、无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 06_library_type_selection.py
"""
from svghelp import *  # noqa: F401,F403

ROWS = [
    # (y, 名称, 名称色, 捕获条宽, 丢失块, 右侧文字, 右侧文字色)
    (80, "WGS", BLUE, 420, None, None, None),
    (205, "polyA", BLUE, 280, (True,), "丢无尾转录本", RED),
    (330, "rRNA", BLUE, 380, None, "去除有效比例低", INK),
    (455, "非链特异", BLUE, 380, ("dir",), "丢转录方向", RED),
]


def main():
    s = SVG(800, 700)
    for y, name, ncol, bw, loss, note, ncol2 in ROWS:
        s.rect(50, y, 170, 76, ncol, rx=12)
        s.text(135, y + 49, name, 30, WHITE, "middle", "bold")
        s.rect(250, y, bw, 76, GREEN_TINT, GREEN, 3, rx=8)
        if loss and loss[0] is True:
            s.rect(250 + bw, y, 420 - bw, 76, "none", RED, 4, rx=8, dash="12 10")
        if loss and loss[0] == "dir":
            s.line(270, y + 38, 250 + bw - 20, y + 38, GRAY, 5)
            s.polygon([(270, y + 38), (286, y + 28), (286, y + 48)], GRAY)
            s.polygon([(250 + bw - 20, y + 38), (250 + bw - 36, y + 28),
                       (250 + bw - 36, y + 48)], GRAY)
        if note:
            if ncol2 is INK:
                s.text(618, y + 48, note, 30, ncol2, "end", "bold")
            else:
                s.text(560, y + 48, note, 30, ncol2, "start", "bold")

    # 底部警示条（深蓝底白字；红色额度留给两处「丢」字标注）
    s.rect(170, 585, 460, 62, BLUE, rx=14)
    s.text(400, 629, "选错下单即丢失", 34, WHITE, "middle", "bold")

    s.save("06_library_type_selection.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

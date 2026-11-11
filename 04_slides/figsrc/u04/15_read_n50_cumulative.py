#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_read_n50_cumulative.py — 生成 15_read_n50_cumulative.svg
（FIG-U04-18：读段 N50 累加算术图【算法】）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-18（P36，cols 一栏，viewBox 800×700）。
5 条读段从长到短：10/8/6/4/2 kb，总长 30 kb，半数 15 kb；
从长到短累加，10+8=18 ≥ 15（「达到或超过」即停）→ N50 = 8 kb（红框）。
数据来源：教材 §6.4.7 L198 算例。依据：教材 §6.4.7 L196–200（手算规则）。
图内汉字 27，红色 2 处。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 15_read_n50_cumulative.py
"""
from svghelp import *


def main():
    reads = [10, 8, 6, 4, 2]                 # kb
    total, half = sum(reads), sum(reads) / 2
    assert (total, half) == (30, 15)
    cum, crossing = 0, None
    for i, ln in enumerate(reads):
        cum += ln
        if cum >= half:
            crossing = i
            break
    assert crossing == 1 and reads[crossing] == 8
    print("check: 总长 30 kb，半数 15 kb，10+8=18 ≥ 15 → N50 = 8 kb")

    s = SVG(800, 700)
    X0, SC = 110, 20                         # px/kb
    colors = [BLUE, CYAN, ORANGE, PURPLE, GRAY]

    s.text(60, 64, "从长到短累加", 32, INK, "start", "bold")

    # 半数分割线（红虚线）与标注
    hx = X0 + half * SC
    s.line(hx, 96, hx, 500, RED, sw=5, dash="16 12")
    s.text(hx, 88, "半数十五", 30, RED, "middle", "bold")

    # 条形与累计刻度
    cum = 0
    for i, ln in enumerate(reads):
        y = 110 + i * 82
        w = ln * SC
        s.rect(X0, y, w, 58, colors[i], rx=8)
        lab = f"{ln}"
        if w >= 100:
            s.text(X0 + 14, y + 40, lab, 30, WHITE, "start", "bold")
        else:
            s.text(X0 + w + 12, y + 40, lab, 30, colors[i], "start", "bold")
        cum += ln
        cx = X0 + cum * SC
        s.line(cx, 508, cx, 522, INK, sw=3)
        s.text(cx, 558, str(cum), 30, GRAY, "middle")
    s.line(X0, 508, X0 + total * SC + 10, 508, INK, sw=4)

    # N50 红框（第二条，8 kb）
    y2 = 110 + 82
    s.rect(300, y2, 250, 58, WHITE, stroke=RED, sw=6, rx=10)
    s.text(425, y2 + 40, "读段五零为八", 30, RED, "middle", "bold")

    # 底部注记
    s.text(250, 634, "总长三十", 30, INK, "middle", "bold")
    s.text(560, 634, "累加跨过半数处", 30, INK, "middle", "bold")

    s.save("15_read_n50_cumulative.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

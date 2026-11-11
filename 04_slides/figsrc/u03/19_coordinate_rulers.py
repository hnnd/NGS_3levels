#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_coordinate_rulers.py — 生成 19_coordinate_rulers.svg（FIG-U03-19：0-based/1-based 双标尺）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-19（P48，cols 一栏，800×700）。
教材依据：chapters/ch05/manuscript.qmd §5.4.4、§5.5.1。
母串 A T G C A：1-based 闭 [2,4] 与 0-based 半开 [1,4) 都切出 TGC（3 bp）；
照抄坐标进 BED 会少算第 1000 号碱基。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 19_coordinate_rulers.py
"""
from svghelp import *  # noqa: F401,F403

BASES = [("A", GREEN), ("T", PURPLE), ("G", ORANGE), ("C", CYAN), ("A", GREEN)]
X0, CW, YMID = 60, 90, 340  # 母串网格起点 / 格宽 / 母串顶


def main():
    s = SVG(800, 700)
    s.text(400, 50, "半开与闭标尺对照", 36, BLUE, "middle", "bold")
    s.text(400, 92, "起点必须减一终点不变", 30, GRAY, "middle", "bold")

    # 母串网格（TGC = 第 2–4 格）
    for i, (b, col) in enumerate(BASES):
        x = X0 + i * CW
        s.rect(x, YMID, CW, 70, col, rx=6)
        s.text(x + CW / 2, YMID + 48, b, 36, WHITE, "middle", "bold")
    s.rect(X0 + CW, YMID, 3 * CW, 70, "none", RED, 5, rx=6)

    # 上标尺：1-based 闭，刻度对准碱基中心（GFF3 / VCF / IGV）
    s.text(X0, 150, "1-based 闭（GFF3/VCF）", 28, GREEN, "start", "bold")
    for i in range(5):
        cx = X0 + i * CW + CW / 2
        s.line(cx, YMID - 50, cx, YMID - 10, GREEN, 4)
        s.text(cx, YMID - 58, str(i + 1), 28, GREEN, "middle", "bold")
    s.line(X0 + 1.5 * CW, YMID - 90, X0 + 3.5 * CW, YMID - 90, GREEN, 5)
    s.line(X0 + 1.5 * CW, YMID - 90, X0 + 1.5 * CW, YMID - 70, GREEN, 5)
    s.line(X0 + 3.5 * CW, YMID - 90, X0 + 3.5 * CW, YMID - 70, GREEN, 5)
    s.text(X0 + 2.5 * CW, YMID - 102, "TGC = [2, 4]，长 3 bp", 28, GREEN,
           "middle", "bold")

    # 下标尺：0-based 半开，刻度对准碱基缝隙（BED / BAM）
    s.text(X0, 438, "0-based 半开（BED）", 28, PURPLE, "start", "bold")
    for i in range(6):
        bx = X0 + i * CW
        s.line(bx, YMID + 104, bx, YMID + 140, PURPLE, 4)
        s.text(bx, YMID + 172, str(i), 28, PURPLE, "middle", "bold")
    s.line(X0 + CW, YMID + 208, X0 + 4 * CW, YMID + 208, PURPLE, 5)
    s.line(X0 + CW, YMID + 208, X0 + CW, YMID + 188, PURPLE, 5)
    s.line(X0 + 4 * CW, YMID + 208, X0 + 4 * CW, YMID + 188, PURPLE, 5)
    s.text(X0 + 2.5 * CW, YMID + 250, "TGC = [1, 4)，长 3 bp", 28, PURPLE,
           "middle", "bold")

    # 右侧陷阱对照：照抄坐标进 BED
    s.rect(540, 250, 240, 200, RED_TINT, RED, 5, rx=14)
    s.text(660, 296, "照抄进 BED", 30, RED, "middle", "bold")
    s.text(660, 344, "chr1 1000 1200", 28, INK, "middle", "bold")
    s.text(660, 392, "→ 第 1001–1200 号", 24, RED, "middle", "bold")

    s.save("19_coordinate_rulers.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

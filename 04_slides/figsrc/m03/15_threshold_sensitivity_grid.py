#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_threshold_sensitivity_grid.py — 生成 15_threshold_sensitivity_grid.svg
（FIG-M03-18：8 组网格扫描保留 SNP 数与 Ts/Tv 权衡曲线）【data-plot】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-18（P38，cols 一栏，800×700）。
数据：textbook/demos/ch10_filter_thresholds.py Part 1（固定种子 20261104）
现跑核对：FS=30 → [3994, 4061, 4171, 4876]，Ts/Tv [1.896, 1.870, 1.816,
1.483]；FS=60 → [4441, 4516, 4634, 5339]，Ts/Tv [1.632, 1.610, 1.574,
1.339]。图内中文按方案（阈值网格 宽松放行 转换颠换比 下跌 伪影混入）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文，工具名/字段名/
命令/参数保留英文，字数不再按 ≤30 字核验。依据：教材 §10.4.7、§10.4.9。
"""
from svghelp import *  # noqa: F401,F403

QD = ["5.0", "3.0", "2.0", "1.0"]
N30, N60 = [3994, 4061, 4171, 4876], [4441, 4516, 4634, 5339]
T30 = [1.896, 1.870, 1.816, 1.483]
T60 = [1.632, 1.610, 1.574, 1.339]


def main():
    assert N30 == [3994, 4061, 4171, 4876] and T30[0] == 1.896
    assert N60 == [4441, 4516, 4634, 5339] and T60[-1] == 1.339
    assert T30 == sorted(T30, reverse=True) and N30 == sorted(N30)
    print("check vs demos Part 1: FS30", N30, T30)
    print("check vs demos Part 1: FS60", N60, T60)

    s = SVG(800, 700)
    s.text(400, 46, "阈值网格", 36, INK, "middle", "bold")

    x0, x1, y0, y1 = 100, 640, 540, 110

    def X(i):
        return x0 + i * (x1 - x0) / 3

    def YN(v):
        return y0 - (v - 3500) / 2000 * (y0 - y1)

    def YT(v):
        return y0 - (v - 0.4) / 1.6 * (y0 - y1)

    s.rect(40, 70, 720, 520, WHITE, PANEL, 3, rx=14)
    s.line(x0, y0, 700, y0, BLUE, 4)
    s.line(x0, y0, x0, y1 - 20, BLUE, 4)
    s.line(700, y0, 700, y1 - 20, GRAY, 3)
    for i, q in enumerate(QD):
        s.text(X(i), y0 + 40, f"QD {q}", 30, GRAY, "middle")
    s.text(400, 616, "QD 放松 →", 30, GRAY, "middle")
    s.text(58, 330, "保留数", 30, CYAN_DEEP, "middle", rotate=-90)
    s.text(742, 330, "Ts/Tv", 30, PURPLE, "middle", rotate=90)

    s.line(x0, YT(0.5), 700, YT(0.5), RED, 4, dash="16 12")
    s.text(400, YT(0.5) + 34, "随机期望 0.5", 30, RED, "middle")

    for series, col in [(N30, CYAN), (N60, BLUE)]:
        pts = [(X(i), YN(v)) for i, v in enumerate(series)]
        s.polyline(pts, col, 7)
        for i, v in enumerate(series):
            s.circle(X(i), YN(v), 9, col)
    for series, col in [(T30, PURPLE), (T60, ORANGE)]:
        pts = [(X(i), YT(v)) for i, v in enumerate(series)]
        s.polyline(pts, col, 6, dash="14 10")
        for i, v in enumerate(series):
            s.circle(X(i), YT(v), 8, col)

    s.text(X(0) - 12, YN(N30[0]) - 16, "3994", 30, CYAN, "end")
    s.text(X(3) + 12, YN(N30[3]) - 16, "4876", 30, CYAN, "start")
    s.text(X(0) - 12, YN(N60[0]) + 42, "4441", 30, BLUE, "end")
    s.text(X(3) + 12, YN(N60[3]) + 42, "5339", 30, BLUE, "start")
    s.text(X(0) - 14, YT(T30[0]) - 18, "1.896", 30, PURPLE, "end")
    s.text(X(3) + 14, YT(T30[3]) + 32, "1.483", 30, PURPLE, "start")
    s.text(X(3) + 14, YT(T60[3]) + 64, "1.339", 30, ORANGE, "start")

    # 中文标注
    s.text(200, 150, "宽松放行", 32, INK, "middle", "bold")
    s.text(560, 140, "转换颠换比", 32, PURPLE, "middle", "bold")
    s.text(560, 178, "下跌", 32, PURPLE, "middle", "bold")
    s.text(320, YT(0.5) - 16, "伪影混入", 32, RED, "middle", "bold")

    # 图例（两行）
    s.line(120, 650, 160, 650, CYAN, 7)
    s.text(172, 660, "FS30 保留数", 30, GRAY, "start")
    s.line(380, 650, 420, 650, BLUE, 7)
    s.text(432, 660, "FS60 保留数", 30, GRAY, "start")
    s.line(120, 684, 160, 684, PURPLE, 6, dash="14 10")
    s.text(172, 694, "FS30 Ts/Tv", 30, GRAY, "start")
    s.line(380, 684, 420, 684, ORANGE, 6, dash="14 10")
    s.text(432, 694, "FS60 Ts/Tv", 30, GRAY, "start")
    s.save("15_threshold_sensitivity_grid.svg")


if __name__ == "__main__":
    main()

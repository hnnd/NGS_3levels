#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""27_filter_overlap_orthogonality.py — 生成 27_filter_overlap_orthogonality.svg
（FIG-M03-28：四硬过滤器独立拦截数与重叠构成）【data-plot】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-28（P53，cols 一栏，800×700）。
数据：textbook/demos/ch10_filter_thresholds.py Part 2（默认阈值 QD2/FS60/
MQ40/SOR3）现跑核对：保留 4634/8000，拦截 3366；首触拦截 QD2=927、FS60=537、
MQ40=902、SOR3=1000；同时触 QD2+FS60 = 0。图内中文按方案（独立拦截 深度去偏
链偏检出 比对质量 各司其职无重叠）。D135（2026-11-10，总编复检）：图内英文
说明短语已译中文，工具名/字段名/命令/参数保留英文，字数不再按 ≤30 字核验。
依据：教材 §10.4.7。
"""
from svghelp import *  # noqa: F401,F403

TOTAL, KEPT = 8000, 4634
FILTERS = [("QD2", 927, CYAN, "深度去偏"), ("FS60", 537, ORANGE, "链偏检出"),
           ("MQ40", 902, PURPLE, "比对质量"), ("SOR3", 1000, GREEN, "链偏")]


def main():
    assert TOTAL - KEPT == 3366
    assert [f[1] for f in FILTERS] == [927, 537, 902, 1000]
    print("check vs demos Part 2: kept", KEPT, "intercept", TOTAL - KEPT,
          [f[1] for f in FILTERS])

    s = SVG(800, 700)
    s.text(400, 44, "独立拦截构成", 36, INK, "middle", "bold")

    # 上：总构成条
    s.rect(40, 68, 720, 130, WHITE, PANEL, 3, rx=14)
    s.text(160, 118, "总数 8000", 32, INK, "middle", "bold")
    bx, bw, by = 300, 420, 92
    wk = bw * KEPT / TOTAL
    s.rect(bx, by, wk, 56, BLUE, None, rx=8)
    s.rect(bx + wk + 6, by, bw - wk - 6, 56, RED, None, rx=8)
    s.text(bx + wk / 2, by + 38, f"保留 {KEPT}", 30, WHITE, "middle", "bold")
    s.text(bx + wk + (bw - wk) / 2, by + 38, f"拦截 {TOTAL-KEPT}", 30, WHITE,
           "middle", "bold")

    # 下：四条拦截柱
    s.rect(40, 226, 720, 380, WHITE, PANEL, 3, rx=14)
    base = 520
    s.line(80, base, 740, base, BLUE, 4)
    for i, (name, cnt, col, role) in enumerate(FILTERS):
        x = 110 + i * 160
        h = cnt / 1000 * 200
        s.rect(x, base - h, 100, h, col, None, rx=6)
        s.text(x + 50, base - h - 16, str(cnt), 32, col, "middle", "bold")
        s.text(x + 50, base - h - 52, f"{cnt/TOTAL:.1%}", 30, GRAY, "middle")
        s.text(x + 50, base + 40, name, 32, INK, "middle", "bold")
        s.text(x + 50, base + 78, role, 30, col, "middle")

    # 徽章与注记
    s.rect(120, 622, 340, 56, GREEN_TINT, GREEN, 5, rx=14)
    s.text(290, 661, "各司其职无重叠", 32, GREEN, "middle", "bold")
    s.text(600, 662, "QD2∩FS60 = 0", 30, GRAY, "middle", "bold")
    s.text(400, 694, "合成算例： ch10_filter_thresholds.py Part 2", 30,
           GRAY, "middle")
    s.save("27_filter_overlap_orthogonality.svg")


if __name__ == "__main__":
    main()

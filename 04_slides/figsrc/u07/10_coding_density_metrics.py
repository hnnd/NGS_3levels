#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_coding_density_metrics.py — 生成 10_coding_density_metrics.svg（FIG-U07-10：编码比例两种口径差异）【data-plot】

方案：reviews/course/U07_FIGP_001.md §4.2 FIG-U07-10（P28，cols 一栏，viewBox 800×700）。
数据（算术复核，教材 §9.4.5 L220–226 设例）：CDS1 101–300、CDS2 251–450（1-based 闭区间），
各 200 bp，重叠 50 bp；求和 400 bp → 40.0%，并集 350 bp → 35.0%，差 5.0 个百分点。
设例标注（图内灰字）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 10_coding_density_metrics.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    c1s, c1e = 101, 300
    c2s, c2e = 251, 450
    g = 1000
    l1, l2 = c1e - c1s + 1, c2e - c2s + 1
    ov = c1e - c2s + 1
    union = c2e - c1s + 1
    sum_bp = l1 + l2
    assert (l1, l2, ov) == (200, 200, 50)
    assert (sum_bp, union) == (400, 350)
    assert sum_bp * 100 // g == 40 and union * 100 // g == 35
    print(f"check: 求和 {l1}+{l2}={sum_bp} bp → {sum_bp / g:.1%}；"
          f"并集 {c2e}−{c1s}+1={union} bp → {union / g:.1%}")

    s = SVG(800, 700)
    s.text(770, 44, "设例", 30, GRAY, "end")

    PX = 0.6  # 600 px = 1,000 bp
    X0 = 80

    def x(p):
        return X0 + (p - 1) * PX

    # 基因组条（深蓝）+ 起止坐标
    s.rect(x(1), 84, g * PX, 36, BLUE, rx=6)
    s.text(x(1), 70, "1", 30, GRAY, "middle")
    s.text(x(1000), 70, "1,000", 30, GRAY, "middle")

    # 两条重叠 CDS + 斜纹重叠区
    s.rect(x(c1s), 170, l1 * PX, 42, CYAN, rx=6)
    s.rect(x(c2s), 240, l2 * PX, 42, ORANGE, rx=6)
    ov_x, ov_w = x(c2s), ov * PX
    clip_id = s.clip("ov", [(ov_x, 160), (ov_x + ov_w, 160),
                            (ov_x + ov_w, 292), (ov_x, 292)])
    s.raw(f'<g clip-path="{clip_id}">')
    for k in range(-6, 14):
        s.line(ov_x + k * 14, 292, ov_x + k * 14 + 60, 160, PURPLE, 4)
    s.raw("</g>")
    s.rect(ov_x, 170, ov_w, 42, "none", PURPLE, 4, rx=6)
    s.rect(ov_x, 240, ov_w, 42, "none", PURPLE, 4, rx=6)
    s.text(ov_x + ov_w / 2, 156, "50 bp", 30, GRAY, "middle")

    for p, lab in ((c1s, "101"), (c2s, "251"), (c2e, "450")):
        s.line(x(p), 292, x(p), 306, GRAY, 4)
        s.text(x(p), 346, lab, 30, GRAY, "middle")
    s.line(x(c1e), 292, x(c1e), 318, GRAY, 4)
    s.text(x(c1e), 392, "300", 30, GRAY, "middle")

    # 求和口径卡（深蓝）
    s.rect(30, 410, 360, 150, BLUE, rx=14)
    s.text(210, 458, "求和口径：重叠算两次", 30, WHITE, "middle", "bold")
    s.text(210, 504, "200 + 200 = 400 bp", 30, WHITE, "middle")
    s.text(210, 544, "→ 40.0%", 32, WHITE, "middle", "bold")

    # 并集口径卡（绿）
    s.rect(410, 410, 360, 150, GREEN, rx=14)
    s.text(590, 458, "并集口径：重叠算一次", 30, WHITE, "middle", "bold")
    s.text(590, 504, "450 − 101 + 1 = 350 bp", 30, WHITE, "middle")
    s.text(590, 544, "→ 35.0%", 32, WHITE, "middle", "bold")

    # 底部红色差异块（唯一红色）
    s.rect(190, 596, 420, 60, RED, rx=12)
    s.text(400, 638, "同份注释差五个百分点", 32, WHITE, "middle", "bold")

    s.save("10_coding_density_metrics.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

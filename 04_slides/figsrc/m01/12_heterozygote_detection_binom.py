#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_heterozygote_detection_binom.py — 生成 12_heterozygote_detection_binom.svg
（FIG-M01-14：杂合位点二项抽样与漏检阈值）【data-plot】

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-14（P34，cols 一栏，800×700）。
数据（算术二项模型，教材 §13.4.4 L211–221；demos/ch13_variance_partition.py
--selftest Part 0 同式核对）：Bin(10, 0.5) 的 P(X≤1) = 11/1024 = 1.07%；
P(X≤1|d) = (1+d)/2^d，d=14 时 15/2^14 = 9.16×10⁻⁴ < 0.1%；d=25 时 7.75×10⁻⁷。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 12_heterozygote_detection_binom.py
"""
import math

from svghelp import *  # noqa: F401,F403

N = 10
BASE = 520  # 两面板统一直角坐标基线


def main():
    # 与 demos Part 0 逐格核对
    p_le1 = (math.comb(N, 0) + math.comb(N, 1)) / 2 ** N
    assert abs(p_le1 - 11 / 1024) < 1e-12 and abs(p_le1 - 0.0107421875) < 1e-9
    p14 = 15 / 2 ** 14
    p25 = 26 / 2 ** 25
    assert p14 < 1e-3 and abs(p14 - 9.16e-4) < 1e-6
    assert abs(p25 - 7.75e-7) < 1e-9
    print(f"check: P(X≤1|10×)={100*p_le1:.2f}%（11/1024）；d=14: {p14:.2e}；"
          f"d=25: {p25:.2e}（demos Part 0 同式）")

    s = SVG(800, 700)
    s.text(400, 48, "杂合等位抽样", 34, INK, "middle", "bold")

    # 左：Bin(10, 0.5) 概率柱（k≤1 红色斜纹；k 轴标签奇偶错行防重叠）
    s.rect(50, 76, 330, 540, WHITE, PANEL, 3, rx=14)
    s.text(215, 112, "10× 下 P(X≤1)=1.07%", 30, RED, "middle", "bold")
    s.line(70, BASE, 380, BASE, BLUE, 4)
    s.line(70, 130, 70, BASE, BLUE, 4)
    for k in range(N + 1):
        p = math.comb(N, k) / 2 ** N
        h = max(p / 0.2461 * 360, 3)
        x = 72 + k * 28
        if k <= 1:
            clip = s.clip(f"hatch{k}", [(x, BASE - h), (x + 24, BASE - h),
                                        (x + 24, BASE), (x, BASE)])
            s.rect(x, BASE - h, 24, h, RED)
            s.raw(f'<g clip-path="{clip}">')
            yy = BASE - h - 24
            while yy < BASE + 24:
                s.line(x - 20, yy, x + 44, yy - 40, WHITE, 4)
                yy += 16
            s.raw("</g>")
        else:
            s.rect(x, BASE - h, 24, h, BLUE)
        ly = BASE + 38 if k % 2 == 0 else BASE + 76
        s.text(x + 12, ly, str(k), 30, GRAY, "middle")

    # 右：P(X≤1|d) 对数衰减曲线 + d=14 达标线 + 25–30× 惯例带
    s.rect(420, 76, 330, 540, WHITE, PANEL, 3, rx=14)

    def X(d):
        return 440 + (d - 8) / 22 * 240

    def Y(logp):
        return BASE - (logp + 8) / 6.8 * 400

    s.line(440, BASE, 690, BASE, BLUE, 4)
    s.line(440, 150, 440, BASE, BLUE, 4)
    pts = []
    for d in range(8, 31):
        lp = math.log10((1 + d) / 2 ** d)
        pts.append((X(d), Y(lp)))
    s.polyline(pts, BLUE, 5)
    for d in (8, 14, 20, 30):
        s.text(X(d) + (20 if d == 8 else 0), BASE + 38, str(d), 30, GRAY,
               "middle")

    # d=14 绿色达标线（P(X≤1) < 0.1%）；标签右对齐于线左侧空区，避开曲线
    s.line(X(14), 150, X(14), BASE, GREEN, 5)
    s.text(X(14) - 10, 440, "d=14 达到", 30, GREEN, "end", "bold")
    s.text(X(14) - 10, 480, "<0.1%", 30, GREEN, "end", "bold")

    # 25–30× 工程惯例带（深蓝底纹；标签置于带上方空区）
    s.rect(X(25), 150, X(30) - X(25), BASE - 150, BLUE_TINT)
    s.text(652, 110, "25–30×", 30, BLUE, "middle", "bold")
    s.text(652, 146, "为工程惯例带", 30, INK, "middle", "bold")

    s.save("12_heterozygote_detection_binom.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

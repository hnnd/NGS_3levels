#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_kmer_spectrum_reading.py — 生成 18_kmer_spectrum_reading.svg
（FIG-U02-18：k-mer 频谱怎么读；插入页 figure 版式 1600×900）

方案：reviews/course/U02_FIGP_001.md §4 FIG-U02-18（插入页，viewBox 1600×900）。
数据：无量字数字（定性示意）。防复活条款（方案问题 Q3）：不画 2× 重复峰、
不标峰位 45/90（CNT-U02-06 已撤）、不标 XLIM_MAX=150（脚本配置留 P47 文字）。
依据：教材 §3.4.7 L235（错误峰远多于主峰、线性轴压平、对数纵轴）。
红 2 处（满额）：错误峰 + 线性轴贴地对照；主峰绿（要看的信号）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 18_kmer_spectrum_reading.py
"""
import math

from svghelp import *  # noqa: F401,F403

# (depth, log10(频数))——定性形态示意，无数值含义
SPEC = [(2, 5.5), (4, 6.2), (6, 6.6), (8, 6.4), (12, 5.2), (18, 4.0),
        (25, 3.4), (35, 4.2), (45, 4.9), (55, 5.1), (65, 4.6), (80, 3.8),
        (100, 3.0), (125, 2.4), (150, 1.9)]
X0, X1 = 160, 1520
Y_TOP, Y_BASE = 80, 700


def xmap(d):
    return X0 + d * (X1 - X0) / 150


def ymap(logc):
    return Y_BASE - logc * (Y_BASE - Y_TOP) / 7


def main():
    s = SVG(1600, 900)

    s.text(40, 380, "纵轴取对数", 32, INK, "start", "bold")
    s.text(360, 56, "log10(k-mer count)", 32, INK, "start", "bold")
    s.line(X0, Y_TOP - 24, X0, Y_BASE, INK, 4)
    s.line(X0, Y_BASE, X1, Y_BASE, INK, 4)
    for logc in range(1, 7):
        y = ymap(logc)
        s.line(X0 - 12, y, X0, y, INK, 3)
        s.text(X0 - 22, y + 10, f"10^{logc}", 30, GRAY, "end")
    for d in (0, 50, 100, 150):
        x = xmap(d)
        s.line(x, Y_BASE, x, Y_BASE + 14, INK, 3)
        s.text(x, Y_BASE + 52, str(d), 30, GRAY, "middle")
    s.text((X0 + X1) / 2, Y_BASE + 96, "k-mer depth", 32, INK, "middle", "bold")

    red_pts = [(xmap(d), ymap(c)) for d, c in SPEC[:6]]
    blue_pts = [(xmap(d), ymap(c)) for d, c in SPEC[5:]]
    s.curve(blue_pts, BLUE, 7)
    s.curve(red_pts, RED, 7)

    mx = xmap(55)
    s.line(mx, ymap(5.1), mx, Y_BASE, GREEN, 5, dash="16 12")
    s.text(mx, ymap(5.1) - 26, "主峰", 36, GREEN, "middle", "bold")
    s.text(xmap(16), ymap(6.2) + 6, "错误峰", 36, RED, "start", "bold")

    # 幽灵对照面板：线性纵轴，主峰被压成贴地一条线
    gx, gy, gw, gh = 200, 540, 380, 200
    s.rect(gx, gy, gw, gh, WHITE, GRAY, 4, rx=10)
    lin = [(d, 10 ** c) for d, c in SPEC]
    top = 10 ** 6.8
    pts = [(gx + 20 + d / 150 * (gw - 40), gy + gh - 20 - c / top * (gh - 60))
           for d, c in lin]
    s.polyline(pts, RED, 6)
    s.text(gx + gw / 2, gy - 16, "线性轴主峰贴地", 32, RED, "middle", "bold")
    s.text(gx + gw - 16, gy + gh - 28, "linear y", 30, GRAY, "end")

    s.save("18_kmer_spectrum_reading.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

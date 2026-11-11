#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_spectrum_area_integration.py — 05_spectrum_area_integration.svg
（FIG-M02-07，P18，cols）：频谱面积法积分求基因组大小【data-plot】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-07。数据（与 demos 现跑一致）：
demos/ch08_kmer_spectrum.py --selftest 场景一（G=40,000、D=30×、L=100、k=21、
e=0.01、种子 20261102）：主峰 19×；按 i_min=4 剔除错误尾后
G_est = Σ(i·N_i, i≥4)/19 = 40,976 bp（真值 40,000，偏差 2.4%）。
无网络；种子固定。用法：PYTHONDONTWRITEBYTECODE=1 python3 05_spectrum_area_integration.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch08_kmer_spectrum as demo  # noqa: E402

from svghelp import (BLUE, GRAY, GREEN, INK, RED, SVG, WHITE)

CYAN_TINT = "#D6EEF5"


def check_data():
    rng = np.random.default_rng(20261102)
    genome = demo.random_genome(rng, 40000)
    reads = demo.simulate_reads(genome, 30, 100, 0.01, rng)
    hashes = demo.canonical_kmer_hashes(reads, 21)
    _, counts = np.unique(hashes, return_counts=True)
    hist = np.bincount(counts, minlength=int(counts.max()) + 1)
    area = sum(i * hist[i] for i in range(4, len(hist)))
    g_est = area / 19
    assert round(g_est) == 40976, g_est
    print(f"check: Σ(i·N_i, i≥4)/19 = {g_est:,.0f} bp（demos 场景一复算）")
    return hist


def main():
    hist = check_data()

    imax = 50
    nbin = len(hist)
    contrib = [i * int(hist[i]) if i < nbin else 0 for i in range(imax + 1)]
    vmax = max(contrib[1:]) * 1.06

    s = SVG(800, 700)

    # 坐标区：i∈[1,50] → px 100..760；贡献量 → py 520..110
    x0, x1, y0, y1 = 100.0, 760.0, 520.0, 110.0

    def px(i):
        return x0 + (i - 1) / (imax - 1) * (x1 - x0)

    def py(v):
        return y0 - v / vmax * (y0 - y1)

    pts = [(px(i), py(contrib[i])) for i in range(1, imax + 1)]

    # i≤3 红色斜纹错误尾 + i=4 红色分割线
    hatch = s.hatch("errtail", RED, gap=12, sw=4)
    s.rect(x0, y1, px(4) - x0, y0 - y1, hatch)
    s.line(px(4), y0, px(4), y1 - 8, RED, 6)
    s.text(px(4) + 16, 138, "i<4 错误尾剔除", 30, RED, "start", "bold")

    # i≥4 有效面积（青蓝淡底）+ 深蓝曲线
    area = [(px(4), y0)] + pts[3:] + [(px(imax), y0)]
    clip = s.clip("keep", area)
    s.raw(f'<g clip-path="{clip}"><rect x="{x0}" y="{y1}" '
          f'width="{x1 - x0}" height="{y0 - y1}" fill="{CYAN_TINT}"/>'
          f'<rect x="{x0}" y="{y1}" width="{px(4) - x0}" height="{y0 - y1}" '
          f'fill="#FAFAF7"/></g>')
    s.curve(pts, BLUE, 6)

    # 坐标轴与刻度
    s.line(x0, y0, x1 + 12, y0, INK, 5)
    s.line(x0, y0, x0, y1 - 14, INK, 5)
    for i in (1, 10, 20, 30, 40, 50):
        s.line(px(i), y0, px(i), y0 + 9, INK, 4)
        s.text(px(i), y0 + 40, str(i), 30, INK, "middle")
    s.text(x1 + 18, y0 - 6, "i", 32, INK, "start", "bold")

    # 面积法标注 + 主峰位置
    s.line(px(19), y0, px(19), y1 + 40, BLUE, 4, dash="14 10")
    s.text(px(19) + 8, y1 + 84, "19×", 32, BLUE, "start", "bold")
    s.text(430, 300, "有效面积除以主峰 19×", 32, BLUE, "start", "bold")

    # 结果（绿）与底部红字警示
    s.text(400, 610, "估计 40,976 bp 偏差 2.4%", 34, GREEN, "middle", "bold")
    s.text(400, 664, "不可把错误尾计入面积", 32, RED, "middle", "bold")

    s.save("05_spectrum_area_integration.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

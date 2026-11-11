#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_strain_selection_bias_gamma.py — 15_strain_selection_bias_gamma.svg
（FIG-M02-20，P39，cols）：选株偏倚改变开放性指数 gamma【data-plot】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-20。数据（与 demos 现跑一致）：
demos/ch11_pan_rarefaction.py --selftest（种子 20261104，draws=200）：
近缘 12 株 pan(12)=5510、γ=0.253；混簇 12 株 pan(12)=6610、γ=0.317；
封闭组仅用 N≤6 拟合 γ=0.115（小样本高估开放性）。本脚本按 demos selftest
完全相同的 rng 调用序列复算并断言。无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 15_strain_selection_bias_gamma.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch11_pan_rarefaction as demo  # noqa: E402

from svghelp import (BLUE, GRAY, INK, ORANGE, PURPLE, RED, SVG)


def check_data():
    rng = np.random.default_rng(20261104)
    open_mat, _ = demo.simulate_panel(rng, 24, demo.OPEN, two_clades=True,
                                      seed_tag="开放组")
    open_pan, _ = demo.rarefaction(open_mat, 200, rng)
    closed_mat, _ = demo.simulate_panel(rng, 24, demo.CLOSED,
                                        two_clades=False, seed_tag="封闭组")
    closed_pan, _ = demo.rarefaction(closed_mat, 200, rng)
    clade_only = open_mat[:, :12]
    clade_pan, _ = demo.rarefaction(clade_only, 200, rng)
    kn, gn, _ = demo.heaps_fit(clade_pan, 12)
    mixed = np.hstack([open_mat[:, :6], open_mat[:, 12:18]])
    mixed_pan, _ = demo.rarefaction(mixed, 200, rng)
    km, gm, _ = demo.heaps_fit(mixed_pan, 12)
    ks, gs, _ = demo.heaps_fit(closed_pan, 6)

    assert round(clade_pan[12]) == 5510 and round(mixed_pan[12]) == 6610
    assert abs(gn - 0.253) < 5e-4 and abs(gm - 0.317) < 5e-4
    assert abs(gs - 0.115) < 5e-4
    print(f"check: 近缘 γ={gn:.3f} pan12={clade_pan[12]:.0f}；混簇 γ={gm:.3f} "
          f"pan12={mixed_pan[12]:.0f}；N≤6 拟合 γ={gs:.3f}（demos 复算）")
    return (clade_pan, gn, kn), (mixed_pan, gm, km), (gs, ks)


def main():
    (clade_pan, gn, kn), (mixed_pan, gm, km), (gs, ks) = check_data()

    s = SVG(800, 700)

    # 坐标区：N∈[1,12] → px 90..740；家族数 → py 560..140（上限 7000）
    x0, x1, y0, y1 = 90.0, 740.0, 560.0, 140.0
    vmax = 7000.0

    def px(n):
        return x0 + (n - 1) / 11.0 * (x1 - x0)

    def py(v):
        return y0 - v / vmax * (y0 - y1)

    s.line(x0, y0, x1 + 10, y0, INK, 5)
    s.line(x0, y0, x0, y1 - 12, INK, 5)
    for n in (1, 3, 6, 9, 12):
        s.line(px(n), y0, px(n), y0 + 9, INK, 4)
        s.text(px(n), y0 + 42, str(n), 30, INK, "middle")

    ns = np.arange(1, 13)
    s.curve([(px(n), py(clade_pan[n])) for n in ns], BLUE, 7)
    s.curve([(px(n), py(mixed_pan[n])) for n in ns], ORANGE, 7)
    # 小样本 N≤6 拟合错觉（紫虚线，按该拟合律外推整段）
    small = [ks * n ** gs for n in ns]
    s.curve([(px(n), py(v)) for n, v in zip(ns, small)], PURPLE, 6,
            dash="16 12")

    s.text(px(12) - 6, py(clade_pan[12]) + 56, "近缘 12 株 γ=0.253", 30,
           BLUE, "end", "bold")
    s.text(px(12) - 6, py(mixed_pan[12]) - 20, "混簇 12 株 γ=0.317", 30,
           ORANGE, "end", "bold")
    s.text(px(7), py(small[6]) + 44, "小样本 N≤6 高估开放性", 30, PURPLE,
           "middle", "bold")

    s.text(400, 656, "开放性是抽样属性", 34, RED, "middle", "bold")

    s.save("15_strain_selection_bias_gamma.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_rarefaction_heaps_open_closed.py — 14_rarefaction_heaps_open_closed.svg
（FIG-M02-19，P38，cols）：泛基因组稀释曲线与 Heaps 定律开放/封闭拟合【data-plot】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-19（FT11-01 题材）。
数据（与 demos 现跑一致）：demos/ch11_pan_rarefaction.py --selftest
（种子 20261104，draws=200）：开放组 pan(24)=8456、γ=0.331、末 5 增量中位 142、
核心占比 57.0%→30.7%；封闭组 pan(24)=4053、γ=0.089、增量 10。
本脚本按 demos selftest 完全相同的 rng 调用序列复算并断言。
无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 14_rarefaction_heaps_open_closed.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch11_pan_rarefaction as demo  # noqa: E402

from svghelp import (BLUE, CYAN, GRAY, GREEN, INK, RED, SVG, WHITE)


def check_data():
    rng = np.random.default_rng(20261104)
    open_mat, _ = demo.simulate_panel(rng, 24, demo.OPEN, two_clades=True,
                                      seed_tag="开放组")
    open_pan, open_core = demo.rarefaction(open_mat, 200, rng)
    ko, go, _ = demo.heaps_fit(open_pan, 24)
    closed_mat, _ = demo.simulate_panel(rng, 24, demo.CLOSED,
                                        two_clades=False, seed_tag="封闭组")
    closed_pan, closed_core = demo.rarefaction(closed_mat, 200, rng)
    kc, gc, _ = demo.heaps_fit(closed_pan, 24)

    assert round(open_pan[24]) == 8456 and round(closed_pan[24]) == 4053
    assert round(closed_core[24]) == 2601
    assert abs(go - 0.331) < 5e-4 and abs(gc - 0.089) < 5e-4
    inc_o = np.median(np.diff(open_pan[20:25]))
    inc_c = np.median(np.diff(closed_pan[20:25]))
    assert round(inc_o) == 142 and round(inc_c) == 10
    assert abs(open_core[4] / open_pan[4] - 0.570) < 5e-3
    assert abs(open_core[24] / open_pan[24] - 0.307) < 5e-3
    print(f"check: 开放 pan24={open_pan[24]:.0f} γ={go:.3f} 增量{inc_o:.0f}；"
          f"封闭 pan24={closed_pan[24]:.0f} γ={gc:.3f} 增量{inc_c:.0f}（demos 复算）")
    return (open_pan, open_core, go, ko), (closed_pan, closed_core, gc, kc)


def panel(s, x0, w, title, tcolor, pan, core, gamma, kappa, pan24, inc):
    s.rect(x0, 100, w, 440, WHITE, "#E9E9E5", 3, rx=14)
    head, tail = title.split(" ", 1)
    s.text(x0 + w / 2, 140, head, 32, tcolor, "middle", "bold")
    s.text(x0 + w / 2, 180, tail, 30, tcolor, "middle", "bold")
    px0, px1, py0, py1 = x0 + 30, x0 + w - 30, 500.0, 210.0
    vmax = 9800.0

    def px(n):
        return px0 + (n - 1) / 23.0 * (px1 - px0)

    def py(v):
        return py0 - v / vmax * (py0 - py1)

    s.line(px0, py0, px1 + 8, py0, INK, 4)
    s.line(px0, py0, px0, py1 - 10, INK, 4)
    for n in (1, 6, 12, 18, 24):
        s.line(px(n), py0, px(n), py0 + 8, INK, 3)
        s.text(px(n), py0 + 36, str(n), 30, GRAY, "middle")
    # pan 曲线（实线）+ Heaps 拟合（同色虚线）
    ns = np.arange(1, 25)
    s.curve([(px(n), py(pan[n])) for n in ns], tcolor, 6)
    fit = [kappa * n ** gamma for n in ns]
    s.curve([(px(n), py(v)) for n, v in zip(ns, fit)], tcolor, 5,
            dash="14 10")
    # core 曲线（绿，近平 → 与 pan 的张口即占比下降）
    s.curve([(px(n), py(core[n])) for n in ns], GREEN, 5)
    s.text(px1, py(pan[24]) - 18, f"{pan24:.0f}", 30, tcolor, "end", "bold")
    s.text(px1, py(core[24]) + 40, f"core {core[24]:.0f}", 30, GREEN, "end",
           "bold")
    s.text(px0 + 12, py1 + 32, f"+{inc:.0f}/株", 30, GRAY, "start", "bold")


def main():
    (open_pan, open_core, go, ko), (closed_pan, closed_core, gc, kc) = \
        check_data()

    s = SVG(800, 700)
    panel(s, 30, 355, "开放组：γ=0.331 持续上升", BLUE, open_pan, open_core,
          go, ko, open_pan[24], 142)
    panel(s, 415, 355, "封闭组：γ=0.089 趋于平台", CYAN, closed_pan,
          closed_core, gc, kc, closed_pan[24], 10)

    s.text(400, 656, "末段仍在降不可下结论", 34, RED, "middle", "bold")

    s.save("14_rarefaction_heaps_open_closed.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

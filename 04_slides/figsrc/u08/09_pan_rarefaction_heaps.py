#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_pan_rarefaction_heaps.py — 生成 09_pan_rarefaction_heaps.svg（FIG-U08-09：
泛基因组累积曲线与 Heaps 拟合，FT11-01 落地）

方案：reviews/course/U08_FIGP_001.md §4 FIG-U08-09（P26，cols 一栏，800×700）【data-plot】。
数据（与 demos 现跑一致）：demos/ch11_pan_rarefaction.py 固定种子 20261104、
draws=200 的中位数曲线——开放组 pan(24)=8456、core(24)=2600、γ=0.331；
近簇 12 株 pan(12)=5510、γ=0.253；混簇 12 株 pan(12)=6610、γ=0.317
（教材 §11.3 符号、§11.4.5、§11.5.3）。
无网络；种子固定。用法：PYTHONDONTWRITEBYTECODE=1 python3 09_pan_rarefaction_heaps.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "textbook"
                       / "demos"))
import ch11_pan_rarefaction as demo  # noqa: E402

from svghelp import *  # noqa: F401,F403,E402


def main():
    # —— 复现 demos selftest 的完整 rng 消费顺序，保证曲线逐点一致 ——
    rng = np.random.default_rng(20261104)
    open_mat, _ = demo.simulate_panel(rng, 24, demo.OPEN, two_clades=True,
                                      seed_tag="开放组")
    open_pan, open_core = demo.rarefaction(open_mat, 200, rng)
    closed_mat, _ = demo.simulate_panel(rng, 24, demo.CLOSED, two_clades=False,
                                        seed_tag="封闭组")
    closed_pan, _ = demo.rarefaction(closed_mat, 200, rng)
    clade_only = open_mat[:, :12]
    clade_pan, _ = demo.rarefaction(clade_only, 200, rng)
    mixed = np.hstack([open_mat[:, :6], open_mat[:, 12:18]])
    mixed_pan, _ = demo.rarefaction(mixed, 200, rng)

    _, g_open, _ = demo.heaps_fit(open_pan, 24)
    _, g_closed, _ = demo.heaps_fit(closed_pan, 24)
    _, g_clade, _ = demo.heaps_fit(clade_pan, 12)
    _, g_mixed, _ = demo.heaps_fit(mixed_pan, 12)
    assert round(open_pan[24]) == 8456 and round(open_core[24]) == 2600
    assert abs(g_open - 0.331) < 5e-3, f"γ_open={g_open:.3f}"
    assert abs(g_closed - 0.089) < 5e-3, f"γ_closed={g_closed:.3f}"
    assert round(clade_pan[12]) == 5510 and abs(g_clade - 0.253) < 5e-3
    assert round(mixed_pan[12]) == 6610 and abs(g_mixed - 0.317) < 5e-3
    assert np.all(np.diff(open_core[1:]) <= 0), "核心曲线应随 N 不增"
    print(f"check: pan(24)={open_pan[24]:.0f} core(24)={open_core[24]:.0f} "
          f"γ={g_open:.3f}；近簇 γ={g_clade:.3f} pan(12)={clade_pan[12]:.0f}；"
          f"混簇 γ={g_mixed:.3f} pan(12)={mixed_pan[12]:.0f}")

    s = SVG(800, 700)
    X0, X1, Y0, Y1 = 96, 430, 120, 560
    ymax = 9000.0

    def px(n):
        return X0 + (X1 - X0) * (n - 1) / 23

    def py(v):
        return Y1 - (Y1 - Y0) * v / ymax

    # 坐标轴
    s.line(X0, Y0, X0, Y1, INK, 3)
    s.line(X0, Y1, X1 + 12, Y1, INK, 3)
    for n in (4, 8, 12, 16, 20, 24):
        s.text(px(n), Y1 + 40, str(n), 30, GRAY, "middle")
    s.text(X0 + 4, Y0 - 22, "gene families", 30, GRAY, "start")
    for v in (2000, 4000, 6000, 8000):
        s.line(X0 - 8, py(v), X0, py(v), INK, 3)
        s.text(X0 - 18, py(v) + 11, f"{v}", 30, GRAY, "end")
    s.text(X1 + 26, Y1 + 40, "N", 30, GRAY, "start")

    # 双曲线：Pan（青蓝上升）与 Core（深蓝下降）
    pan_pts = [(px(n), py(open_pan[n])) for n in range(1, 25)]
    core_pts = [(px(n), py(open_core[n])) for n in range(1, 25)]
    s.curve(pan_pts, CYAN, 6)
    s.curve(core_pts, BLUE, 6)
    s.text(436, 132, "泛基因组累积：开放", 30, CYAN_DEEP, "end", "bold")
    s.text(px(24) + 4, py(open_core[24]) + 70, "核心基因递减", 30, BLUE,
           "end", "bold")

    # 右侧嵌框：Heaps 拟合随选株改变（两行一组，防溢出）
    s.rect(500, 100, 276, 300, WHITE, PANEL, 4, rx=14)
    s.text(638, 150, "Heaps P(N)=κ·N^γ", 30, INK, "middle", "bold")
    s.text(638, 194, "随选株改变", 32, RED, "middle", "bold")
    s.text(638, 250, "近缘 12 株", 32, GREEN, "middle", "bold")
    s.text(638, 290, f"γ = {g_clade:.3f}", 30, INK, "middle")
    s.text(638, 338, "混簇 12 株", 32, "#D0763B", "middle", "bold")
    s.text(638, 378, f"γ = {g_mixed:.3f}", 30, INK, "middle")

    s.text(400, 646, "合成数据 demos/ch11_pan_rarefaction.py", 30, GRAY,
           "middle")
    s.text(400, 684, "open panel n=24: gamma=0.331; median of 200 draws", 30,
           GRAY, "middle")

    s.save("09_pan_rarefaction_heaps.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

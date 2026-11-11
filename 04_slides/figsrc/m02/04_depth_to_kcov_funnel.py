#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_depth_to_kcov_funnel.py — 04_depth_to_kcov_funnel.svg
（FIG-M02-06，P17，cols）：测序深度 D 到 k-mer 深度 D_k 理论换算漏斗【data-plot】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-06。数据（与 demos 现跑一致）：
demos/ch08_kmer_spectrum.py --selftest 场景一（G=40,000、D=30×、L=100、k=21、
e=0.01、种子 20261102）：主峰 19×，理论 D_k=30×0.80×0.99^21≈19.4×，
错误尾（深度 1–3）占种类数 81.5%。无网络；种子固定。
用法：PYTHONDONTWRITEBYTECODE=1 python3 04_depth_to_kcov_funnel.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch08_kmer_spectrum as demo  # noqa: E402

from svghelp import (BLUE, CYAN, GRAY, GREEN, INK, RED, SVG, WHITE)


def check_data():
    rng = np.random.default_rng(20261102)
    genome = demo.random_genome(rng, 40000)
    reads = demo.simulate_reads(genome, 30, 100, 0.01, rng)
    hashes = demo.canonical_kmer_hashes(reads, 21)
    _, counts = np.unique(hashes, return_counts=True)
    hist = np.bincount(counts, minlength=int(counts.max()) + 1)
    sm = demo.smooth(hist.astype(float))
    body = sm[4:]
    sig = [4 + p for p in demo.local_maxima(body, min_height=0.08 * body.max())]
    peak = max(sig)
    err_tail = hist[1:4].sum() / hist[1:].sum() * 100
    expect = 30 * (100 - 21 + 1) / 100 * (1 - 0.01) ** 21
    assert peak == 19, peak
    assert abs(expect - 19.4) < 0.05, expect
    assert abs(err_tail - 81.5) < 0.05, err_tail
    print(f"check: 主峰 {peak}×，理论 D_k={expect:.1f}×，错误尾 {err_tail:.1f}%"
          "（demos 场景一复算）")
    return peak, expect, err_tail


def main():
    peak, expect, err_tail = check_data()

    s = SVG(800, 700)

    # 顶层：测序深度 D（深蓝）
    s.polygon([(120, 84), (680, 84), (640, 196), (160, 196)], BLUE)
    s.text(400, 128, "测序深度 D=30×", 36, WHITE, "middle", "bold")
    s.text(400, 176, "D = 30×", 32, WHITE, "middle", "bold")

    # 中层：产出率 × 无错率（青蓝）
    s.polygon([(160, 236), (640, 236), (600, 348), (200, 348)], CYAN)
    s.text(400, 282, "产出率 0.80", 34, WHITE, "middle", "bold")
    s.text(400, 326, "乘无错率 0.81", 34, WHITE, "middle", "bold")

    # 底层：理论 D_k（绿）+ 实测主峰对照
    s.polygon([(200, 388), (600, 388), (560, 500), (240, 500)], GREEN)
    s.text(400, 434, f"理论 D_k={expect:.1f}×", 36, WHITE, "middle", "bold")
    s.text(400, 478, f"峰位 {peak}×", 34, WHITE, "middle", "bold")

    # 侧向收敛箭头（数据流）
    s.arrow(150, 200, 210, 230, CYAN, 6)
    s.arrow(650, 200, 590, 230, CYAN, 6)
    s.arrow(190, 352, 250, 382, CYAN, 6)
    s.arrow(610, 352, 550, 382, CYAN, 6)

    # 右侧红色警示泡：错误尾占种类（两行：词 + 数值）
    s.rect(505, 536, 272, 116, WHITE, RED, 6, rx=16)
    s.text(641, 588, "错误尾占种类", 32, RED, "middle", "bold")
    s.text(641, 632, f"{err_tail:.1f}%", 34, RED, "middle", "bold")

    s.save("04_depth_to_kcov_funnel.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""21_no_peak_err010.py — 生成 21_no_peak_err010.svg（FIG-U06-21：e=0.10 无主峰频谱）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-21（P63，cols 一栏，800×700）【data-plot】。
数据（与 demos 现跑一致）：demos/ch08_kmer_spectrum.py --error-rate 0.10
（G=40,000、D=30×、L=100、k=21、e=0.10、种子 20261102）→ 主峰 4×、
G_est=13,062 bp（偏差 67.3%）；含错 89.1% = 1−0.9^21（教材 §8.4.3 L159）。
对照正常场景一幽灵曲线（灰色虚线，同参数 e=0.01）。纵轴对数、不标刻度。
图注标「合成数据」：demo 行在图内灰字，deck .ref 另行标注。
无网络；种子固定。用法：PYTHONDONTWRITEBYTECODE=1 python3 21_no_peak_err010.py
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "textbook"
                       / "demos"))
import ch08_kmer_spectrum as demo  # noqa: E402

from svghelp import *  # noqa: F401,F403,E402


def spectrum(error_rate):
    rng = np.random.default_rng(20261102)
    genome = demo.random_genome(rng, 40000)
    reads = demo.simulate_reads(genome, 30, 100, error_rate, rng)
    hashes = demo.canonical_kmer_hashes(reads, 21)
    _, counts = np.unique(hashes, return_counts=True)
    hist = np.bincount(counts, minlength=int(counts.max()) + 1)
    return hist.astype(float)


def main():
    bad = spectrum(0.10)
    good = spectrum(0.01)
    sm_bad = demo.smooth(bad)
    body = sm_bad[4:]
    sig = [4 + p for p in demo.local_maxima(body, min_height=0.08 * body.max())]
    if not sig:  # 与 demos run_spectrum 相同回退：无显著峰取全局最大
        sig = [int(4 + np.argmax(body))]
    peak = max(sig)
    g_est = float(sum(i * bad[i] for i in range(4, len(bad)))) / peak
    assert peak == 4 and abs(g_est - 13062) < 1, (peak, g_est)
    assert abs((1 - 0.9 ** 21) - 0.891) < 5e-4
    print(f"check: 主峰 {peak}×，G_est={g_est:,.0f} bp（偏差 "
          f"{abs(g_est - 40000) / 40000:.1%}）；1−0.9^21={1 - 0.9**21:.1%}")

    # 横轴以正常谱为准（0–41）；异常谱在深度 ~12 后自然归零截断
    dmax = len(good) - 1
    dmax_bad = len(bad) - 1
    ymax = math.log10(1 + bad[1:].max())
    X0, X1, Y0, Y1 = 90, 700, 130, 470

    def px(i):
        return X0 + (X1 - X0) * i / dmax

    def py(v):
        return Y1 - (Y1 - Y0) * math.log10(1 + v) / ymax

    s = SVG(800, 700)
    # 顶部参数徽章
    s.rect(60, 54, 170, 56, WHITE, BLUE, 4, rx=12)
    s.text(145, 92, "e=0.10", 32, BLUE, "middle", "bold")
    s.rect(250, 54, 220, 56, WHITE, PANEL, 3, rx=12)
    s.text(360, 92, "含错 89.1%", 30, INK, "middle", "bold")

    s.line(X0, Y0, X0, Y1, INK, 3)
    s.line(X0, Y1, X1 + 10, Y1, INK, 3)

    # 正常场景一幽灵曲线（灰虚线，有主峰）
    ghost = [(px(i), py(good[i])) for i in range(1, dmax + 1)]
    s.curve(ghost, GRAY, 4, dash="12 10")
    # 异常曲线（深蓝，单调滑落无主峰；深度 ≥13 后无数据自然截断）
    pts = [(px(i), py(bad[i])) for i in range(1, dmax_bad + 1)]
    s.curve(pts, BLUE, 6)

    # 峰值处灰色 4× 标注
    s.circle(px(peak), py(bad[peak]), 8, GRAY)
    s.text(px(peak) + 14, py(bad[peak]) - 10, "4×", 30, GRAY, "start", "bold")

    # 红色标签「没有主峰」（唯一红色）
    s.rect(486, 176, 190, 56, WHITE, RED, 4, rx=12)
    s.text(581, 214, "没有主峰", 32, RED, "middle", "bold")

    # 底部结果行
    s.rect(170, 530, 460, 62, BLUE, rx=12)
    s.text(400, 573, "G 估计偏 67.3%", 36, WHITE, "middle", "bold")

    # 图内灰字：合成数据标注 + 复现入口（分两行防溢出）
    s.text(400, 636, "合成数据", 30, GRAY, "middle")
    s.text(400, 678, "demos/ch08_kmer_spectrum.py --error-rate 0.10", 30,
           GRAY, "middle")

    s.save("21_no_peak_err010.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""21_raw_reads_no_peak_spectrum.py — 生成 21_raw_reads_no_peak_spectrum.svg
（FIG-U08-21：原始长读长高错误率致 k-mer 频谱主峰塌缩）

方案：reviews/course/U08_FIGP_001.md §4 FIG-U08-21（P62，cols 一栏，800×700）【data-plot】。
数据（与 demos 现跑一致）：demos/ch08_kmer_spectrum.py 参数 G=40,000、D=30×、
L=100、k=21、种子 20261102——e=0.01 时主峰 ≈19×（理论 30×0.8×0.99^21≈19.4×）；
e=0.10 时含错 1−0.9^21=89.1%，主峰塌至 4×、G 估计偏 67.3%（教材 §8.5.3、讲义 ⑨ E5）。
无网络；种子固定。用法：PYTHONDONTWRITEBYTECODE=1 python3 21_raw_reads_no_peak_spectrum.py
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "textbook"
                       / "demos"))
import ch08_kmer_spectrum as demo  # noqa: E402

from svghelp import *  # noqa: F401,F403,E402

XMAX = 41          # 横轴最大深度（正常谱长度）


def spectrum(error_rate):
    rng = np.random.default_rng(20261102)
    genome = demo.random_genome(rng, 40000)
    reads = demo.simulate_reads(genome, 30, 100, error_rate, rng)
    hashes = demo.canonical_kmer_hashes(reads, 21)
    _, counts = np.unique(hashes, return_counts=True)
    hist = np.bincount(counts, minlength=int(counts.max()) + 1)
    return hist.astype(float)


def analyze(hist):
    sm = demo.smooth(hist)
    body = sm[4:]
    sig = [4 + p for p in demo.local_maxima(body, min_height=0.08 * body.max())]
    if not sig:
        sig = [int(4 + np.argmax(body))]
    peak = max(sig)
    g_est = float(sum(i * hist[i] for i in range(4, len(hist)))) / peak
    return peak, g_est


def main():
    good = spectrum(0.01)
    bad = spectrum(0.10)
    peak_g, g_good = analyze(good)
    peak_b, g_bad = analyze(bad)
    # —— 数据复核（与 demos selftest / U08_FIGP_001 §0 一致）——
    assert 15 <= peak_g <= 24 and abs(g_good - 40000) / 40000 < 0.10
    assert peak_b == 4 and abs(g_bad - 13062) < 1, (peak_b, g_bad)
    assert abs((1 - 0.9 ** 21) - 0.891) < 5e-4
    print(f"check: e=0.01 主峰 {peak_g}×、G≈{g_good:,.0f}；e=0.10 主峰 {peak_b}×、"
          f"G={g_bad:,.0f}（偏 {abs(g_bad - 40000) / 40000:.1%}）、含错 89.1%")

    s = SVG(800, 700)
    panels = [(60, 380, "正常短读长：主峰清晰", GREEN, good, peak_g, False),
              (430, 750, "原始长读长：主峰消失", RED, bad, peak_b, True)]

    for x0, x1, title, color, hist, peak, is_bad in panels:
        y0, y1 = 150, 470
        ymax = math.log10(1 + hist[1:].max())

        def px(i):
            return x0 + (x1 - x0) * i / XMAX

        def py(v):
            return y1 - (y1 - y0) * math.log10(1 + v) / ymax

        s.text((x0 + x1) / 2, 78, title, 32, color, "middle", "bold")
        s.line(x0, y0, x0, y1, INK, 3)
        s.line(x0, y1, x1 + 8, y1, INK, 3)
        for t in (10, 20, 30, 40):
            s.text(px(t), y1 + 40, str(t), 30, GRAY, "middle")
        pts = [(px(i), py(hist[i])) for i in range(1, len(hist))]
        s.curve(pts, color, 6)
        # 主峰/塌缩标注
        s.circle(px(peak), py(hist[peak]), 8, RED if is_bad else GREEN)
        tag_color = GRAY if is_bad else GREEN
        s.text(px(peak) + 16, py(hist[peak]) - 8, f"{peak}×", 32, tag_color,
               "start", "bold")
        # 错误率徽章
        e = "e=0.10" if is_bad else "e=0.01"
        bx = x1 - 118
        s.rect(bx, 104, 118, 44, WHITE, color, 3, rx=10)
        s.text(bx + 59, 136, e, 30, color, "middle", "bold")

    # 底部红色结论框 + 灰字复现入口
    s.rect(160, 548, 480, 62, RED, rx=12)
    s.text(400, 591, "改用外部先验 4 Mb", 36, WHITE, "middle", "bold")
    s.text(400, 656, "合成数据 demos/ch08_kmer_spectrum.py", 30, GRAY, "middle")
    s.text(400, 692, "e=0.01 peak 19x; e=0.10 peak 4x, G bias 67.3%", 30,
           GRAY, "middle")

    s.save("21_raw_reads_no_peak_spectrum.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

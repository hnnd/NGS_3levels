#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_homopolymer_vote_fail.py — 生成 07_homopolymer_vote_fail.svg（FIG-U03-07：投票失效）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-07（P25，cols 一栏，800×700）【data-plot】。
数据：demos/ch04_homopolymer_indel.py --selftest 现跑
（σ=0.7、系统少判起点 L≥7 为 −1 bp、投票 51 次、trials=20000、seed=20261103），
此处用同一函数、同一种子、同一 L 顺序（1…7）复算并断言：
  L=6：单次 0.769 → 投票 0.039（约降 20 倍，偏移 0 bp）；
  L=7：单次 0.819 → 投票 0.971（偏移固化为 −1 bp）。
无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 07_homopolymer_vote_fail.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]  # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch04_homopolymer_indel as demo  # noqa: E402

from svghelp import *  # noqa: F401,F403,E402

Y_BASE, H = 560, 380  # y=560 → 0；y=180 → 1.0


def y_of(rate):
    return Y_BASE - rate * H


def main():
    # 与 demos 完全相同的复算（同一 rng 顺序：L=1..7，每档先单次后投票）
    rng = np.random.default_rng(20261103)
    stats = {}
    for l in range(1, 8):
        single = demo.call_lengths(l, 0.7, 7, 1, 20000, rng)
        single_err = float((single != l).mean())
        votes_mat = demo.call_lengths(l, 0.7, 7, 1, 20000 * 51, rng)
        vote = np.round(votes_mat.reshape(20000, 51).mean(axis=1))
        stats[l] = (single_err, float((vote != l).mean()),
                    float((single - l).mean()), float((vote - l).mean()))
    s6, s7 = stats[6], stats[7]
    assert abs(s6[0] - 0.769) < 5e-4 and abs(s6[1] - 0.039) < 5e-3, \
        f"L=6 与 demos 不符: {s6}"
    assert abs(s7[0] - 0.819) < 5e-4 and abs(s7[1] - 0.971) < 5e-3, \
        f"L=7 与 demos 不符: {s7}"
    print(f"check: L=6 单次 {s6[0]:.3f} → 投票 {s6[1]:.3f}（demos 一致）")
    print(f"check: L=7 单次 {s7[0]:.3f} → 投票 {s7[1]:.3f}（demos 一致）")

    s = SVG(800, 700)
    s.text(400, 48, "同聚物系统少判，多数票原样确认系统偏差", 32, BLUE,
           "middle", "bold")

    # 坐标轴
    s.line(80, 180, 80, Y_BASE, GRAY, 4)
    s.line(80, Y_BASE, 730, Y_BASE, GRAY, 4)
    for v in (0.0, 0.5, 1.0):
        s.text(70, y_of(v) + 10, f"{v:.1f}", 26, GRAY, "end", "bold")

    groups = {"L=6": (240, s6[0], s6[1], GREEN, True),
              "L=7": (560, s7[0], s7[1], RED, False)}
    for lab, (cx, e_single, e_vote, vcol, works) in groups.items():
        xs, xv = cx - 55, cx + 55
        ys, yv = y_of(e_single), y_of(e_vote)
        s.rect(xs - 45, ys, 90, Y_BASE - ys, BLUE, rx=8)
        s.rect(xv - 45, yv, 90, Y_BASE - yv, vcol, rx=8)
        s.text(xs, ys - 14, f"{e_single:.3f}", 28, INK, "middle", "bold")
        s.text(xv, yv - 14, f"{e_vote:.3f}", 28, vcol, "middle", "bold")
        s.text(cx, Y_BASE + 40, lab, 30, INK, "middle", "bold")
        if works:
            s.arrow(xs + 52, ys + 30, xv - 52, yv - 30, GREEN, 6)
            s.text(cx + 96, (ys + yv) / 2, "↓ 20×", 28, GREEN, "middle",
                   "bold")
        else:
            s.arrow(xs + 52, ys + 40, xv - 52, yv + 26, RED, 6)
            s.text(cx, yv - 52, "确认错误", 28, RED, "middle", "bold")

    # 图例与偏移标注（分两行，避免出界）
    s.rect(100, 622, 30, 30, BLUE, rx=6)
    s.text(140, 648, "单次", 28, INK, "start", "bold")
    s.rect(230, 622, 30, 30, GREEN, rx=6)
    s.text(270, 648, "投票", 28, INK, "start", "bold")
    s.text(400, 692,
           f"偏移：L=6 → {s6[3]:+.2f} bp ｜ L=7 → {s7[3]:+.2f} bp",
           26, GRAY, "middle", "bold")

    s.save("07_homopolymer_vote_fail.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

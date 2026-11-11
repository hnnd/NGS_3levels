#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_k_seeding_tradeoff.py — 生成 04_k_seeding_tradeoff.svg（FIG-U05-04：-k 杠杆）

方案：reviews/course/U05_FIGP_001.md §4 FIG-U05-04（P22，cols 一栏，viewBox 800×700）【data-plot】。
折线图：x＝错误率 5%/10%/15%，y＝无种子%；k=19（绿）/ k=32（橙）两条线；
k=32@15%＝71.50 红点＋引线「一条种子都找不到」；k=19@15%＝10.25 灰点。
数据由 demos/ch07_seed_extend.py 的函数现跑取数（固定种子 20261103，每档 400 条，
与方案 §0.2 及 deck P22 现表逐位一致，Q5）；不手抄。依据教材 §7.4.3 L144–148。
无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 04_k_seeding_tradeoff.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]  # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch07_seed_extend as demo  # noqa: E402

from svghelp import *  # noqa: F401,F403


def main():
    # ---- 与 demos --selftest 完全相同的合成流程（固定种子），取扫描表 ----
    k_list = [19, 32]
    err_list = [0.05, 0.10, 0.15]
    rng = np.random.default_rng(demo.SEED)
    genome = demo.make_genome(rng, 20000)
    reads_by_err = {
        e: demo.make_reads(np.random.default_rng(demo.SEED + int(e * 1000)),
                           genome, 400, 150, e)
        for e in err_list}
    results = demo.sweep(genome, reads_by_err, k_list, 100)
    u19 = [round(results[(19, e)][1], 2) for e in err_list]
    u32 = [round(results[(32, e)][1], 2) for e in err_list]

    # 复现锚（方案 §0.2 ＝ demos --selftest 扫描表，2026-11-10 重跑一致）
    assert u19 == [0.00, 1.00, 10.25], f"k=19 无种子% {u19}"
    assert u32 == [2.75, 36.00, 71.50], f"k=32 无种子% {u32}"
    print(f"check: k=19 无种子% {'/'.join(f'{v:.2f}' for v in u19)}；"
          f"k=32 无种子% {'/'.join(f'{v:.2f}' for v in u32)}")

    s = SVG(800, 700)

    # 绘图区：x 90–740，y 90–545（y=0 在 545，y=80% 在 90）
    x0, x1, yb, yt = 90, 740, 545, 90
    xs = {0.05: 170, 0.10: 400, 0.15: 630}

    def yv(v):
        return yb - v / 80.0 * (yb - yt)

    s.text(95, 60, "unseeded %", 30, GRAY, "start", "bold")

    # 轴与刻度
    s.line(x0, yb, x1, yb, GRAY, 5)
    s.line(x0, yb, x0, yt, GRAY, 5)
    for v in (0, 20, 40, 60, 80):
        s.line(x0 - 8, yv(v), x0, yv(v), GRAY, 4)
        s.text(x0 - 14, yv(v) + 10, str(v), 30, GRAY, "end", "bold")
    for e in err_list:
        s.text(xs[e], yb + 44, f"{e:.0%}", 30, GRAY, "middle", "bold")
    s.text(430, yb + 92, "error rate", 30, GRAY, "middle", "bold")

    # 两条折线
    s.polyline([(xs[e], yv(u19[i])) for i, e in enumerate(err_list)], GREEN, 7)
    s.polyline([(xs[e], yv(u32[i])) for i, e in enumerate(err_list)], ORANGE, 7)

    # k=32@15% 红点 + 引线 + k=19@15% 灰点
    s.circle(xs[0.15], yv(71.50), 10, RED)
    s.line(xs[0.15], yv(71.50) - 12, xs[0.15], yv(71.50) - 30, RED, 4)
    s.text(xs[0.15], 84, "一条种子都找不到", 30, RED, "middle", "bold")
    s.text(650, yv(71.50) + 34, "71.50", 30, RED, "start", "bold")
    s.circle(xs[0.15], yv(10.25), 8, GRAY)
    s.text(650, yv(10.25) + 12, "10.25", 30, GRAY, "start", "bold")

    # 图例
    s.line(110, 162, 160, 162, GREEN, 7)
    s.text(172, 170, "k=19", 30, INK, "start", "bold")
    s.line(110, 202, 160, 202, ORANGE, 7)
    s.text(172, 210, "k=32", 30, INK, "start", "bold")

    # 图内文字（方案逐字）
    s.text(110, 122, "种子越长丢得越多", 32, INK, "start", "bold")
    s.text(60, yb + 92, "无种子＝整条必丢", 32, INK, "start", "bold")

    s.text(740, yb + 92, "400 reads/档", 30, GRAY, "end", "bold")

    s.save("04_k_seeding_tradeoff.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

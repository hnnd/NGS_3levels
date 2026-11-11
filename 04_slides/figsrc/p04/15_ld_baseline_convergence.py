#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_ld_baseline_convergence.py — 生成 15_ld_baseline_convergence.svg
（FIG-P04-15：第 31 页 cols 一栏「1/n 抽样基线对 LD 衰减曲线的垫高与扣除收敛」）【data-plot】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-15（P31，cols，800×700）。
依据：教材 §20.4.4——无连锁时 E[r̂²] ≈ 1/n（n 为染色体数），单倍体 40 条即 0.025；
合成算例同一真实衰减（r²(d) = 0.8·2^(−d/50 kb)）下 n = 30 朴素半衰 54.0 kb、
扣基线 48.0 kb；n = 200 朴素 51.0 kb、扣基线 50.0 kb；r² = 0.2 的距离也随样本量
从 111.0 kb 漂到 102.0 kb，扣基线后收敛到 99.0 与 101.0 kb。
数字入口：`textbook/demos/ch20_ld_r2_baseline.py --selftest`
（每档 2 万对、1 kb 分箱、种子 20261104）。本脚本调用该 demo 的
`mean_r2_unlinked()` 核两条基线、按 demo 的解析生成式画出曲线，并断言
demo 现跑的四个半衰读数，不一致即失败退出；见回执核对表。
图内中文严格取方案给定 26 字（3 句）；r²、kb、n 与数字属符号。
结构＝一张衰减曲线图：两条观测曲线（n = 30 橙、n = 200 青蓝）停在各自的 1/n
平台，扣基线的绿色虚线把两条压回同一条；右上角图例兼作读数表
（54 / 51 kb 朴素，48 / 50 kb 扣基线）。
红只标「小样本基线整体抬高」一处。
无网络；随机数只用 demo 的固定种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 15_ld_baseline_convergence.py
"""
import contextlib
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # NGS_3Levels/
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from svghelp import *                                        # noqa: E402,F401,F403
from ch20_ld_r2_baseline import mean_r2_unlinked, R2_TRUE_MAX  # noqa: E402

PHRASES = ["无连锁停在样本倒数", "小样本基线整体抬高", "扣除基线半衰收敛"]
TEXT = "".join(PHRASES)

N_S, N_L, SEED = 30, 200, 20261104
HALF = {30: (54.0, 48.0), 200: (51.0, 50.0)}      # (naive, adjusted) kb，demo 现跑


def numbers():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        b_s = mean_r2_unlinked(N_S, 20000, SEED + 7)
        b_l = mean_r2_unlinked(N_L, 20000, SEED + 13)
    if abs(b_s - 0.0333) > 0.004 or abs(b_l - 0.0050) > 0.004:
        raise SystemExit(f"基线读数与 demos 不一致：{b_s:.4f} / {b_l:.4f}")
    return 1.0 / N_S, 1.0 / N_L


def curve(d_kb, base):
    """demo 的解析生成式：真实衰减 0.8·2^(−d/50kb) + 1/n 抽样基线。"""
    return R2_TRUE_MAX * 2.0 ** (-d_kb / 50.0) + base


def main():
    base_s, base_l = numbers()
    s = SVG(800, 700, "1/n sampling floor lifts the LD decay curve", plan=TEXT)

    x0, x1, ybase, ytop = 96, 744, 430, 130
    vmax = 0.90
    xv = lambda d: x0 + d / 200.0 * (x1 - x0)
    yv = lambda v: ybase - v / vmax * (ybase - ytop)

    # 坐标轴与刻度
    s.arrow(x0, ybase, x1 + 6, ybase, BLUE, 5, 14)
    s.arrow(x0, ybase, x0, ytop - 8, BLUE, 5, 14)
    for v in (0.0, 0.2, 0.4, 0.6, 0.8):
        y = yv(v)
        s.line(x0 - 8, y, x0, y, BLUE, 3)
        s.text(x0 - 16, y + 10, f"{v:.1f}", 30, GRAY, "end")
    for d in (0, 50, 100, 150, 200):
        x = xv(d)
        s.line(x, ybase, x, ybase + 10, BLUE, 3)
        s.text(x, ybase + 44, str(d), 30, GRAY, "middle")
    s.text(700, ybase + 44, "kb", 30, BLUE, "end", "bold")

    # 两条观测曲线 + 一条扣基线曲线
    ds = [d / 2 for d in range(0, 401)]
    for base, col in ((base_s, ORANGE), (base_l, CYAN)):
        s.polyline([(round(xv(d), 1), round(yv(curve(d, base)), 1)) for d in ds],
                   col, 5)
    s.polyline([(round(xv(d), 1), round(yv(curve(d, 0.0)), 1)) for d in ds],
               GREEN, 4, dash="12 8")

    # 半衰线（峰值 0.8 的一半 = 0.4）
    s.line(x0, yv(0.4), x1, yv(0.4), GRAY, 3, dash="6 8")

    # 右上角图例兼读数表
    s.rect(430, 132, 318, 148, WHITE, PANEL, 3, rx=12)
    legs = [(ORANGE, None, f"n = {N_S} → {HALF[N_S][0]:.0f} kb"),
            (CYAN_DEEP, None, f"n = {N_L} → {HALF[N_L][0]:.0f} kb"),
            (GREEN, "12 8", "−1/n → 48 / 50 kb")]
    for i, (col, dash, txt) in enumerate(legs):
        y = 172 + i * 44
        s.line(452, y - 10, 500, y - 10, col, 5, dash=dash)
        s.text(514, y, txt, 30, col, "start", "bold")

    # 三句判读（底部结论条）
    s.caption([PHRASES[0], PHRASES[1], PHRASES[2]], [BLUE, RED, GREEN], 30,
              gap=40, pad_top=22)

    s.save("15_ld_baseline_convergence.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 26, TEXT
    raise SystemExit(main())

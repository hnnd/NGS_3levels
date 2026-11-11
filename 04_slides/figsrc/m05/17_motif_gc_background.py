#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_motif_gc_background.py — FIG-M05-17 背景不匹配制造假富集（data-plot）

方案：`reviews/course/M05_FIGP_001.md` §4.2 FIG-M05-17（P37，`.cols` 800×700，data-plot）。
数据入口：`textbook/demos/ch15_motif_gc_background.py` Part 1 合成算例——
实测 GC：前景 0.549、随机背景 0.400；GC-rich 诱饵 GCbox 前景命中 210/2000，
GC 匹配背景 226/2000（富集 0.93×、p = 0.806，不显著），随机背景 36/2000
（富集 5.83×、p = 4.12×10⁻³³，虚假显著）。
本脚本用 demo 的模拟函数与同种子复算并断言，图上只上这四项数字。

★ 与配图方案冲突，已按 demos/教材口径处理：方案 §4.2 写「前景 60.2% vs 45.0%」，
demo 实测与教材 §15.4.6 正文都是 0.549 / 0.400（54.9% / 40.0%）。任务卡要求
data-plot 的数字与 demos 输出逐一核对，故取后者；差异登记在回执 issues。

排版说明：p 值与 GC 两项数字宽度差很大（「p = 4.1×10^-33」约 214 单位），
若各居中于柱下必然相撞（初版即为此返工），故改为柱下小表：列头「匹配/随机」，
两行分别左对齐 p 与 GC。指数写成 `×10^-33`（与图 08 的 `10^-6` 同一写法）；
CJK 字体缺上标负号（U+207B）与上标数字，直接写会渲染成方框。
图内汉字 29 字：标题「背景不匹配」5；结论「前景高碱基偏差制造虚假显著基序」14
＋纵轴「富集倍数」4 ＋列头「匹配」「随机」4 ＋基线「前景」2。
红只用于随机背景的假富集（柱合成一条 path 1 处 + p 值 1 处 = 2 处）。
无网络；随机数仅经 demo 同种子复算。超几何尾概率改用 demo 自带的手算实现
（`hypergeom_sf_hand`，math.comb），本脚本因此只依赖标准库 + numpy。
用法：PYTHONDONTWRITEBYTECODE=1 python3 17_motif_gc_background.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]              # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from ch15_motif_gc_background import (                   # noqa: E402
    GCBOX, SEED, hypergeom_sf_hand, motif_hits, simulate_sequences,
)

from svghelp import *                                    # noqa: F401,F403,E402

N_SEQ, SEQ_LEN = 2000, 300
GC_PEAK, GC_GENOME = 0.55, 0.40
rng = np.random.default_rng(SEED)
# 与 demo Part 1 相同的调用顺序：前景 → 匹配背景 → 随机背景 → 三条 NeuM 命中
seq_peak = simulate_sequences(rng, N_SEQ, GC_PEAK, SEQ_LEN)
seq_match = simulate_sequences(rng, N_SEQ, GC_PEAK, SEQ_LEN)
seq_rand = simulate_sequences(rng, N_SEQ, GC_GENOME, SEQ_LEN)
_ = rng.random(N_SEQ)                                   # hits_neu_peak
_ = rng.random(N_SEQ)                                   # hits_neu_match
_ = rng.random(N_SEQ)                                   # hits_neu_rand
hit_peak = motif_hits(seq_peak, GCBOX)
hit_match = motif_hits(seq_match, GCBOX)
hit_rand = motif_hits(seq_rand, GCBOX)

GC_P = float(np.isin(seq_peak, ["C", "G"]).mean())
GC_R = float(np.isin(seq_rand, ["C", "G"]).mean())
K_PEAK, K_MATCH, K_RAND = int(hit_peak.sum()), int(hit_match.sum()), int(hit_rand.sum())


def hyper(k, K):
    """与 demo row() 同口径：总体 2N、成功态 = 前景+背景命中、抽 n = N。

    直接调用 demo 的手算实现（math.comb），不依赖 scipy；两条尾概率
    （0.806 与 4.12×10^-33）与 demo `--selftest` 打印值一致。
    """
    return float(hypergeom_sf_hand(k, 2 * N_SEQ, k + K, N_SEQ))


FOLD_MATCH = (K_PEAK / N_SEQ) / (K_MATCH / N_SEQ)
FOLD_RAND = (K_PEAK / N_SEQ) / (K_RAND / N_SEQ)
P_MATCH, P_RAND = hyper(K_PEAK, K_MATCH), hyper(K_PEAK, K_RAND)

# 与 demos --selftest Part 1 的打印值逐一相符
assert round(GC_P, 3) == 0.549 and round(GC_R, 3) == 0.400, (GC_P, GC_R)
assert (K_PEAK, K_MATCH, K_RAND) == (210, 226, 36), (K_PEAK, K_MATCH, K_RAND)
assert abs(FOLD_MATCH - 0.93) < 5e-3 and abs(FOLD_RAND - 5.83) < 5e-3
assert abs(P_MATCH - 0.806) < 5e-3 and P_RAND < 1e-30

s = SVG()

s.text(400, 62, "背景不匹配", 36, BLUE, "middle", "bold")

# ---- 坐标框 ----
L, B, T = 180, 430, 216
YMAX = 6.6
BAR_W, GAP = 110, 90


def py(v):
    return B - (B - T) * v / YMAX


def bx(i):
    return 216 + i * (BAR_W + GAP)


s.line(L, B, bx(1) + BAR_W + 32, B, INK, 4)
s.line(L, B, L, T, INK, 4)
s.text(L, T - 44, "富集倍数", 30, GRAY, "start")
for v in (2, 4, 6):
    s.line(L - 10, py(v), L, py(v), INK, 3)
    s.text(L - 18, py(v) + 10, str(v), 30, GRAY, "end")

# ---- 匹配背景（0.93×）：绿 ----
s.rect(bx(0), py(FOLD_MATCH), BAR_W, B - py(FOLD_MATCH), GREEN, rx=8)
s.text(bx(0) + BAR_W / 2, py(FOLD_MATCH) - 18, "0.93", 34, GREEN, "middle", "bold")
s.text(bx(0) + BAR_W / 2, 502, "匹配", 30, INK, "middle", "bold")

# ---- 随机背景（5.83×）：红（柱合成一条 path，红记 1 处）----
s.path(f"M {bx(1)} {B} L {bx(1)} {py(FOLD_RAND):.1f} "
       f"L {bx(1) + BAR_W} {py(FOLD_RAND):.1f} L {bx(1) + BAR_W} {B} Z",
       RED, 2, fill=RED)
s.text(bx(1) + BAR_W / 2, py(FOLD_RAND) - 18, "5.83", 34, INK, "middle", "bold")
s.text(bx(1) + BAR_W / 2, 502, "随机", 30, INK, "middle", "bold")

# ---- 前景基准线（前景自身 = 1×）----
s.line(L, py(1.0), bx(1) + BAR_W + 32, py(1.0), BLUE, 4, dash="14 10")
s.text(bx(1) + BAR_W + 40, py(1.0) - 12, "前景 1×", 30, BLUE, "start", "bold")

# ---- 两列小表：p 与 GC 口径（列内左对齐，避免中轴文字相撞）----
for i, (p_txt, gc_txt, color) in enumerate((
        ("p = 0.806", "GC 0.549", GREEN),
        ("p = 4.1×10^-33", "GC 0.400", RED))):
    x = bx(i)
    s.text(x, 552, p_txt, 30, color, "start", "bold")
    s.text(x, 598, gc_txt, 30, GRAY, "start")

# ---- 结论行（方案原句 14 字）----
s.text(400, 660, "前景高碱基偏差制造虚假显著基序", 30, INK, "middle", "bold")

s.save("17_motif_gc_background.svg")
print(f"check: GC {GC_P:.3f}/{GC_R:.3f}；命中 {K_PEAK}/{K_MATCH}/{K_RAND}；"
      f"富集 {FOLD_MATCH:.2f}×/{FOLD_RAND:.2f}×；p {P_MATCH:.3g}/{P_RAND:.3g}")

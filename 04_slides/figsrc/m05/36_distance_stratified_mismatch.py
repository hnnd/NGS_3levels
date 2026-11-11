#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""36_distance_stratified_mismatch.py — FIG-M05-36 真实距离分层错配率（data-plot）

方案：`reviews/course/M05_FIGP_001.md` §4.4 FIG-M05-36（P60，`.cols` 800×700，data-plot）。
数据入口：`textbook/demos/ch15_nearest_gene_mismatch.py` Part 1（分层错配率）与 Part 3
（≤10 kb 截断的代价）。教材依据 §15.5.3 L367–L376、§15.4.5。

本脚本按 demo 的同一随机种子与同一调用顺序复算——Part 1 先跑一次 `simulate`，Part 2 再跑
一次，Part 2b 跑四次，Part 3 复用 Part 1 的结果——然后直接取 `stratify()` 与截断口径的
输出，**不硬写任何百分比**。四层（0–10 kb / 10–30 kb / 30–60 kb / 60–150 kb）与截断对照组
的数字因此与本机 `--selftest` 的 PASS 行逐位相符，脚本里的断言就是那条判据。

画法：五根柱，前四根按距离分层由近到远（近距离橙 `#F39B7F`、最远层警示红），第五根是
「只信 ≤10 kb」截断后的对照（深蓝，旁边标可注释比例）。横轴为距离分层，纵轴为错配率。
错配率随距离单调上升这件事由柱高直接读出来，数字同时写在柱顶（复现入口是 demo）。

图内汉字 28 字（上限 30），结论逐字取方案原句「错配单调上升：距离越远无关基因越多，
错配率剧增」：标题「错配率」3 ＋「错配单调上升」6 ＋「距离越远无关基因越多」10
＋「错配率剧增」5 ＋ 轴名「真实距离」4 ＝ 28。第五根柱脚下的 55% 是 demo Part 3 打印的可注释比例
（只采用 ≤10 kb 的元件时还能注释的比例），数字不加汉字。
数字均为 demo 输出；配色按方案。
无随机数自造（只用 demo 的同种子复算）、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 36_distance_stratified_mismatch.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]              # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from ch15_nearest_gene_mismatch import (SEED, simulate, stratify)   # noqa: E402

from svghelp import *                                    # noqa: F401,F403,E402

# ---- 按 demo main() 的调用顺序复算（Part 1 → Part 2 → Part 2b → Part 3）----
rng = np.random.default_rng(SEED)
CHROM_KB = 120.0 * 1000.0
N_ENH = 400

mism, skipped, dists, ndist, n_genes = simulate(
    rng, CHROM_KB, 25.0, N_ENH, np.log(25.0), 0.6)        # Part 1（稀疏，间距 25 kb）
STRATA = stratify(mism, dists)
simulate(rng, CHROM_KB, 8.0, N_ENH, np.log(25.0), 0.6)     # Part 2（紧凑）
for d_geo in (6.0, 25.0, 60.0):                             # Part 2b 三次扫描
    simulate(rng, CHROM_KB, 25.0, N_ENH, np.log(d_geo), 0.6)
simulate(rng, CHROM_KB, 8.0, N_ENH, np.log(4.0), 0.6)      # Part 2b 末次

# ---- Part 3：≤10 kb 截断（复用 Part 1 的结果）----
keep = ndist <= 10.0
TRUNC_RATE = float(mism[keep].mean())
TRUNC_COVER = float(keep.mean())

# 与 demo --selftest 的打印逐条相符
assert [round(r, 3) for _, _, _, r in STRATA] == [0.200, 0.650, 0.857, 0.921], \
    [r for _, _, _, r in STRATA]
assert round(TRUNC_RATE, 3) == 0.744, TRUNC_RATE
assert round(TRUNC_COVER, 2) == 0.55, TRUNC_COVER

s = SVG()

s.text(400, 60, "错配率", 36, BLUE, "middle", "bold")

# ---------------- 坐标框 ----------------
L, R, B, T = 120, 700, 470, 168
YMAX = 1.0


def px_of(v):
    return B - (B - T) * v / YMAX


s.line(L, B, R, B, INK, 4)
s.line(L, B, L, T, INK, 4)
s.text(L - 4, T - 28, "真实距离 kb", 30, GRAY, "start")

for frac in (0.25, 0.50, 0.75, 1.00):
    s.line(L, px_of(frac), L - 8, px_of(frac), INK, 3)
    s.text(L - 18, px_of(frac) + 10, f"{int(frac * 100)}%", 30, GRAY, "end")

# ---------------- 五根柱：四层 + 截断对照 ----------------
N = 5
SLOT = (R - L) / N
BW = 74
LABELS = ["0–10", "10–30", "30–60", "60–150", "≤10"]
VALUES = [r for _, _, _, r in STRATA] + [TRUNC_RATE]
COLORS = [ORANGE, ORANGE, RED, RED, BLUE]
SUB = [""] * 4 + ["55%"]

for i, (lab, v, color) in enumerate(zip(LABELS, VALUES, COLORS)):
    cx = L + SLOT * (i + 0.5)
    s.rect(cx - BW / 2, px_of(v), BW, B - px_of(v), color, None, rx=8)
    s.text(cx, B + 40, lab, 30,
           BLUE if i == N - 1 else GRAY, "middle", "bold" if i == N - 1 else None)
    # 百分比写在柱顶上方（红色柱上的数字用墨色，避免红字叠加）
    s.text(cx, px_of(v) - 16, f"{v * 100:.1f}%", 30,
           INK if color == RED else color, "middle", "bold")

# 截断组的可注释比例（demo Part 3 的 keep.mean()）写在柱内底部，避免与横轴标签拥挤
s.text(L + SLOT * 4.5, B - 18, f"{TRUNC_COVER:.0%}", 30, WHITE, "middle", "bold")

# 截断对照组单独加一道竖向分隔，说明它不在距离分层轴上
sep_x = L + SLOT * 4 - 6
s.line(sep_x, T - 12, sep_x, B, GRAY, 3, dash="10 8")

# ---------------- 结论（方案原句逐字） ----------------
s.text(400, 566, "错配单调上升", 32, BLUE, "middle", "bold")
s.text(400, 618, "距离越远无关基因越多", 32, INK, "middle", "bold")
s.text(400, 672, "错配率剧增", 32, BLUE, "middle", "bold")

s.save("36_distance_stratified_mismatch.svg")
print("check: 分层 " + " ".join(f"{lab}={v * 100:.1f}%"
                              for lab, v in zip(LABELS, VALUES))
      + f"；≤10 kb 截断后可注释 {TRUNC_COVER:.0%}")

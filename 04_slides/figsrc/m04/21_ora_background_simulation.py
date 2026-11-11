#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-21 ORA 背景集合成算例对比（data-plot）。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-21；配色：spec.md §2。
数字复现：textbook/demos/ch14_ora_background.py Part 1（import 复算 + 断言）。"""
import sys
from pathlib import Path

import numpy as np
from scipy import stats

from svghelp import *

DEMO_DIR = Path(__file__).resolve().parents[3] / "textbook" / "demos"
sys.path.insert(0, str(DEMO_DIR))
import ch14_ora_background as demo   # noqa: E402

# ---- 与 demo main() Part 1 完全一致的生成逻辑（同 seed、同调用顺序）----
rng = np.random.default_rng(demo.SEED)
N = 30000
pathways = [rng.choice(N, size=40, replace=False) for _ in range(200)]
in_any = np.zeros(N, dtype=bool)
for pw in pathways:
    in_any[pw] = True
p_test = np.where(in_any, 1.0, 0.5)
tested = rng.random(N) < p_test
n_tested = int(tested.sum())
k_annot = int(in_any.sum())
k_tested = int((in_any & tested).sum())
de = rng.choice(np.where(tested)[0], size=3000, replace=False)
p_correct = np.empty(200)
p_wrong = np.empty(200)
for j, pw in enumerate(pathways):
    k_hit = int(np.isin(de, pw).sum())
    K_c = int(tested[pw].sum())
    p_correct[j] = stats.hypergeom.sf(k_hit - 1, n_tested, K_c, 3000)
    p_wrong[j] = stats.hypergeom.sf(k_hit - 1, N, 40, 3000)
adj_c = demo.bh_adjust(p_correct)
adj_w = demo.bh_adjust(p_wrong)
sig_c = int((adj_c < 0.05).sum())
sig_w = int((adj_w < 0.05).sum())
med_c = float(np.median(p_correct))
med_w = float(np.median(p_wrong))
ratio = float(np.median(p_wrong / p_correct))
pushed = int(((p_correct >= 0.05) & (p_wrong < 0.05)).sum())

# ---- 与 demo --selftest 打印值逐一核对 ----
assert n_tested == 18670 and k_annot == 6994 and k_tested == 6994
assert sig_c == 0 and sig_w == 22, (sig_c, sig_w)
assert round(med_c, 3) == 0.639 and round(med_w, 3) == 0.206
assert round(ratio, 3) == 0.323
assert pushed == 43
print(f"checked vs demo: sig {sig_c} vs {sig_w} · median {med_c:.3f} vs "
      f"{med_w:.3f} · ratio {ratio:.3f} · pushed {pushed}")

s = SVG()

s.label(400, 52, ["真实零富集"], 30, BLUE, weight="bold")

# ---- 左：显著 term 数对比 ----
s.text(200, 100, "显著 Term 数", 30, GRAY, "middle")
s.text(200, 138, "(BH < 0.05)", 30, GRAY, "middle")
base = 480
for x, v, col, lab in ((110, sig_c, GREEN, "正确背景"),
                       (230, sig_w, RED, "错误背景")):
    h = max(v * 12, 6)
    s.rect(x, base - h, 70, h, col, None)
    s.text(x + 35, base - h - 16, str(v), 36, col, "middle", "bold")
s.line(90, base, 330, base, BLUE, 4)
s.text(145, 516, "正确", 30, INK, "middle")
s.text(265, 516, "错误", 30, INK, "middle")
s.text(200, 566, "真实富集 = 0", 30, GRAY, "middle")

# ---- 右：p 值中位数对比 ----
s.text(580, 108, "p 值中位数", 30, GRAY, "middle")
for x, v, col in ((500, med_c * 420, GREEN), (620, med_w * 420, ORANGE)):
    s.rect(x, base - v, 70, v, col, None)
s.line(480, base, 720, base, BLUE, 4)
s.text(535, base - med_c * 420 - 16, "0.639", 32, INK, "middle", "bold")
s.text(655, base - med_w * 420 - 16, "0.206", 32, INK, "middle", "bold")
s.text(580, 516, "整体压缩至 0.323 倍", 30, GRAY, "middle")
s.text(560, 566, "43 个边缘 Term 被推进", 30, GRAY, "middle")

# ---- 中文结论 ----
s.label(400, 622, ["错误背景虚报二十二项"], 30, INK, weight="bold")
s.label(400, 670, ["值整体压缩三分之二"], 30, INK)

s.save("21_ora_background_simulation.svg")

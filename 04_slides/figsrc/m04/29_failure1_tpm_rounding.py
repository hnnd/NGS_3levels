#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-29 失效一 round(TPM)：假阳性率失控与 size factor 失明（data-plot）。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-29；配色：spec.md §2。
数字复现：textbook/demos/ch14_tpm_rounding.py Part 1 & Part 2（import 复算 + 断言）。"""
import sys
from pathlib import Path

import numpy as np

from svghelp import *

DEMO_DIR = Path(__file__).resolve().parents[3] / "textbook" / "demos"
sys.path.insert(0, str(DEMO_DIR))
import ch14_tpm_rounding as demo   # noqa: E402

# ---- 与 demo main() 完全一致的生成逻辑（同 seed、同调用顺序）----
rng = np.random.default_rng(demo.SEED)
n_rep, alpha = 6, 0.15
x = np.concatenate([np.zeros(n_rep), np.ones(n_rep)])
s = np.tile(np.array([0.4, 0.5, 0.7, 1.5, 2.0, 3.0]), 2)
s[:n_rep] = s[:n_rep][rng.permutation(n_rep)]
s[n_rep:] = s[n_rep:][rng.permutation(n_rep)]
log_s = np.log(s)
half = 4000 // 2
beta = np.concatenate([np.zeros(half), np.full(4000 - half, 1.5)])
beta[rng.permutation(4000)[:1000]] *= -1
mu_base = rng.lognormal(mean=np.log(800.0), sigma=1.5, size=4000)
len_kb = rng.lognormal(mean=np.log(2.0), sigma=0.5, size=4000)
mu = mu_base[:, None] * s[None, :] * 2.0 ** (beta[:, None] * x[None, :])
y = rng.negative_binomial(1.0 / alpha, (1.0 / alpha) / (1.0 / alpha + mu),
                          mu.shape)
tpm_round = np.rint(y / (len_kb[:, None] * y.sum(axis=0, keepdims=True))
                    * 1e6)

p_raw, _ = demo.run_path(y, x, log_s, log_s)
p_tpm, _ = demo.run_path(tpm_round, x, np.zeros(12), np.zeros(12))
h0 = beta == 0
h1 = ~h0
fpr_raw = float((p_raw[h0] < 0.05).mean())
fpr_tpm = float((p_tpm[h0] < 0.05).mean())
pow_raw = float((p_raw[h1] < 0.05).mean())
pow_tpm = float((p_tpm[h1] < 0.05).mean())
sf_tpm = demo.median_of_ratios(tpm_round)
s_rel = s / np.exp(np.log(s).mean())

# ---- 与 demo --selftest 打印值逐一核对 ----
assert round(fpr_raw, 3) == 0.038 and round(fpr_tpm, 3) == 0.288
assert round(pow_raw, 3) == 0.978 and round(pow_tpm, 3) == 0.744
assert round(float(s_rel.min()), 2) == 0.38
assert round(float(s_rel.max()), 2) == 2.89
assert round(float(sf_tpm.min()), 2) == 0.93
assert round(float(sf_tpm.max()), 2) == 1.14
print(f"checked vs demo: FPR {fpr_raw:.3f} vs {fpr_tpm:.3f} · power "
      f"{pow_raw:.3f} vs {pow_tpm:.3f} · sf {sf_tpm.min():.2f}-{sf_tpm.max():.2f}")

s = SVG()

# ---- 左：假阳性率 / 检出率对比 ----
s.text(190, 70, "假阳性率 (H0) / 检出率 (H1)", 30, GRAY, "middle")
base = 460
for gx, v, col, sc in ((90, fpr_raw, GREEN, 1000), (170, fpr_tpm, RED, 1000),
                       (270, pow_raw, GREEN, 260),
                       (350, pow_tpm, RED, 260)):
    h = v * sc
    s.rect(gx, base - h, 56, h, col, None)
    s.text(gx + 28, base - h - 14, f"{v:.3f}", 30, INK, "middle", "bold")
s.line(70, base, 430, base, BLUE, 4)
s.text(158, 500, "H0 假阳性", 30, GRAY, "middle")
s.text(310, 500, "H1 检出率", 30, GRAY, "middle")
s.text(190, 550, "虚增 7.6 倍", 30, INK, "middle", "bold")
s.text(190, 608, "原始计数假阳性达标", 30, GREEN, "middle", "bold")
s.text(190, 664, "假整数假阳性失控", 30, INK, "middle", "bold")

# ---- 右：文库因子失明散点 ----
s.text(610, 70, "文库因子估计", 30, GRAY, "middle")
rx0, ry0, rw, rh = 470, 120, 300, 340
s.rect(rx0, ry0, rw, rh, WHITE, BLUE, 4, rx=8)

def mx(v):
    return rx0 + 30 + (np.log(v) - np.log(0.3)) / (np.log(3.0) - np.log(0.3)) \
        * (rw - 60)

def my(v):
    return ry0 + rh - 30 - (np.log(v) - np.log(0.3)) / \
        (np.log(3.0) - np.log(0.3)) * (rh - 60)

s.line(mx(0.3), my(0.3), mx(3.0), my(3.0), PANEL, 4, dash="10 8")
s.line(mx(0.85), my(1.0), mx(1.2), my(1.0), BLUE, 6)
s.text(478, 170, "≈ 1 (0.93–1.14)", 30, INK, "start", "bold")
for sv, fv in zip(s_rel, sf_tpm):
    s.circle(mx(sv), my(sv), 5, PANEL)
    s.circle(mx(sv), my(fv), 9, CYAN_DEEP)
s.text(rx0 + rw / 2, ry0 + rh + 36, "真实深度 (0.38–2.89)", 30, GRAY,
       "middle")
s.text(610, 664, "文库因子估计失明", 30, INK, "middle", "bold")

s.save("29_failure1_tpm_rounding.svg")

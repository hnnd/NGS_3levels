#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-31 失效三 参照系设反 log2FC 反号（data-plot）。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-31；配色：spec.md §2。
数字复现：textbook/demos/ch14_reversed_reflevel.py Part 1（import 复算 + 断言）。"""
import sys
from pathlib import Path

import numpy as np

from svghelp import *

DEMO_DIR = Path(__file__).resolve().parents[3] / "textbook" / "demos"
sys.path.insert(0, str(DEMO_DIR))
import ch14_reversed_reflevel as demo   # noqa: E402

# ---- 与 demo main() 完全一致的生成逻辑（同 seed、同调用顺序）----
rng = np.random.default_rng(demo.SEED)
n_rep, alpha, ng = 6, 0.15, 2400
x = np.concatenate([np.zeros(n_rep), np.ones(n_rep)])
half = ng // 2
beta_true = np.concatenate([np.zeros(half), np.full(ng - half, 1.5)])
beta_true[half + rng.permutation(ng - half)[: (ng - half) // 2]] = -1.5
mu_base = rng.lognormal(mean=np.log(800.0), sigma=1.5, size=ng)
mu = mu_base[:, None] * 2.0 ** (beta_true[:, None] * x[None, :])
y = rng.negative_binomial(1.0 / alpha, (1.0 / alpha) / (1.0 / alpha + mu),
                          mu.shape)

b_ok = np.empty(ng)
p_ok = np.empty(ng)
b_rev = np.empty(ng)
p_rev = np.empty(ng)
for i in range(ng):
    b_ok[i], p_ok[i] = demo.nb_glm_wald(y[i].astype(float), x, alpha)
    b_rev[i], p_rev[i] = demo.nb_glm_wald(y[i].astype(float), 1.0 - x, alpha)
sig_ok = p_ok < 0.05
sig_rev = p_rev < 0.05
up_ok = sig_ok & (b_ok > 1)
up_rev = sig_rev & (b_rev > 1)
sign_ok = float((np.sign(b_ok[beta_true != 0])
                 == np.sign(beta_true[beta_true != 0])).mean())
sign_rev = float((np.sign(b_rev[beta_true != 0])
                  == np.sign(beta_true[beta_true != 0])).mean())
up_rev_true = float((np.sign(beta_true[up_rev]) > 0).mean())

# ---- 与 demo --selftest 打印值逐一核对 ----
assert int(sig_ok.sum()) == 1257 and int(sig_rev.sum()) == 1257
assert int(up_ok.sum()) == 343 and int(up_rev.sum()) == 322
assert round(sign_ok, 3) == 1.000 and round(sign_rev, 3) == 0.000
assert round(up_rev_true, 3) == 0.000
print(f"checked vs demo: sig {int(sig_ok.sum())}/{int(sig_rev.sum())} · "
      f"up-list {int(up_ok.sum())}/{int(up_rev.sum())} · sign "
      f"{sign_ok:.0%}/{sign_rev:.0%}")

s = SVG()

# ---- 上：显著基因数两通路相同 ----
s.text(400, 60, "显著基因完全相同", 30, GRAY, "middle")
s.rect(150, 84, 200, 84, WHITE, BLUE, 5, rx=12)
s.text(250, 122, "正确参照", 30, GREEN, "middle", "bold")
s.text(250, 156, "1257 个基因", 32, INK, "middle", "bold")
s.rect(450, 84, 200, 84, WHITE, RED, 5, rx=12)
s.text(550, 122, "设反参照", 30, INK, "middle", "bold")
s.text(550, 156, "1257 个基因", 32, INK, "middle", "bold")
s.text(400, 210, "p 值逐位相同 · 最大差 5.8e-15", 30, GRAY,
       "middle")
s.text(400, 262, "显著检验完全相同", 32, BLUE, "middle", "bold")
s.text(400, 312, "效应量正负颠倒", 30, INK, "middle", "bold")

# ---- 左下：上调清单对比 ----
s.text(170, 306, "「N 上调」基因", 30, GRAY, "middle")
base = 600
for gx, v, col in ((110, 343, GREEN), (300, 322, RED)):
    h = v * 0.72
    s.rect(gx, base - h, 90, h, col, None)
    s.text(gx + 45, base - h - 16, str(v), 36, INK, "middle", "bold")
s.line(80, base, 430, base, BLUE, 4)
s.text(155, 640, "正确", 30, GRAY, "middle")
s.text(345, 640, "设反", 30, GRAY, "middle")

# ---- 右：机制注释 ----
s.rect(480, 340, 290, 250, WHITE, PURPLE, 5, rx=14)
s.text(625, 384, "mcols(res)$", 30, PURPLE, "middle", "bold")
s.text(625, 424, "description[2]", 30, PURPLE, "middle", "bold")
s.text(625, 470, "N vs K  ↔  K vs N", 30, INK, "middle", "bold")
s.text(625, 516, "符号静默反号", 30, GRAY, "middle")
s.text(625, 556, "富集接着解读", 30, GRAY, "middle")
s.text(625, 596, "机理全反", 30, GRAY, "middle")

# ---- 中文结论 ----
s.text(250, 686, "上调清单全是下调", 30, INK, "middle", "bold")
s.text(560, 686, "机理解释全反", 30, INK, "middle", "bold")

s.save("31_failure3_reversed_reflevel.svg")

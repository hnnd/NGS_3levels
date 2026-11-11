#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-30 失效二 样本对齐错配三档后果（data-plot）。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-30；配色：spec.md §2。
数字复现：textbook/demos/ch14_sample_mismatch.py Part 1（import 复算 + 断言）。"""
import sys
from pathlib import Path

import numpy as np

from svghelp import *

DEMO_DIR = Path(__file__).resolve().parents[3] / "textbook" / "demos"
sys.path.insert(0, str(DEMO_DIR))
import ch14_sample_mismatch as demo   # noqa: E402

# ---- 与 demo main() 完全一致的生成逻辑（同 seed、同调用顺序）----
rng = np.random.default_rng(demo.SEED)
n_rep, alpha, n_perm = 6, 0.15, 10
x = np.concatenate([np.zeros(n_rep), np.ones(n_rep)])
ng = 2400
half = ng // 2
beta_true = np.concatenate([np.zeros(half), np.full(ng - half, 1.5)])
beta_true[half + rng.permutation(ng - half)[: (ng - half) // 2]] = -1.5
mu_base = rng.lognormal(mean=np.log(800.0), sigma=1.5, size=ng)
mu = mu_base[:, None] * 2.0 ** (beta_true[:, None] * x[None, :])
y = rng.negative_binomial(1.0 / alpha, (1.0 / alpha) / (1.0 / alpha + mu),
                          mu.shape)
h1 = ~ (beta_true == 0)

b_ok, p_ok = demo.run_all_genes(y, x, alpha)
b_sw, p_sw = demo.run_all_genes(y, 1.0 - x, alpha)
pow_ok = float((p_ok[h1] < 0.05).mean())
pow_sw = float((p_sw[h1] < 0.05).mean())
deg_ok = int(((p_ok < 0.05) & (np.abs(b_ok) > 1)).sum())
deg_sw = int(((p_sw < 0.05) & (np.abs(b_sw) > 1)).sum())
sign_ok = float((np.sign(b_ok[(p_ok < 0.05) & (np.abs(b_ok) > 1)])
                 == np.sign(beta_true[(p_ok < 0.05) & (np.abs(b_ok) > 1)])).mean())
sign_sw = float((np.sign(b_sw[(p_sw < 0.05) & (np.abs(b_sw) > 1)])
                 == np.sign(beta_true[(p_sw < 0.05) & (np.abs(b_sw) > 1)])).mean())
pow_bad = np.empty(n_perm)
deg_bad = np.empty(n_perm)
for k in range(n_perm):
    x_bad = x[rng.permutation(2 * n_rep)]
    b_k, p_k = demo.run_all_genes(y, x_bad, alpha)
    pow_bad[k] = (p_k[h1] < 0.05).mean()
    deg_bad[k] = ((p_k < 0.05) & (np.abs(b_k) > 1)).sum()

# ---- 与 demo --selftest 打印值逐一核对 ----
assert round(pow_ok, 3) == 0.990 and round(pow_sw, 3) == 0.990
assert round(float(pow_bad.mean()), 3) == 0.308
assert deg_ok == 665 and deg_sw == 665
assert round(float(deg_bad.mean()), 1) == 67.7
assert round(sign_ok, 3) == 1.000 and round(sign_sw, 3) == 0.000
print(f"checked vs demo: power {pow_ok:.3f}/{pow_sw:.3f}/"
      f"{pow_bad.mean():.3f} · DEG {deg_ok}/{deg_sw}/{deg_bad.mean():.1f} · "
      f"sign {sign_ok:.0%}/{sign_sw:.0%}")

s = SVG()

# ---- 三档柱状对比 ----
s.text(400, 52, "正确 ／ 对调 ／ 随机重贴（10 次均值）", 30,
       GRAY, "middle")
base = 470
scen = [("正确", GREEN), ("对调", RED), ("随机", RED)]
# 检出率（对调 / 随机 = 失效，红色）
for i, (lab, col) in enumerate(scen):
    gx = 80 + i * 130
    v = (pow_ok, pow_sw, float(pow_bad.mean()))[i]
    h = v * 340
    s.rect(gx, base - h, 70, h, col, None)
    s.text(gx + 35, base - h - 14, f"{v:.3f}", 32, INK, "middle", "bold")
    s.text(gx + 35, base + 38, lab, 30, GRAY, "middle")
# 差异基因数（失效两档用橙色区分量级）
deg_cols = [GREEN, ORANGE, ORANGE]
for i, lab in enumerate(("正确", "对调", "随机")):
    gx = 560 + i * 76
    v = (deg_ok, deg_sw, float(deg_bad.mean()))[i]
    h = v * 0.52
    s.rect(gx, base - h, 48, h, deg_cols[i], None)
    s.text(gx + 24, base - h - 14, f"{v:.0f}" if i < 2 else f"{v:.1f}", 30,
           INK, "middle", "bold")
s.text(620, base + 38, "差异基因数", 30, GRAY, "middle")
s.line(60, base, 800 - 60, base, BLUE, 4)

# 方向正确率标注
s.text(135, 548, "方向正确 100%", 30, GREEN, "middle", "bold")
s.text(292, 548, "方向正确 0%", 30, INK, "middle", "bold")

# 中文结论
s.text(150, 600, "对调事故方向全反", 30, INK, "middle", "bold")
s.text(420, 600, "随机重贴功效暴跌", 30, INK, "middle", "bold")
s.text(655, 600, "流程静默不报错", 30, INK, "middle", "bold")
s.text(400, 656, "rc = 0 · 全程无警告", 30, GRAY, "middle")
s.text(400, 700 - 12, "灾难全在下游", 30, INK, "middle", "bold")

s.save("30_failure2_sample_mismatch.svg")

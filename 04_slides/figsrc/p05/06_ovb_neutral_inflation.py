#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_ovb_neutral_inflation.py — 生成 06_ovb_neutral_inflation.svg
（FIG-P05-06：P20「结构如何把中性标记变成显著」，cols 左栏）【data-plot】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-06（800×700，中文共 28 字）。
数据入口：`textbook/demos/ch21_structure_confounding_ols.py`，参数 n=400、
m=20000、Δ=2.0、σ_δ=0.15、种子 20261104（与 demos 默认完全一致）。
  - 朴素 OLS（不加协变量）：中性 SNP 假阳性率 0.573（名义 0.05）、
    λ_GC = 12.149；
  - OLS + 亚群指示协变量（GLM+Q 两群退化形态）：假阳性率 0.051、
    λ_GC = 1.005；
  - OVB 恒等式：β̂_j 对 δ_j/(p_j(1−p_j)) 回归，观测斜率 0.4791，
    理论值 Δ·w_A·w_B = 2.00×0.5×0.5 = 0.5000。
集计数直接用 demo.simulate() 的返回值；散点需要逐 SNP 的 β̂ 与 g，故用一个
「与 demo.simulate() 同序同参」的复算函数重放同一随机流，并在脚本里逐项
断言它与 demo.simulate() 的输出完全一致（斜率、两条假阳性率、两个 λ），
保证图上的点就是 demos 输出的那批点。
图内中文严格取方案给定两句（16 + 12 = 28 字）；数字、λ、g、β̂ 为符号。
配色：红＝朴素 OLS 假阳性过半膨胀，绿＝加协变量后受控，深蓝虚线＝理论回归线。
依赖：numpy + scipy（同 demos）；无网络；种子固定。
用法：PYTHONDONTWRITEBYTECODE=1 python3 06_ovb_neutral_inflation.py
"""
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch21_structure_confounding_ols as demo              # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["朴素回归中性假阳性过半膨胀超十二",   # 16
           "加协变量回归正常名义水平"]            # 12
TEXT = "".join(PHRASES)

N, M, DELTA, SIGMA_D, SEED = 400, 20000, 2.0, 0.15, 20261104


def simulate_detail(n, m, delta, sigma_d, seed):
    """与 demos.simulate() 逐行同序的重放，额外返回逐 SNP 的 β̂ 与 g。"""
    rng = np.random.default_rng(seed)
    n_a = n // 2
    w_a, w_b = n_a / n, (n - n_a) / n
    is_a = np.zeros(n)
    is_a[:n_a] = 1.0
    y = delta * is_a + rng.standard_normal(n)
    y_c = y - y.mean()
    d_j = rng.normal(0.0, sigma_d, m)
    p_b = rng.uniform(0.15, 0.85, m)
    p_a = np.clip(p_b + d_j, 0.02, 0.98)
    d_j = p_a - p_b
    p = w_a * p_a + w_b * p_b
    x = np.empty((m, n), dtype=np.float64)
    for lo, hi, pj in ((0, n_a, p_a), (n_a, n, p_b)):
        x[:, lo:hi] = rng.binomial(2, pj[:, None], size=(m, hi - lo))
    x_c = x - x.mean(axis=1, keepdims=True)
    sxx = (x_c * x_c).sum(axis=1)
    sxy = x_c @ y_c
    beta = sxy / sxx
    g = d_j / (p * (1.0 - p))
    return beta, g


def check_data():
    r = demo.simulate(N, M, DELTA, SIGMA_D, SEED)
    beta, g = simulate_detail(N, M, DELTA, SIGMA_D, SEED)
    slope_fit = float(np.polyfit(g, beta, 1)[0])
    assert abs(r["slope"] - 0.4791) < 1e-4, r["slope"]
    assert abs(slope_fit - r["slope"]) < 1e-9, (slope_fit, r["slope"])
    assert abs(r["fpr_ols"] - 0.573) < 5e-3 and abs(r["fpr_q"] - 0.051) < 5e-3
    assert abs(r["lam_ols"] - 12.149) < 5e-3 and abs(r["lam_q"] - 1.005) < 5e-3
    print(f"check: fpr_ols={r['fpr_ols']:.4f}, fpr_q={r['fpr_q']:.4f}, "
          f"lam_ols={r['lam_ols']:.3f}, lam_q={r['lam_q']:.3f}, "
          f"slope={r['slope']:.4f}（theory {DELTA * 0.5 * 0.5:.4f}）")
    return r, beta, g


def main():
    r, beta, g = check_data()
    s = SVG(800, 700, "Structural confounding inflates neutral markers",
            plan=TEXT)

    # ---------- 上半：两条假阳性率 ----------
    BX, BW = 168.0, 330.0
    s.text(52, 152, "OLS", 30, INK, "start", "bold")
    s.rect(BX, 118, BW, 46, RED_TINT, RED, 4, rx=8)
    s.text(BX + BW + 14, 152, f"{100 * r['fpr_ols']:.1f}%", 32, RED,
           "start", "bold")
    s.text(BX + BW + 134, 152, f"λ={r['lam_ols']:.3f}", 30, RED)

    s.text(52, 222, "OLS+Q", 30, INK, "start", "bold")
    s.rect(BX, 188, BW * r["fpr_q"] / r["fpr_ols"], 46, GREEN_TINT, GREEN,
           4, rx=8)
    s.text(BX + 44, 222, f"{100 * r['fpr_q']:.1f}%", 32, GREEN, "start",
           "bold")
    s.text(BX + 184, 222, f"λ={r['lam_q']:.3f}", 30, GREEN)

    s.text(400, 348, PHRASES[0], 32, RED, "middle", "bold")
    s.text(400, 396, PHRASES[1], 32, GREEN, "middle", "bold")

    # ---------- 下半：OVB 散点与两条回归线 ----------
    xl, xr, yb, yt = 130.0, 660.0, 640.0, 440.0
    gx, gy, bmax = 2.2, 1.2, 1.2

    def px(v):
        return xl + (v + gx) / (2 * gx) * (xr - xl)

    def py(v):
        return yb - (v + bmax) / (2 * bmax) * (yb - yt)

    s.rect(xl, yt, xr - xl, yb - yt, WHITE, PANEL, 3)
    s.line(xl, py(0), xr, py(0), PANEL, 4)
    s.line(px(0), yt, px(0), yb, PANEL, 4)
    s.line(xl - 10, yb, xr + 10, yb, INK, 4)
    s.line(xl, yb, xl, yt - 10, INK, 4)
    s.text(px(-gx) - 6, yt - 12, "β", 30, INK, "end", "bold")
    s.text(xr + 6, yb + 30, "g", 30, INK, "start", "bold")
    for v in (-2, 2):
        s.text(px(v), yb + 30, str(v), 30, GRAY, "middle")
    for v in (-1, 1):
        s.text(xl - 10, py(v) + 10, str(v), 30, GRAY, "end")

    idx = np.arange(0, M, 40)                 # 500 个代表点（全量点会撑爆 SVG）
    for i in idx:
        cx_, cy_ = px(float(g[i])), py(float(beta[i]))
        if 134 <= cx_ <= 360 and 439 <= cy_ <= 547:
            continue                          # 图例白底覆盖区不画点，免歧义
        s.circle(cx_, cy_, 3.0, BLUE, None, 0)

    for slope, col, dash in ((0.5, BLUE, "14 9"), (r["slope"], PURPLE, None)):
        s.line(px(-gx), py(-gx * slope), px(gx), py(gx * slope), col, 5,
               dash=dash)

    # 图例（白底压在散点上，保证可读）
    s.rect(140, 445, 220, 96, WHITE, PANEL, 3, rx=10)
    s.line(154, 477, 190, 477, BLUE, 5, dash="14 9")
    s.text(200, 487, "0.5000", 30, BLUE, "start", "bold")
    s.line(154, 515, 190, 515, PURPLE, 5)
    s.text(200, 525, f"{r['slope']:.4f}", 30, PURPLE, "start", "bold")

    s.save("06_ovb_neutral_inflation.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())

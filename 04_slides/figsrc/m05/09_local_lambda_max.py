#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_local_lambda_max.py — FIG-M05-09 局部多尺度最大值（data-plot）

方案：`reviews/course/M05_FIGP_001.md` §4.1 FIG-M05-09（P25，`.cols` 800×700，data-plot）。
数据入口：`textbook/demos/ch15_local_lambda.py` Part 1 合成算例——
100,000 个 200 bp 窗口、背景 10.0 reads/窗口，窗口 20000..24999 为 2.0× 共享开放结构域
（处理与对照共享该偏差、无真实 peak）；λBG-only 口径域内假阳性 255 个窗口，
取 max(λBG, λ1k, λ10k) 后降为 0。本脚本用 demo 同种子复算并断言。
尺度只用 MACS2 实现里的 1k 与 10k 两个局部尺度（ALN W3：不出现 5k 或 d）。
图内汉字 24 字，逐字取方案原句：多尺度局部背景 7 / 取最大值抬高致密区门槛 11 /
假峰清除归零 6；「个」是数量单位，不构成新提法。
红为唯一警示色：左面板过线标记（1 处）+ 左面板数字 255（1 处）＝ 2 处。
无网络；随机数仅经 demo 同种子复算。
泊松尾概率在本脚本内用 numpy + math.lgamma 向量化自算（不 import scipy），
与 demo 里 scipy 的 `stats.poisson.sf` 同义；两种实现逐个窗口比对，读段数 k>0 的窗口
最大绝对差 5.8×10^-15，域内（k ≥ 6）过线窗口判定完全一致（同样 255 → 0）。
k=0 的 7 个窗口两种实现有分歧（本脚本 8.1×10^-13，scipy 恰为 1.0），但它们全在域外、
且任何 λ 下都远低于 1e-5 阈值，不影响本图两个计数。这样本脚本只依赖标准库 + numpy。
比对记录见 `textbook/tasks/logs/M05_FIGS_poisson_check.py` 与其 `.log`。
用法：PYTHONDONTWRITEBYTECODE=1 python3 09_local_lambda_max.py
"""
import sys
from math import lgamma
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]              # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from ch15_local_lambda import sliding_mean               # noqa: E402

from svghelp import *                                    # noqa: F401,F403,E402

N_W, LAM0, P_CUT = 100000, 10.0, 1e-5
rng = np.random.default_rng(20260829)
domain = np.zeros(N_W, dtype=bool)
D0 = N_W // 5
domain[D0:D0 + 5000] = True
LAM_DOM = LAM0 * 2.0
treat = np.where(domain, rng.poisson(LAM_DOM, N_W), rng.poisson(LAM0, N_W))
ctrl = np.where(domain, rng.poisson(LAM_DOM, N_W), rng.poisson(LAM0, N_W))
lam_bg = treat.sum() / N_W
lam_1k = sliding_mean(ctrl, 2)
lam_10k = sliding_mean(ctrl, 25)
lam_max = np.maximum(np.maximum(np.full(N_W, lam_bg), lam_1k), lam_10k)


def poisson_sf(k, lam):
    """P(X ≥ k | λ)，向量化实现（只用 numpy + math.lgamma，不依赖 scipy）。

    与 demo 里 scipy 的 `stats.poisson.sf(k − 1, λ)` 同义：先按 λ 逐窗铺开
    log P(X = j)，再累加成 CDF 取补。P(X = j) 在对数域里算，避免 λ^j 直接溢出。
    """
    kmax = int(k.max())
    j = np.arange(kmax + 1)
    log_fac = np.array([lgamma(int(x) + 1) for x in j])
    log_pmf = j[None, :] * np.log(lam)[:, None] - lam[:, None] - log_fac[None, :]
    cdf = np.cumsum(np.exp(log_pmf), axis=1)
    sf = 1.0 - cdf[np.arange(len(k)), k - 1]
    return np.maximum(sf, 0.0)


fp_bg = int(((poisson_sf(treat, np.full(N_W, lam_bg)) < P_CUT) & domain).sum())
fp_max = int(((poisson_sf(treat, lam_max) < P_CUT) & domain).sum())
assert fp_bg == 255 and fp_max == 0, (fp_bg, fp_max)

s = SVG()

s.text(400, 58, "多尺度局部背景", 36, BLUE, "middle", "bold")

PANEL_W, PANEL_Y, PANEL_H = 336, 122, 336
PX = (48, 416)
BASE = PANEL_Y + PANEL_H - 62              # 信号基线
BLOCK_H = 128                              # 2.0× 共享偏差域的读段高度
BLOCK_X, BLOCK_W = 104, 116                # 面板内偏移


def panel(px, name, lines, n_pass, pass_color):
    """lines = [(门槛高度, 颜色, 标签, 虚线)]；n_pass = 域内过线窗口标记数。"""
    s.panel(px, PANEL_Y, PANEL_W, PANEL_H, caption=None)
    s.text(px + PANEL_W / 2, PANEL_Y + 46, name, 30, BLUE, "middle", "bold")

    bx = px + BLOCK_X
    s.rect(bx, BASE - BLOCK_H, BLOCK_W, BLOCK_H, CYAN, rx=6)     # 开放结构域
    for i in range(6):                                          # 两侧背景读数
        for x0 in (px + 26, px + 244):
            s.line(x0 + i * 14, BASE, x0 + i * 14, BASE - 38, CYAN, 7)

    for h, color, lab, dash in lines:                            # 三条 λ 门槛
        if dash:
            s.line(px + 22, BASE - h, px + PANEL_W - 22, BASE - h,
                   color, 4, dash="12 9")
        else:
            s.line(px + 22, BASE - h, px + PANEL_W - 22, BASE - h, color, 6)
        s.text(px + PANEL_W - 24, BASE - h - 12, lab, 30, color, "end", "bold")

    if n_pass:                                                   # 域内过线（红 1 处）
        step = (BLOCK_W - 34) / max(n_pass - 1, 1)
        d = " ".join(f"M {bx + 17 + i * step:.1f} {BASE - BLOCK_H + 8} "
                     f"L {bx + 17 + i * step:.1f} {BASE - BLOCK_H + 36}"
                     for i in range(n_pass))
        s.path(d, RED, 7)

    s.text(px + PANEL_W / 2, PANEL_Y + PANEL_H + 52,
           f"{n_pass} 个", 34, pass_color, "middle", "bold")


panel(PX[0], "λBG", [(58, PURPLE, "λBG", True)], fp_bg, RED)
panel(PX[1], "max", [(58, PURPLE, "λBG", True),
                     (112, CYAN_DEEP, "λ1k", True),
                     (172, BLUE, "λ10k", False)], fp_max, GREEN)

s.text(400, 578, "取最大值抬高致密区门槛", 32, INK, "middle", "bold")
s.text(400, 636, "假峰清除归零", 32, GREEN, "middle", "bold")

s.save("09_local_lambda_max.svg")
print(f"check: 域内假阳性 λBG-only={fp_bg}，max 局部 λ={fp_max}")

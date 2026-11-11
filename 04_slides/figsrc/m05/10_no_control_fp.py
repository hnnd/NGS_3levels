#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_no_control_fp.py — FIG-M05-10 有对照与无对照对比（data-plot）

方案：`reviews/course/M05_FIGP_001.md` §4.1 FIG-M05-10（P26，`.cols` 800×700，data-plot）。
数据入口：`textbook/demos/ch15_local_lambda.py` Part 2 合成算例——
A 有对照（λ1k/λ10k 取对照）：假阳性 2、宽域召回 0.871、伪 FRiP 0.0665；
B 无对照（MACS2 实际自估 λ10k）：假阳性 218、召回 0.003、伪 FRiP 0.0160；
C 无对照 + --nolambda（仅 λBG）：假阳性 288、召回 0.897、伪 FRiP 0.0789。
本脚本 import `run_pipeline` 同种子复算并断言，不写死数字；召回与 FRiP 只写进
脚本输出与回执核对表，不上图面（图面只承担方案要求的假阳性对比）。
图内汉字 27 字，逐字取方案原句：缺对照后果 5 / 假阳性窗口 5 /
宽偏差域假阳性激增 9 / 加入对照彻底过滤 8。
红只用于两条无对照管线（各 1 处，共 2 处，符合唯一警示色上限）。
无网络；随机数仅经 demo 同种子复算。
用法：PYTHONDONTWRITEBYTECODE=1 python3 10_no_control_fp.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]              # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from ch15_local_lambda import run_pipeline               # noqa: E402

from svghelp import *                                    # noqa: F401,F403,E402

N_W, LAM0, P_CUT = 100000, 10.0, 1e-5
rng = np.random.default_rng(20260829)

# Part 1 的随机数消耗必须复现，Part 2 的数字才与 demos 一致
domain = np.zeros(N_W, dtype=bool)
D0 = N_W // 5
domain[D0:D0 + 5000] = True
LAM_DOM = LAM0 * 2.0
treat1 = np.where(domain, rng.poisson(LAM_DOM, N_W), rng.poisson(LAM0, N_W))
ctrl1 = np.where(domain, rng.poisson(LAM_DOM, N_W), rng.poisson(LAM0, N_W))
_ = (treat1, ctrl1)

treat = rng.poisson(LAM0, N_W).astype(float)
ctrl = rng.poisson(LAM0, N_W).astype(float)
for sp in rng.choice(N_W - 10, size=30, replace=False):
    treat[int(sp):int(sp) + 10] = rng.poisson(LAM0 * 4.0, 10)
    ctrl[int(sp):int(sp) + 10] = rng.poisson(LAM0 * 4.0, 10)
G0 = N_W // 2
broad = np.zeros(N_W, dtype=bool)
broad[G0:G0 + 2000] = True
treat[G0:G0 + 2000] = rng.poisson(LAM0 * 3.5, 2000)
true_peaks = np.zeros(N_W, dtype=bool)
for p_ in rng.choice(N_W, size=150, replace=False):
    true_peaks[int(p_)] = True
    treat[int(p_)] += int(LAM0 + 30)
outside = ~(broad | true_peaks)

rows = []
for mode in ("control", "self", "nolambda"):
    sig, _ = run_pipeline(treat, ctrl, mode, P_CUT, N_W)
    interior = broad.copy()
    interior[G0:G0 + 100] = False
    interior[G0 + 1900:G0 + 2000] = False
    rows.append((int((sig & outside).sum()),
                 float((sig & interior).sum() / interior.sum()),
                 float(treat[sig].sum() / treat.sum())))

FP = [r[0] for r in rows]
assert FP == [2, 218, 288], FP
assert abs(rows[0][1] - 0.871) < 5e-4 and abs(rows[1][1] - 0.003) < 5e-4
assert abs(rows[0][2] - 0.0665) < 5e-5 and abs(rows[1][2] - 0.0160) < 5e-5

s = SVG()

s.text(400, 58, "缺对照后果", 36, BLUE, "middle", "bold")

L, R, B, T = 108, 704, 470, 190
BW, GAP = 122, 52
SY = (B - T) / max(FP)
PIPES = [("input", GREEN), ("self", RED), ("λBG", RED)]

s.line(L, B, R, B, INK, 4)
s.line(L, B, L, T - 12, INK, 4)
s.text(L, T - 46, "假阳性窗口", 30, GRAY, "start")

for i, (lab, color) in enumerate(PIPES):
    x = L + 34 + i * (BW + GAP)
    h = max(FP[i] * SY, 10)                     # A 只有 2 个：保留最小可视高度
    s.rect(x, B - h, BW, h, color, rx=6)
    s.text(x + BW / 2, B - h - 18, str(FP[i]), 34, INK, "middle", "bold")
    s.text(x + BW / 2, B + 48, lab, 32, INK, "middle", "bold")

s.text(400, 580, "宽偏差域假阳性激增", 32, INK, "middle", "bold")
s.text(400, 638, "加入对照彻底过滤", 32, GREEN, "middle", "bold")

s.save("10_no_control_fp.svg")
print(f"check: FP A/B/C = {FP}；召回 {rows[0][1]:.3f}/{rows[1][1]:.3f}/"
      f"{rows[2][1]:.3f}；伪 FRiP {rows[0][2]:.4f}/{rows[1][2]:.4f}/{rows[2][2]:.4f}")

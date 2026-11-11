#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_xcorr_vs_bampe.py — FIG-M05-11 互相关与双端定界（data-plot）

方案：`reviews/course/M05_FIGP_001.md` §4.1 FIG-M05-11（P28，`.cols` 800×700，data-plot）。
数据入口：`textbook/demos/ch15_atac_fragment_model.py` Part 2 合成算例——
ChIP-SE 互相关峰在滞后 208 bp（≈ 片段长 220 bp）；ATAC-SE 互相关峰在 9 bp（Tn5 交错切口），
50–500 bp 区间最大值/全局峰 = 0.049（MACS2 报 Fewer paired peaks → 必须 --nomodel）。
本脚本按 demo 的随机数消耗顺序同种子复算两条互相关曲线；峰位与比值在**原始曲线**上
断言，图上曲线只做 5 滞后滑动平均以利观感（不改变峰位），峰位圆点落在同一条平滑曲线上。

下方面板的纵轴只按「50–500 bp 建模区间内的最大值」定标：9 bp 处的尖峰远高于该量级，
故以一条超出量程的竖线 + 三角标记表示「峰在区间外」，这样才看得出建模窗口里是一片平坦。
图内汉字 28 字：方案原句 22 字（单端互相关平移估片段 10 / 双端直接物理定界无需建模 12）
＋「建模区间」4 ＋「滞后」2（坐标轴名）。
红不上图：本图无警示语义，只用青蓝（ChIP）与橙（ATAC）两色。
无网络；随机数仅经 demo 同种子复算。
用法：PYTHONDONTWRITEBYTECODE=1 python3 11_xcorr_vs_bampe.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]              # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from ch15_atac_fragment_model import (                   # noqa: E402
    SEED, atac_ladder_lognorm_mix, xcorr_peak,
)

from svghelp import *                                    # noqa: F401,F403,E402

N_SITES, REGION, MAX_LAG = 1500, 60000, 500
rng = np.random.default_rng(SEED)
atac_ladder_lognorm_mix(rng, N_SITES)                    # 与 demo 同序消耗随机数
_ = np.clip(np.round(rng.normal(130, 20, N_SITES)), 20, 1000).astype(int)

centers = np.sort(rng.choice(REGION - 1000, size=N_SITES, replace=False) + 500)
plus_chip, minus_chip = np.zeros(REGION), np.zeros(REGION)
plus_atac, minus_atac = np.zeros(REGION), np.zeros(REGION)
plus_chip += rng.poisson(0.005, REGION)
minus_chip += rng.poisson(0.005, REGION)
plus_atac += rng.poisson(0.005, REGION)
minus_atac += rng.poisson(0.005, REGION)
for c in centers:
    d = int(rng.normal(220, 25))
    plus_chip[c - d // 2] += 1
    minus_chip[c + d // 2] += 1
    p = int(c + rng.normal(0, 2))
    plus_atac[p] += 1
    minus_atac[p + 9] += 1

LAG_C, VAL_C, VALS_C = xcorr_peak(plus_chip, minus_chip, MAX_LAG)
LAG_A, VAL_A, VALS_A = xcorr_peak(plus_atac, minus_atac, MAX_LAG)
BAND = float(VALS_A[50:501].max() / VAL_A)
assert LAG_C == 208 and LAG_A == 9, (LAG_C, LAG_A)
assert abs(BAND - 0.049) < 5e-4, BAND


def smooth(vals, k=5):
    """5 滞后滑动平均（仅观感；峰位断言在原始曲线上完成）。"""
    pad = np.concatenate([vals[:k], vals, vals[-k:]])
    return np.convolve(pad, np.ones(k) / k, mode="same")[k:-k]


s = SVG()

s.text(400, 58, "单端互相关平移估片段", 34, BLUE, "middle", "bold")
s.text(400, 104, "双端直接物理定界无需建模", 30, INK, "middle")

X0, X1 = 112, 704


def bx(lag):
    return X0 + (X1 - X0) * lag / MAX_LAG


# ---------------- 上：ChIP-SE 互相关，峰在 208 bp（片段长度） ----------------
YC_T, YC_B = 190, 372
YC_SPAN = YC_B - YC_T
SMOOTH_C = smooth(VALS_C)
YC_LIM = SMOOTH_C[LAG_C] * 1.06
s.line(X0, YC_B, X1, YC_B, INK, 4)
s.line(X0, YC_B, X0, YC_T, INK, 4)
s.curve([(bx(i), YC_B - YC_SPAN * min(SMOOTH_C[i], YC_LIM) / YC_LIM)
         for i in range(len(SMOOTH_C))], CYAN_DEEP, 5)
py = YC_B - YC_SPAN * SMOOTH_C[LAG_C] / YC_LIM
s.circle(bx(LAG_C), py, 10, CYAN_DEEP)
s.text(bx(LAG_C) + 18, py - 24, "208 bp", 30, CYAN_DEEP, "start", "bold")

# ---------------- 下：ATAC-SE 互相关，峰在 9 bp，建模区间内平坦 ----------------
YA_T, YA_B = 430, 620
YA_SPAN = YA_B - YA_T
SMOOTH_A = smooth(VALS_A)
BAND_MAX = SMOOTH_A[50:501].max()
YA_LIM = BAND_MAX * 1.5                        # 只按建模区间内的最大值定标
s.line(X0, YA_B, X1, YA_B, INK, 4)
s.line(X0, YA_B, X0, YA_T, INK, 4)
s.curve([(bx(i), YA_B - YA_SPAN * min(SMOOTH_A[i], YA_LIM) / YA_LIM)
         for i in range(50, MAX_LAG + 1)], ORANGE, 5)
# 9 bp 峰：远超量程，用超出量程的竖线 + 三角标记表示
s.line(bx(LAG_A) + 3, YA_B, bx(LAG_A) + 3, YA_T + 26, ORANGE, 5)
s.polygon([(bx(LAG_A) + 3, YA_T + 8), (bx(LAG_A) - 9, YA_T + 30),
           (bx(LAG_A) + 15, YA_T + 30)], ORANGE)
s.text(bx(LAG_A) + 42, YA_T - 6, "9 bp", 30, ORANGE, "start", "bold")

# 建模区间 50–500 bp（MACS2 找成对正负峰的扫描窗）
BAND_L, BAND_R = bx(50), bx(MAX_LAG)
s.line(BAND_L, YA_B, BAND_L, YA_T + 16, PURPLE, 4, dash="10 8")
s.line(BAND_R, YA_B, BAND_R, YA_T + 16, PURPLE, 4, dash="10 8")
s.text((BAND_L + BAND_R) / 2, YA_T + 52, "建模区间", 30, PURPLE, "middle", "bold")
s.text(X1, YA_B + 46, "滞后", 30, GRAY, "end")

# 双端定界：BAMPE 由片段两端直接闭合，不需要任何模型平移
s.arrow(BAND_L + 96, 664, BAND_L + 226, 664, GREEN, 5, head=14)
s.text(BAND_L + 242, 676, "BAMPE", 30, GREEN, "start", "bold")

s.save("11_xcorr_vs_bampe.svg")
print(f"check: ChIP 峰 {LAG_C} bp；ATAC 峰 {LAG_A} bp；"
      f"50–500 bp 区间最大值/全局峰 = {BAND:.3f}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""21_permutation_null.py — FIG-M05-21 置换检验经验零分布（new-svg + 现算零分布）

方案：`reviews/course/M05_FIGP_001.md` §4.2 FIG-M05-21（P41，`.cols` 800×700，new-svg）。
教材依据：§15.4.7 L309–L319：固定「差异峰关联基因」集合大小 n_draw，从可检测基因全集
（padj 非 NA 的行）里随机抽同样多个基因，与差异基因集求交，重复 n_perm 次得到经验零分布；
经验 p 值 = (1 + 零分布中不小于观察值的次数) / (n_perm + 1)。

数字入口：教材 §15.4.7 与习题给的是设例参数——可检测基因全集 N = 12 400、
差异基因 m = 1 843、每次抽取 n_draw = 512、观察交集 137、n_perm = 1000
（`05_peak_annotation.R` 用 `set.seed(20260829)` + `nperm = 1000`，同一零模型）。
本脚本用 numpy 在同一设定、同一种子下现算 1000 次不放回抽取的交集分布，画的就是这份
现算结果，并断言与教材口径相符（期望 512×1843/12400 = 76.10、
sd = sqrt(n·m·(N−m)·(N−n)/(N²(N−1))) = 7.88）。
图上不标模拟中位数等派生数字，避免与 R 脚本在真实差异表上得到的零分布混淆。

图内汉字 22 字，逐字取方案原句：标题「标签随机置换千次构建经验零分布」15
＋ 结论「检验交集显著性」7。轴名与公式只用符号（`空集大小`→`k`、`不小于观测的次数`
→ `#(null ≥ 137)`），因为方案给的 22 字预算已用满。
红为唯一警示色：观察值竖线与三角标记合成 1 个 `<g>`（1 处）+ 观察值数字 137（1 处）
= 2 处。
无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 21_permutation_null.py
"""
import math

import numpy as np

from svghelp import *                                    # noqa: F401,F403,E402

N_GENE, M_DEG, N_DRAW = 12400, 1843, 512      # 教材 §15.4.7 设例参数
OBS, N_PERM, SEED = 137, 1000, 20260829

rng = np.random.default_rng(SEED)
null = np.array([rng.hypergeometric(M_DEG, N_GENE - M_DEG, N_DRAW)
                 for _ in range(N_PERM)])
EXP = N_DRAW * M_DEG / N_GENE
SD = math.sqrt(N_DRAW * M_DEG * (N_GENE - M_DEG) * (N_GENE - N_DRAW)
               / (N_GENE ** 2 * (N_GENE - 1)))
assert abs(EXP - 76.10) < 5e-3 and abs(SD - 7.88) < 5e-3
assert null.min() >= 40 and null.max() <= 120 and OBS > null.max()
P_EMP = (1 + int((null >= OBS).sum())) / (N_PERM + 1)

s = SVG()

s.text(400, 62, "标签随机置换千次构建经验零分布", 32, BLUE, "middle", "bold")

# ---------------- 直方图 ----------------
L, R, B, T = 120, 704, 452, 208
LO, HI, BIN = 40, 152, 4


def px(v):
    return L + (R - L) * (v - LO) / (HI - LO)


def py(v_frac):
    return B - (B - T) * v_frac


counts, edges = np.histogram(null, bins=np.arange(LO, HI + BIN, BIN))
YMAX = float(counts.max()) + 12.0

s.line(L, B, R, B, INK, 4)
s.line(L, B, L, T - 4, INK, 4)
s.text(L - 8, T - 44, "k", 30, GRAY, "start")

for i, c in enumerate(counts):
    if c == 0:
        continue
    x0, x1 = px(edges[i]) + 2, px(edges[i + 1]) - 2
    s.rect(x0, py(c / YMAX), x1 - x0, B - py(c / YMAX), CYAN, rx=2)

for v in (40, 60, 80, 100, 120, 140):
    s.line(px(v), B, px(v), B + 9, INK, 3)
    s.text(px(v), B + 42, str(v), 30, GRAY, "middle")

# ---------------- 观察值竖线（红：竖线 + 三角合成 1 处） ----------------
OX = px(OBS)
s.raw(f'<g stroke="{RED}" fill="{RED}">'
      f'<line x1="{OX:.1f}" y1="{B}" x2="{OX:.1f}" y2="{T + 18}" '
      f'stroke-width="6" stroke-dasharray="16 10"/>'
      f'<polygon points="{OX:.1f},{T + 14} {OX - 18:.1f},{T + 46} '
      f'{OX + 18:.1f},{T + 46}"/></g>')
s.text(OX, T - 22, "137", 34, RED, "middle", "bold")

# ---------------- 经验 p 值公式（符号 + 数字，不增汉字） ----------------
s.text(400, 556, "p = (1 + #(null ≥ 137)) / (n + 1)", 32, INK, "middle", "bold")

# ---------------- 结论（方案原句逐字） ----------------
s.text(400, 636, "检验交集显著性", 32, BLUE, "middle", "bold")

s.save("21_permutation_null.svg")
print(f"check: 期望 {EXP:.2f}、sd {SD:.2f}、模拟中位 {np.median(null):.0f}、"
      f"最大 {null.max()}、p 经验 {P_EMP:.4f}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch13_opening_case.py — 第 13 章开篇设例：只有批次、没有处理效应，PCA 与差异表照样"好看"（合成算例）

服务章节：第 13 章 §13.1「这一章要回答的问题」开篇的两份结果（图 13-1 PCA、表 13-1 差异表前十），
          §13.5.2 失效条件 2（完全混杂）回指。
数据性质：【合成算例】全部为伪随机数，真值在生成时写定——
  * 6 个样本：对照 C1–C3 于 1 月建库送测，处理 T1–T3 于 3 月建库送测（处理组 == 送测批次，完全混杂）；
  * 2,000 个基因，计数为负二项（Gamma–Poisson）抽样，文库大小相同；
  * 只写入一个与送测日期同步的批次偏移：随机选 150 个基因在 3 月批次上调 3 倍（log2 ≈ +1.58）；
    这 150 个里有 60 个被标注为"叶绿素合成"（合成注释，基因组中该注释共 80 个基因，占 4%）；
  * 处理效应为零：处理组与对照组之间不存在任何生物学差异。
差异检验用 log2 CPM 上的 Welch t 检验 + BH 校正（教学简化，不是 DESeq2；目的只是给出"一张看起来正常的表"）。

用法：
  python3 textbook/demos/ch13_opening_case.py              # 打印 PCA 方差占比与差异表前十
  python3 textbook/demos/ch13_opening_case.py --svg OUT    # 另存 PCA 图（SVG）
  python3 textbook/demos/ch13_opening_case.py --selftest   # 断言正文引用的数字
作者：总编（D138）  日期：2026-11-10
"""
from __future__ import annotations

import argparse
import logging
import os
import random
import sys

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)
SEED = 20261110
N_GENE, N_OFFSET, N_CHL_IN_OFFSET, N_CHL_TOTAL = 2000, 150, 60, 80
SAMPLES = ["C1", "C2", "C3", "T1", "T2", "T3"]
MARCH = np.array([0, 0, 0, 1, 1, 1], dtype=bool)  # 送测批次 == 处理组


def simulate() -> dict:
    """Generate counts with a batch-only offset; return counts, annotations and ground truth."""
    random.seed(SEED)
    os.environ["PYTHONHASHSEED"] = str(SEED)
    rng = np.random.default_rng(SEED)
    base = np.exp(rng.normal(5.0, 1.2, N_GENE))                       # 基因平均表达
    offset_idx = rng.choice(N_GENE, N_OFFSET, replace=False)          # 随送测日期抬高的基因
    chl = np.zeros(N_GENE, dtype=bool)
    chl[offset_idx[:N_CHL_IN_OFFSET]] = True
    others = np.setdiff1d(np.arange(N_GENE), offset_idx)
    chl[rng.choice(others, N_CHL_TOTAL - N_CHL_IN_OFFSET, replace=False)] = True
    mu = np.tile(base[:, None], (1, len(SAMPLES)))
    mu[np.ix_(offset_idx, np.where(MARCH)[0])] *= 3.0                  # 唯一写入的效应：批次
    disp = 0.01                                                        # 生物学离散度
    lam = rng.gamma(1 / disp, mu * disp)
    counts = rng.poisson(lam)
    return {"counts": counts, "chl": chl, "offset": np.isin(np.arange(N_GENE), offset_idx)}


def analyse(sim: dict) -> dict:
    """PCA on log2 CPM (top-500 variable genes) and Welch t-test + BH."""
    c = sim["counts"]
    logcpm = np.log2(c / c.sum(0) * 1e6 + 1)
    keep = c.sum(1) >= 10
    top = np.argsort(logcpm.var(1))[::-1][:500]
    x = logcpm[top].T - logcpm[top].T.mean(0)
    u, s, _ = np.linalg.svd(x, full_matrices=False)
    var = s ** 2 / (s ** 2).sum()
    pcs = u * s
    t, p = stats.ttest_ind(logcpm[:, MARCH], logcpm[:, ~MARCH], axis=1, equal_var=False)
    p = np.where(keep, p, np.nan)
    order = np.argsort(np.where(np.isnan(p), 2, p))
    m = int(np.sum(~np.isnan(p)))
    padj = np.full_like(p, np.nan)
    ranked = p[order[:m]] * m / np.arange(1, m + 1)
    padj[order[:m]] = np.minimum.accumulate(ranked[::-1])[::-1].clip(max=1)
    lfc = logcpm[:, MARCH].mean(1) - logcpm[:, ~MARCH].mean(1)
    return {"var": var, "pcs": pcs, "p": p, "padj": padj, "lfc": lfc, "order": order}


def top_table(sim: dict, res: dict, n: int = 10) -> list[tuple]:
    rows = []
    for g in res["order"][:n]:
        rows.append((f"g{g + 1:04d}", res["lfc"][g], res["p"][g], res["padj"][g],
                     "叶绿素合成" if sim["chl"][g] else "—", bool(sim["offset"][g])))
    return rows


def write_svg(res: dict, path: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import warnings
    warnings.filterwarnings("ignore", module="matplotlib")
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Source Han Sans SC", "WenQuanYi Zen Hei", "DejaVu Sans"]
    plt.rcParams["svg.fonttype"] = "none"
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    pcs, var = res["pcs"], res["var"]
    for mask, col, mk, lab in [(~MARCH, "#4DBBD5", "o", "对照组（1 月送测）"), (MARCH, "#E64B35", "^", "处理组（3 月送测）")]:
        ax.scatter(pcs[mask, 0], pcs[mask, 1], s=130, c=col, marker=mk, edgecolors="#3C5488", linewidths=1, label=lab, zorder=3)
    for i, nm in enumerate(SAMPLES):
        ax.annotate(nm, (pcs[i, 0], pcs[i, 1]), xytext=(8, 6), textcoords="offset points", fontsize=11, color="#3C5488")
    ax.set_xlabel(f"PC1（{var[0] * 100:.1f}%）", fontsize=12)
    ax.set_ylabel(f"PC2（{var[1] * 100:.1f}%）", fontsize=12)
    ax.set_aspect("equal", adjustable="datalim")  # 两轴同尺度，簇内距离与簇间距离可直接比较
    ax.axhline(0, color="#ccc", lw=0.8, zorder=1)
    ax.axvline(0, color="#ccc", lw=0.8, zorder=1)
    ax.legend(frameon=False, fontsize=11, loc="upper center", bbox_to_anchor=(0.5, 1.13), ncol=2)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(path)
    logger.info("wrote %s", path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--svg", help="save PCA figure to this SVG path")
    ap.add_argument("--selftest", action="store_true", help="assert numbers quoted in §13.1")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    sim = simulate()
    res = analyse(sim)
    rows = top_table(sim, res)
    n_chl = sum(r[4] == "叶绿素合成" for r in rows)
    n_sig = int(np.nansum(res["padj"] < 0.05))
    print(f"PC1 {res['var'][0] * 100:.1f}%  PC2 {res['var'][1] * 100:.1f}%")
    print(f"padj<0.05: {n_sig} genes (all of them reflect the batch offset; true treatment effect = 0)")
    print("gene\tlog2FC\tp\tpadj\tannotation\tbatch_offset(truth)")
    for g, l, p, q, ann, off in rows:
        print(f"{g}\t{l:.2f}\t{p:.2e}\t{q:.3f}\t{ann}\t{off}")
    print(f"chlorophyll genes in top 10: {n_chl}")
    if a.svg:
        write_svg(res, a.svg)
    if a.selftest:
        assert res["var"][0] > 0.5, "PC1 should be dominated by the batch offset"
        assert all(r[5] for r in rows), "every top-10 gene must be a batch-offset gene"
        assert n_chl == 3, f"§13.1 quotes 3 chlorophyll genes in top 10, got {n_chl}"
        print("SELFTEST PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

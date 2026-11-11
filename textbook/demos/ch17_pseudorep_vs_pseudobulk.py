#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch17_pseudorep_vs_pseudobulk.py — 单细胞伪重复 vs pseudobulk 的 H0 假阳性率对比（合成算例）

服务于：教材第 17 章（单细胞与空间转录组）§17.5 失效条件第 1 条
「把细胞当重复做差异检验是伪重复，p 值严重偏小；须 pseudobulk」，
对应讲义 p02 §4.1 / §⑦-2 与仓库脚本 ../03_code/phd/scripts/02_pseudobulk_de.R。

合成设定（零差异基因，H0 处处为真）：
  - 2 组 × S 个生物学样本（默认 S=3，呼应 GSE222584 的处理间比较形态）；
  - 每个样本解离出 m 个细胞（m 取 250/1000/4000，模拟「每样本细胞数变化」；
    同一样本内的细胞可交换，故小 m 直接取大矩阵的前列子采样，分布不变）；
  - 每个 (样本, 基因) 有一个对数正态随机乘子（样本间方差 σ_sample > 0）——
    同一解离管的全部细胞共享这个乘子，这是「细胞不独立」的物理来源；
  - 每个细胞的计数 ~ Poisson(文库因子 × 样本乘子 × 基因均值)。
    （用 Poisson 而非负二项只为提速；结论只依赖样本层共享方差，不依赖细胞层噪声形态。）

两种检验都作用在 log1p(计数) 上，均为 Welch 双样本 t 检验，差别只在统计单位：
  ① 细胞级检验：把 3m 个细胞当独立样本（伪重复，= FindMarkers 的做法）；
  ② pseudobulk 检验：先把每样本的原始计数加和成 1 列，3 vs 3 做检验
    （= 02_pseudobulk_de.R 中 Matrix::rowSums 聚合的做法）。

正文引用的输出：
  - 每个 m 下两种检验的「假阳性率」（H0 下 p < α 的基因比例）：
    细胞级假阳性率随 m 逼近 1，pseudobulk 贴着 α ——
    即讲义 ⑥「显著基因数相比细胞级检验下降 1–2 个数量级」的方差结构机制；
  - 「无样本间方差」对照（σ_sample = 0，m = 4000）：细胞级假阳性率回落到 ≈ α，
    证明膨胀来自样本共享方差，而不是「大 N 本身错了」。

参数：
  --genes        基因数（默认 150）
  --samples      每组生物学样本数 S（默认 3）
  --reps         模拟重复次数 R（默认 20；对照组用 R/2）
  --alpha        显著性水平（默认 0.05）
  --sigma-sample 样本间对数标准差 σ_sample（默认 0.3；0 = 对照情形）
  --seed         随机种子（默认 20261104）

合成数据不得写成真实样本结果；真实数据流程需集群 conda 环境 ngs_phd_sc（unverified）。
只依赖 numpy + scipy；约 3–5 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch17_pseudorep_vs_pseudobulk.py --selftest
"""
import argparse

import numpy as np
from scipy import stats

GRID = (250, 1000, 4000)  # 每样本细胞数
M_MAX = 4000              # 实际抽样的最大列数，小 m 用子采样


def draw_counts(genes, samples_per_group, cells, sigma_sample, rng):
    """返回 (2S 个 (genes, cells) 计数矩阵, 组标签)。组间零差异（H0 为真）。"""
    mu_g = np.exp(rng.normal(0.0, 1.0, genes)) * 2.0  # 基因基线均值
    mats, groups = [], []
    for group in (0, 1):
        for _ in range(samples_per_group):
            mult = np.exp(rng.normal(0.0, sigma_sample, genes))[:, None]  # 样本层共享
            lib = np.exp(rng.normal(0.0, 0.25, cells))[None, :]
            lam = np.clip(mu_g[:, None] * mult * lib, 0.0, None)
            mats.append(rng.poisson(lam))
            groups.append(group)
    return mats, groups


def welch_from_stats(sum_x, sum_x2, n1, sum_y, sum_x2b, n2):
    """由充分统计量算逐基因 Welch t 的 p 值（向量化，不物化全部细胞值）。"""
    m1, m2 = sum_x / n1, sum_y / n2
    v1 = np.maximum(sum_x2 / n1 - m1**2, 1e-12)
    v2 = np.maximum(sum_x2b / n2 - m2**2, 1e-12)
    se = np.sqrt(v1 / n1 + v2 / n2)
    t = (m1 - m2) / se
    df = (v1 / n1 + v2 / n2) ** 2 / (
        (v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1)
    )
    return 2.0 * stats.t.sf(np.abs(t), df)


def one_rep_all_m(genes, samples_per_group, sigma_sample, rng, alpha):
    """一次抽样（M_MAX 列/样本），对 GRID 中每个 m 各算两种检验的逐基因 p 值。

    返回 {m: (细胞级 FP, pseudobulk FP)}。同一批细胞在组间可交换（H0 为真），
    故不同 m 共用同一次抽样，只改统计单位。
    """
    mats, groups = draw_counts(genes, samples_per_group, M_MAX, sigma_sample, rng)
    out = {}
    for m in GRID:
        n_sub = min(m, M_MAX)
        # ① 细胞级检验（伪重复）：同组各样本细胞池在一起，取每样本前 n_sub 列
        stats_by_group = []
        for group in (0, 1):
            sub = [np.log1p(mm[:, :n_sub]) for mm, g in zip(mats, groups) if g == group]
            stack = np.concatenate(sub, axis=1)  # genes × (S·n_sub)
            stats_by_group.append(
                (stack.sum(axis=1), (stack**2).sum(axis=1), stack.shape[1]))
        pvals_cell = welch_from_stats(*stats_by_group[0], *stats_by_group[1])

        # ② pseudobulk：每样本原始计数加总（rowSums 语义），S vs S
        pb = np.log1p(np.stack([mm[:, :n_sub].sum(axis=1) for mm in mats], axis=1))
        mask = np.array(groups) == 0
        pvals_pb = welch_from_stats(
            pb[:, mask].sum(axis=1), (pb[:, mask] ** 2).sum(axis=1), int(mask.sum()),
            pb[:, ~mask].sum(axis=1), (pb[:, ~mask] ** 2).sum(axis=1), int((~mask).sum()),
        )
        out[m] = ((pvals_cell < alpha).mean(), (pvals_pb < alpha).mean())
    return out


def fp_at(genes, samples_per_group, cells, sigma_sample, rng, alpha):
    """对照专用：只算一个 m 的细胞级 FP。"""
    mats, groups = draw_counts(genes, samples_per_group, cells, sigma_sample, rng)
    stats_by_group = []
    for group in (0, 1):
        sub = [np.log1p(mm) for mm, g in zip(mats, groups) if g == group]
        stack = np.concatenate(sub, axis=1)
        stats_by_group.append((stack.sum(axis=1), (stack**2).sum(axis=1), stack.shape[1]))
    pvals_cell = welch_from_stats(*stats_by_group[0], *stats_by_group[1])
    return (pvals_cell < alpha).mean()


def run(genes, samples_per_group, reps, alpha, sigma_sample, seed):
    print("合成算例（H0 处处为真：组间零差异基因；σ_sample > 0 = 同管细胞共享样本因子）")
    print(f"每组 {samples_per_group} 个生物学样本；每组基因数 {genes}；"
          f"重复 {reps} 次；α = {alpha}；σ_sample = {sigma_sample}；seed = {seed}\n")
    print(f"{'每样本细胞数 m':>14} | {'细胞级检验 FP（伪重复）':>22} | "
          f"{'pseudobulk FP':>14} | {'FP 倍数':>8}")
    print("-" * 70)
    acc = {m: [0.0, 0.0] for m in GRID}
    for rep_i in range(reps):
        rng = np.random.default_rng(seed + 1000 * rep_i)
        for m, (c, p) in one_rep_all_m(genes, samples_per_group,
                                       sigma_sample, rng, alpha).items():
            acc[m][0] += c
            acc[m][1] += p
    results = {m: (acc[m][0] / reps, acc[m][1] / reps) for m in GRID}
    for m in GRID:
        c, p = results[m]
        print(f"{m:>14} | {c:>22.3f} | {p:>14.3f} | {c / max(p, 1e-9):>7.1f}×")
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--genes", type=int, default=150)
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--sigma-sample", type=float, default=0.3)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    results = run(args.genes, args.samples, args.reps, args.alpha,
                  args.sigma_sample, args.seed)

    # 对照：无样本间方差（细胞真正 i.i.d.），细胞级检验应回到 ≈ α
    rng = np.random.default_rng(args.seed + 999)
    fc0 = [fp_at(args.genes, args.samples, 4000, 0.0, rng, args.alpha)
           for _ in range(max(args.reps // 2, 1))]
    control = float(np.mean(fc0))
    print(f"\n对照（σ_sample = 0，m = 4000）：细胞级 FP = {control:.3f}（应 ≈ α = {args.alpha}）"
          " —— 膨胀来自样本共享方差，不是大 N 本身")
    print("判读：m 越大，细胞级 FP 越逼近 1（伪重复的 p 值雪崩），pseudobulk 始终贴着 α；"
          "FP 倍数即讲义 ⑥「下降 1–2 个数量级」的机制演示。")
    print("真实数据对照（GSE222584，unverified）：02_pseudobulk_de.R 输出的 "
          "de_comparison_summary.tsv（sig_findmarkers vs sig_pseudobulk）。")

    if args.selftest:
        cell = [c for c, _ in results.values()]
        checks = [
            ("pseudobulk FP 全网格 ∈ [0.005, 0.10]",
             all(0.005 <= p <= 0.10 for _, p in results.values())),
            ("细胞级 FP 随 m 单调不减",
             all(a <= b + 0.05 for a, b in zip(cell, cell[1:]))),
            (f"细胞级 FP（m = 4000）> 0.5（实际 {results[4000][0]:.3f}）",
             results[4000][0] > 0.5),
            (f"细胞级 FP 最小格（m = 250）已 > 0.3（实际 {results[250][0]:.3f}，"
             "即少量细胞已足够撑破 α）", results[250][0] > 0.3),
            (f"对照组细胞级 FP ≈ α（{control:.3f} vs {args.alpha}，容差 ±0.03）",
             abs(control - args.alpha) <= 0.03),
        ]
        print("\n[selftest]")
        npass = 0
        for name, passed in checks:
            print(f"  {'PASS' if passed else 'FAIL'}  {name}")
            npass += passed
        print(f"{npass}/{len(checks)} PASS")
        if npass != len(checks):
            raise SystemExit(1)


if __name__ == "__main__":
    main()

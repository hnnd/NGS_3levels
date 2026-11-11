#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch25_power_gono_go.py — 统计功效与「检出 ≥ 50 个差异基因」离散判定阈值（合成算例）

服务于：教材第 25 章（课题设计与图表叙事）§25.5 失效条件第 4 条
「方案只写技术路线不写可证伪的预期结果与备选方案」与 §25.4 假说驱动设计的
量化支撑，对应讲义 p08 ③ 方案 B 的离散判定阈值（「若未能检出超过 50 个高置信度
抗性差异基因，则切入 LMD + 高深度 bulk RNA-seq」）、§④1 第三问（样本量功效
论证）、§⑦-1（Winner's Curse，功效不足时显著结果的效应量虚高）。

合成设定（设例，非任何真实课题的预测）：
  - G 个基因的表达矩阵，其中 --true-de 个真差异基因（|log2FC| ~ 正态截断，
    符号随机），其余为空白基因；对数表达 ~ 正态（噪声 σ=1，合成简化）；
  - 每组样本量 n 取网格（默认 3/6/10，呼应「3 生物学重复 × 2 品系」的
    方案 B 形态及其加倍/三倍对照）；
  - 逐基因 Welch t 检验 + Benjamini-Hochberg FDR 校正（q < --fdr）。

正文引用的输出：
  - 每个 n 的检出基因数中位数（BH 显著数）与 P(检出数 ≥ 50)（--reps 次估计）：
    全基因组 FDR 控制的坡度（0.05×i/G）决定「过线」远比单基因功效苛刻——
    本模型下 3 重复几乎检不出任何基因（中位 0）、6 重复检出个位数、
    10 重复才稳定越过 50 个阈值。讲义 ③ 方案 B「3 重复 + 检出下限 50 个」
    的组合因此必须经过功效推导才能自洽，这正是失效条件 4「只写路线不写
    可证伪预期」的量化反例；
  - 可检出 n 上显著真差异基因的 |log2FC| 中位数 vs 真值（Winner's Curse
    膨胀倍数）：低功效下「显著」等价于「幸运」，报道的效应量系统性偏大。
    n=3 时中位检出为 0、膨胀不可计算——「算不出」本身就是结论。

参数：
  --genes    基因数（默认 3000）
  --true-de  真差异基因数（默认 120）
  --n-grid   每组样本量网格（默认 "3 6 10"）
  --lfc      真差异基因 |log2FC| 的均值（默认 2.0，即「抗性 vs 感病」式的
             强效应设例；σ=1 的简单筛查模型下，全基因组 BH 校正的坡度使
             3/6/10 重复呈 0 / 个位数 / 越线 的梯度——见输出解读）
  --alpha    原始显著性水平（默认 0.05，仅用于 t 检验）
  --fdr      BH 校正阈值（默认 0.05）
  --threshold 离散判定阈值：检出基因数下限（默认 50，同讲义 ③ 方案 B）
  --reps     模拟重复次数（默认 60）
  --seed     随机种子（默认 20261105）

合成数据不得写成真实样本结果；真实数据口径见 06_data/phd/README.md
「p08 课题设计：不使用统一数据」（学生本人课题，unverified）。
只依赖 numpy + scipy；约 0.3 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch25_power_gono_go.py --selftest
"""
import argparse

import numpy as np
from scipy import stats
from scipy.stats import nct, t as tdist


def bh_adjust(pvals):
    """Benjamini-Hochberg 校正，返回 q 值数组。"""
    n = pvals.size
    order = np.argsort(pvals)
    ranked = pvals[order] * n / (np.arange(n) + 1)
    q = np.empty(n)
    q[order] = np.minimum.accumulate(ranked[::-1])[::-1]
    return np.clip(q, 0.0, 1.0)


def one_rep(genes, true_de, n_per_group, lfc_mean, rng):
    """单次模拟：返回（检出数, 检出且为真数, 检出真差异基因的估计|LFC|数组）。"""
    logfc = np.zeros(genes)
    idx = rng.choice(genes, true_de, replace=False)
    sign = rng.choice((-1.0, 1.0), true_de)
    logfc[idx] = sign * np.abs(rng.normal(lfc_mean, 0.25, true_de))
    # 对数表达：组 0 ~ N(0,1)，组 1 ~ N(logfc,1)
    g0 = rng.normal(0.0, 1.0, (genes, n_per_group))
    g1 = logfc[:, None] + rng.normal(0.0, 1.0, (genes, n_per_group))
    pvals = stats.ttest_ind(g0, g1, axis=1, equal_var=False).pvalue
    qvals = bh_adjust(pvals)
    hit = qvals < 0.05
    est_lfc = np.abs(g1.mean(axis=1) - g0.mean(axis=1))
    return int(hit.sum()), int((hit & (logfc != 0)).sum()), est_lfc[hit & (logfc != 0)]


def run(genes, true_de, n_grid, lfc_mean, threshold, reps, seed):
    print("合成算例（设例：真差异基因 |log2FC|≈{:.1f} 的基因表达筛查；"
          "非任何真实课题的预测）".format(lfc_mean))
    print(f"G = {genes}；BH-FDR < 0.05；离散阈值 = 检出 ≥ {threshold} 个；"
          f"reps = {reps}；seed = {seed}\n")
    print(f"{'n/组':>5} | {'单基因功效':>8} | {'检出数中位':>8} | "
          f"{'P(≥阈值)':>9} | {'假检出中位':>8} | {'WC 膨胀':>8}")
    print("-" * 62)
    out = {}
    for n in n_grid:
        counts, fakes, wc_med = [], [], []
        for rep in range(reps):
            rng = np.random.default_rng(seed + 9176 * rep + n)
            n_hit, n_true_hit, est = one_rep(genes, true_de, n, lfc_mean, rng)
            counts.append(n_hit)
            fakes.append(n_hit - n_true_hit)
            if est.size:
                wc_med.append(np.median(est))
        counts = np.array(counts)
        p_cross = float((counts >= threshold).mean())
        # 解析单基因功效（非中心 t）供模拟对照
        df = 2 * n - 2
        nc = lfc_mean * np.sqrt(n / 2)
        tcrit = tdist.ppf(1 - 0.025, df)
        power_analytic = float(1 - nct.cdf(tcrit, df, nc) + nct.cdf(-tcrit, df, nc))
        wc = float(np.mean(wc_med)) if wc_med else float("nan")
        out[n] = (float(np.median(counts)), p_cross, float(np.median(fakes)), wc)
        wc_str = f"{wc / lfc_mean:>7.2f}×" if wc_med else "  不可算"
        print(f"{n:>5} | {power_analytic:>8.3f} | {np.median(counts):>8.0f} | "
              f"{p_cross:>9.3f} | {np.median(fakes):>8.1f} | {wc_str}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--genes", type=int, default=3000)
    ap.add_argument("--true-de", type=int, default=120)
    ap.add_argument("--n-grid", type=int, nargs="+", default=[3, 6, 10])
    ap.add_argument("--lfc", type=float, default=2.0)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--fdr", type=float, default=0.05)
    ap.add_argument("--threshold", type=int, default=50)
    ap.add_argument("--reps", type=int, default=60)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    out = run(args.genes, args.true_de, args.n_grid, args.lfc,
              args.threshold, args.reps, args.seed)
    med = [out[n][0] for n in args.n_grid]
    pcross = [out[n][1] for n in args.n_grid]
    # Winner's Curse：在检出数 > 0 的最小 n 上评估（更小的 n 无显著基因可测，
    # 「不可算」本身即是功效不足的证据）
    wc_ns = [n for n in args.n_grid if out[n][0] > 0]
    wc_first = out[wc_ns[0]][3] if wc_ns else float("nan")
    print("\n判读：「检出下限 50 个」这类离散阈值必须与功效推导绑定——在假定效应量下"
          " P(过线) 就是方案的置信度；全基因组 FDR 校正的坡度使「过线」远比单基因"
          "功效苛刻。功效不足时显著基因的效应量报道值虚高（Winner's Curse），"
          "Plan B 触发概率反而被低估。")

    if args.selftest:
        checks = [
            ("检出数中位数随 n 严格递增",
             all(a < b for a, b in zip(med, med[1:]))),
            (f"P(≥{args.threshold}) 随 n 单调不减",
             all(a <= b + 1e-9 for a, b in zip(pcross, pcross[1:]))),
            (f"最小 n={args.n_grid[0]} 时 P(≥{args.threshold}) < 0.05"
             f"（实际 {pcross[0]:.3f}）", pcross[0] < 0.05),
            (f"最大 n={args.n_grid[-1]} 时 P(≥{args.threshold}) > 0.5"
             f"（实际 {pcross[-1]:.3f}）", pcross[-1] > 0.5),
            (f"Winner's Curse 在最小可检出 n（{wc_ns[0]}）膨胀 > 1.1×"
             f"（实际 {wc_first / args.lfc:.2f}×）", wc_first > 1.1 * args.lfc),
        ]
        print("\n[selftest]")
        npass = sum(pass_ for _, pass_ in checks)
        for name, passed in checks:
            print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        print(f"{npass}/{len(checks)} PASS")
        if npass != len(checks):
            raise SystemExit(1)


if __name__ == "__main__":
    main()

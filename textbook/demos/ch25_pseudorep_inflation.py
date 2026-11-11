#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch25_pseudorep_inflation.py — 把技术重复当生物学重复：n 虚增与假阳性膨胀（合成算例）

服务于：教材第 25 章（课题设计与图表叙事）§25.5 失效条件第 2 条
「图注未写清 n 的含义（细胞、样本还是重复）」的机制演示，对应讲义 p08
§4.5 审稿人防御点 1（把 1 只小鼠的 3 块组织切片称为 n=3 生物学重复属于
学术硬伤）与 §⑨-7（图注必须写明 n 是生物学独立重复还是技术测定）。

合成设定（零假设为真：组间不存在任何差异）：
  - 2 组 × S 个生物学样本（默认 S=3），每样本做 k 次技术重复测量
    （k 取 2/4/8，模拟「每样本测更多次」）；
  - 测量值 = 生物学样本潜变量 b_i ~ N(0, σ_b) + 技术误差 ε ~ N(0, σ_t)，
    同一样本的 k 次技术重复共享同一个 b_i ——「技术重复不独立」的物理来源；
  - --noise-ratio = σ_t/σ_b（默认 0.4，即技术测定比生物学变异更准的
    常见实验室情形；此时组内相关系数 ρ = 1/(1+0.4²) ≈ 0.86）。

两种检验（均为 Welch 双样本 t，差别只在统计单位）：
  ① 错误分析（伪重复）：把 S×k 个测量值当独立生物学样本（n = 9/18/36 vs 同）；
  ② 正确分析：每样本先对 k 次技术重复取均值，S vs S（n = 3 vs 3，不变）。

正文引用的输出：
  - H0 下两种分析的假阳性率（p < α 的基因比例，--reps 次模拟的均值）：
    错误分析 FP 显著 > α 且随 k 增大（名义 n 越大越自信，错得越狠），
    正确分析 FP 始终 ≈ α —— 即「n 写得不清」不只是标注瑕疵，而是直接
    改变结论的假阳性机制（失效条件 2 的量化形态）；
  - 名义 n 与实际有效 n 的比值：n_eff = n·k/(1+(k−1)·ρ)。

参数：
  --genes        基因数（默认 2000，使 FP 率标准误 ≈ 0.005）
  --samples      每组生物学样本数 S（默认 3）
  --grid         每样本技术重复数 k 的网格（默认 "2 4 8"）
  --noise-ratio  σ_t/σ_b（默认 0.4）
  --alpha        显著性水平（默认 0.05）
  --reps         模拟重复次数（默认 20）
  --seed         随机种子（默认 20261105）

合成数据不得写成真实样本结果；真实数据口径见 08_assessment/phd/proposal/
phd_proposal.md 评分要点「重复是生物学重复」（unverified，本演示不依赖集群）。
只依赖 numpy + scipy；约 0.2 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch25_pseudorep_inflation.py --selftest
"""
import argparse

import numpy as np
from scipy import stats


def simulate(genes, samples_per_group, tech_reps, noise_ratio, rng):
    """返回（测量矩阵 genes × (2S·k)，组标签长 2S·k）。H0：组间零差异。"""
    n_units = 2 * samples_per_group
    bio = rng.normal(0.0, 1.0, (genes, n_units))  # 生物学潜变量 b_i
    tech = rng.normal(0.0, noise_ratio, (genes, n_units, tech_reps))
    meas = bio[:, :, None] + tech                 # 共享 b_i ⇒ 重复间相关
    flat = meas.reshape(genes, n_units * tech_reps)
    labels = np.repeat(np.arange(n_units) // samples_per_group, tech_reps)
    return flat, labels


def p_values(meas, labels, samples_per_group, tech_reps):
    """同一批数据、两种统计单位，返回（错误分析 p, 正确分析 p）逐基因数组。"""
    g0, g1 = labels == 0, labels == 1
    p_wrong = stats.ttest_ind(meas[:, g0], meas[:, g1],
                              axis=1, equal_var=False).pvalue
    # 正确分析：每样本 k 次取均值后再检验
    n_units = meas.shape[1] // tech_reps
    means = meas.reshape(meas.shape[0], n_units, tech_reps).mean(axis=2)
    u_labels = np.arange(n_units) // samples_per_group
    u0, u1 = u_labels == 0, u_labels == 1
    p_right = stats.ttest_ind(means[:, u0], means[:, u1],
                              axis=1, equal_var=False).pvalue
    return p_wrong, p_right


def run(genes, samples_per_group, grid, noise_ratio, alpha, reps, seed):
    rho = 1.0 / (1.0 + noise_ratio ** 2)
    print("合成算例（H0 处处为真：组间零差异；同一样本的 k 次技术重复共享生物学潜变量）")
    print(f"每组生物学样本 S = {samples_per_group}；σ_t/σ_b = {noise_ratio} "
          f"(ρ = {rho:.3f})；α = {alpha}；reps = {reps}；seed = {seed}\n")
    print(f"{'每样本技术重复 k':>12} | {'名义 n/组':>8} | {'有效 n/组':>8} | "
          f"{'错误分析 FP':>10} | {'正确分析 FP':>10} | {'膨胀倍数':>8}")
    print("-" * 72)
    results = {}
    for k in grid:
        n_nominal = samples_per_group * k
        n_eff = n_nominal / (1.0 + (k - 1) * rho)
        wrong_acc, right_acc = 0.0, 0.0
        for rep in range(reps):
            rng = np.random.default_rng(seed + 100003 * rep + k)
            meas, labels = simulate(genes, samples_per_group, k, noise_ratio, rng)
            p_wrong, p_right = p_values(meas, labels, samples_per_group, k)
            wrong_acc += float((p_wrong < alpha).mean())
            right_acc += float((p_right < alpha).mean())
        fp_wrong, fp_right = wrong_acc / reps, right_acc / reps
        results[k] = (fp_wrong, fp_right)
        print(f"{k:>12} | {n_nominal:>8} | {n_eff:>8.2f} | "
              f"{fp_wrong:>10.3f} | {fp_right:>10.3f} | {fp_wrong / alpha:>7.1f}×")
    return results, rho


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--genes", type=int, default=2000)
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--grid", type=int, nargs="+", default=[2, 4, 8])
    ap.add_argument("--noise-ratio", type=float, default=0.4)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    results, rho = run(args.genes, args.samples, args.grid, args.noise_ratio,
                       args.alpha, args.reps, args.seed)
    fp_wrong = [results[k][0] for k in args.grid]
    fp_right = [results[k][1] for k in args.grid]
    print("\n判读：错误分析的名义 n 随 k 线性膨胀，但生物学信息只来自 S 个样本，"
          "FP 率因此系统性 > α；正确分析（先平均技术重复）在全部 k 下都贴着 α。")
    print("这回答讲义 ⑨-7 的「n 到底是多少」：先写统计单位，再谈数字。")

    if args.selftest:
        checks = [
            ("正确分析 FP 全网格 ∈ [0.02, 0.10]（应 ≈ α）",
             all(0.02 <= p <= 0.10 for p in fp_right)),
            ("错误分析 FP 全网格 > 2×α",
             all(p > 2 * args.alpha for p in fp_wrong)),
            ("错误分析 FP 随 k 单调不减（容差 0.01）",
             all(a <= b + 0.01 for a, b in zip(fp_wrong, fp_wrong[1:]))),
            (f"最大 k 处错误分析 FP ≥ 4×α（实际 {fp_wrong[-1]:.3f}，"
             f"名义 n = {args.samples * args.grid[-1]}/组）",
             fp_wrong[-1] >= 4 * args.alpha),
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

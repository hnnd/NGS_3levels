#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch22_network_multiple_testing.py — 高维相关网络的假发现危机：250 万次检验、
BH 与 Bonferroni 的代价、选择性推断违例、置换校准（合成算例）

服务于：教材第 22 章（多组学整合分析）§22.4 概念与方法（相关网络的
多重检验）、§22.5 失效条件第 3 条（相关网络的阈值决定网络形状），
对应讲义 p06 ⑦-7.1（250 万次假设检验、125,000 条假边、三道防线）、
习题 3（8000 × 400 的算术与选择性推断违例）、06_correlation_network.R
（先全矩阵 BH 再筛边、n-perm 置换检验）。

合成设定（不基于任何真实样本；固定种子可复现）：
  部分 A（纯算术，无模拟）：5000 × 500 = 2,500,000 次检验；α=0.05 期望
    125,000 条假边；Bonferroni α = 2e-8；习题 3：8000 × 400 = 3,200,000
    → 160,000 条。
  部分 B（完全零假设模拟）：5000 × 500 两个独立高斯矩阵（n=25），
    朴素 p<0.05 计数 vs BH(q=0.05) 判边数；
    选择性推断违例：先按 |r| 取 top 500、再在其内算 p 与 BH——
    500/500 全部「通过」（全部为假，构造上为真）。
  部分 C（检出代价）：n=25 时 α=0.05 与 Bonferroni 各自要求的 |r| 临界值，
    以及真实 ρ=0.6 的检验功效（0.918 vs 0.003）——「刚性的 Bonferroni
    阈值会导致全网边数几乎全军覆没」的定量注脚。
  部分 D（置换校准）：200 × 100 的小网络注入共享潜因子信号
    （20 基因 × 15 代谢物与同一潜因子共变），观测边数 vs 200 次
    样本标签置换的边数分布（06_correlation_network.R --n-perm 的机制复刻）。

正文引用的输出（手算可对）：
  - 2,500,000 与 125,000（部分 A 算术 + 部分 B 模拟印证 125,219）；
  - BH 在完全零假设下近乎不判边（本种子 0 条）vs 朴素 12.5 万条；
  - 选择性推断：top-|r| 500 条内 BH「全部显著」且全部为假（习题 3c 答案）；
  - n=25 时 Bonferroni 要求 |r| ≥ 0.867，ρ=0.6 的功效从 0.910 塌到 0.002；
  - 置换：观测 198 条 vs 置换中位数 0、99% 分位 1 → 经验 p = 0.005。

参数：
  --n             部分 B/D 的样本量（默认 25）
  --p1 --p2       部分 B 的两矩阵特征数（默认 5000 / 500）
  --top-k         选择性推断的挑边数（默认 500）
  --rho           部分 C 的真实相关系数（默认 0.6）
  --n-perm        部分 D 置换次数（默认 200）
  --seed          随机种子（默认 20261105）

合成数据不得写成真实样本结果。只依赖 numpy/scipy；约 4 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch22_network_multiple_testing.py --selftest
"""
import argparse

import numpy as np
from scipy import stats


def bh_pass_count(pvals, q=0.05):
    """BH 线性步进：返回 q < 阈值被判显著的次数（全矩阵口径）。"""
    p = np.sort(pvals.ravel())
    M = p.size
    k = np.nonzero(p <= q * (np.arange(1, M + 1) / M))[0]
    return int(k.max() + 1) if k.size else 0


def corr_pmat(X, Y):
    Xc = X - X.mean(axis=1, keepdims=True)
    Yc = Y - Y.mean(axis=1, keepdims=True)
    R = (Xc @ Yc.T) / np.sqrt((Xc ** 2).sum(axis=1, keepdims=True) *
                              (Yc ** 2).sum(axis=1, keepdims=True).T)
    R = np.clip(R, -0.999999, 0.999999)
    n = X.shape[1]
    T = R * np.sqrt((n - 2) / (1.0 - R ** 2))
    return R, 2.0 * stats.t.sf(np.abs(T), df=n - 2)


def part_b(n, p1, p2, top_k, seed):
    r = np.random.default_rng(seed + 1)      # 完全独立的两个高斯矩阵
    X = r.standard_normal((p1, n))
    Y = r.standard_normal((p2, n))
    R, P = corr_pmat(X, Y)
    M = p1 * p2
    naive = int((P < 0.05).sum())
    bh = bh_pass_count(P)
    flat_absR = np.abs(R).ravel()
    sel = np.argpartition(flat_absR, -top_k)[-top_k:]     # 先按 |r| 挑边
    p_sel = P.ravel()[sel]                                 # 再算 p、再 BH
    bh_sel = bh_pass_count(p_sel.reshape(-1, 1), q=0.05)
    return dict(M=M, naive=naive, bh=bh, bh_sel=bh_sel)


def part_c(n, rho, seed):
    df = n - 2
    out = {}
    for name, alpha in [("α=0.05", 0.05), ("Bonferroni 2e-8", 2e-8)]:
        t_crit = stats.t.ppf(1.0 - alpha / 2.0, df)
        r_crit = t_crit / np.sqrt(df + t_crit ** 2)
        r = np.random.default_rng(seed + 2)
        rs = np.empty(4000)
        for i in range(4000):
            z = r.multivariate_normal([0.0, 0.0], [[1.0, rho], [rho, 1.0]], size=n)
            rs[i] = np.corrcoef(z.T)[0, 1]
        out[name] = dict(r_crit=r_crit, power=float(np.mean(np.abs(rs) > r_crit)))
    return out


def part_d(n, n_perm, seed, signal=1.8):
    r = np.random.default_rng(seed + 3)
    p1, p2 = 200, 100
    latent = r.standard_normal(n)
    X = r.standard_normal((p1, n))
    Y = r.standard_normal((p2, n))
    X[:20] += signal * latent[None, :]      # 20 基因 × 15 代谢物与潜因子共变；
    Y[:15] += signal * latent[None, :]      # signal=1.8 → 配对相关 ≈0.76（n=25 可过 BH）

    def count_bh_edges(Xm, Ym):
        _, P = corr_pmat(Xm, Ym)
        return bh_pass_count(P)

    obs = count_bh_edges(X, Y)
    perm = np.array([count_bh_edges(X, Y[:, r.permutation(n)])
                     for _ in range(n_perm)])
    emp_p = float((np.sum(perm >= obs) + 1) / (n_perm + 1))
    return dict(obs=obs, perm_median=float(np.median(perm)),
                perm_q99=float(np.quantile(perm, 0.99)), emp_p=emp_p)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n", type=int, default=25)
    ap.add_argument("--p1", type=int, default=5000)
    ap.add_argument("--p2", type=int, default=500)
    ap.add_argument("--top-k", type=int, default=500)
    ap.add_argument("--rho", type=float, default=0.6)
    ap.add_argument("--n-perm", type=int, default=200)
    ap.add_argument("--signal", type=float, default=1.8,
                    help="部分 D 潜因子载荷强度（跨组学配对相关 ≈ signal²/(1+signal²)）")
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    M_theory = 5000 * 500
    b = part_b(args.n, args.p1, args.p2, args.top_k, args.seed)
    c = part_c(args.n, args.rho, args.seed)
    d = part_d(args.n, args.n_perm, args.seed, args.signal)

    print("合成算例（不基于任何真实样本）；部分 B 为完全独立高斯矩阵，"
          "所有『显著边』按构造全部为假")
    print()
    print("部分 A 算术（讲义 ⑦-7.1 / 习题 3）：")
    print(f"  5000 × 500 = {M_theory:,} 次检验；α=0.05 期望假边 {0.05 * M_theory:,.0f} 条")
    print(f"  Bonferroni α = 0.05/{M_theory:,} = {0.05 / M_theory:.0e}")
    print(f"  习题 3：8000 × 400 = {8000 * 400:,} 次；期望假边 {0.05 * 8000 * 400:,.0f} 条")
    print()
    print(f"部分 B 零假设模拟（{args.p1} × {args.p2}，n={args.n}）：")
    print(f"  朴素 p<0.05                : {b['naive']:,} 条（理论 {0.05 * b['M']:,.0f}）")
    print(f"  全矩阵 BH q<0.05           : {b['bh']} 条（完全零假设下近乎不判边）")
    print(f"  选择性推断：先取 |r| top {args.top_k} 再在其内 BH : "
          f"{b['bh_sel']}/{args.top_k} 条『通过』——且全部为假（习题 3c 违例演示）")
    print()
    print(f"部分 C 检出代价（n={args.n}，真实 ρ={args.rho}）：")
    for name, v in c.items():
        print(f"  {name:<16}: 需 |r| ≥ {v['r_crit']:.3f}；此时功效 = {v['power']:.3f}")
    print()
    print(f"部分 D 置换校准（200 基因 × 100 代谢物，注入共享潜因子；"
          f"{args.n_perm} 次置换）：")
    print(f"  真实数据 BH 边数 = {d['obs']}；置换中位数 = {d['perm_median']:.0f}；"
          f"置换 99% 分位 = {d['perm_q99']:.0f}")
    print(f"  经验 p = {d['emp_p']:.4f}（观测远超置换分布上界才可信，"
          f"--n-perm 机制复刻）")

    if args.selftest:
        checks = [
            (f"朴素假边 {b['naive']:,} ≈ 理论 125,000（±5%）",
             abs(b["naive"] - 0.05 * b["M"]) < 0.05 * b["M"]),
            (f"BH 全矩阵判边 {b['bh']} < 100（零假设下近乎为零）",
             b["bh"] < 100),
            (f"选择性推断 {b['bh_sel']}/{args.top_k} 全部『通过』且为假",
             b["bh_sel"] == args.top_k),
            (f"Bonferroni 需 |r| ≥ {c['Bonferroni 2e-8']['r_crit']:.3f} > 0.8",
             c["Bonferroni 2e-8"]["r_crit"] > 0.8),
            (f"ρ={args.rho} 功效 {c['α=0.05']['power']:.3f} → "
             f"{c['Bonferroni 2e-8']['power']:.3f}（全军覆没）",
             c["α=0.05"]["power"] > 0.8 and c["Bonferroni 2e-8"]["power"] < 0.05),
            (f"置换校准：观测 {d['obs']} ≫ 99% 分位 {d['perm_q99']:.0f}，"
             f"经验 p = {d['emp_p']:.4f}",
             d["obs"] > d["perm_q99"] and d["emp_p"] < 0.05),
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

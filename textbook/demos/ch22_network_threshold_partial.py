#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch22_network_threshold_partial.py — 间接连锁伪边与偏相关、网络阈值敏感性、
WGCNA 软阈值 R² 的非检验本质（合成算例）

服务于：教材第 22 章（多组学整合分析）§22.4 概念与方法（相关 vs 偏相关
网络、网络阈值的敏感性、WGCNA 软阈值）、§22.5 失效条件第 3 条（相关网络
的阈值决定网络形状），对应讲义 p06 §4.9（间接连锁伪迹、GGM 与偏相关、
阈值稳定性敏感度曲线）、⑦-7.2（软阈值拟合优度绝非统计学假设检验）、
⑥-6.1 排查矩阵（soft_threshold.png 与 threshold_sensitivity.png 的判读）、
06_wgcna_analysis.R（--sft-target 0.8 的停机判据）。

合成设定（不基于任何真实样本；固定种子可复现）：
  部分 A（间接伪边）：调控因子 B 同时驱动 A 与 C（A = 1.5B + ε，C = 1.5B + ε），
    A、C 间无直接生化联系；展示 Pearson(A,C) 高度显著而给定 B 的偏相关 ≈ 0。
  部分 B（阈值敏感性）：60 节点、15 个四节点块，块内真实相关分别取
    ρ=0.60（脆弱网络：抽样后大量边落在临界阈值附近）与 ρ=0.95（稳健网络），
    统计 |r| 阈值 0.50→0.95 网格上的边数曲线与报告区间 [0.65, 0.75] 内的相对变化。
  部分 C（软阈值 R² 非检验本质）：复刻 pickSoftThreshold 的 scale-free 拟合口径
    （10 个等宽连接度箱，log10(密度) 对 log10(箱中点) 线性拟合的 R²），
    比较三种输入：重尾载荷潜因子数据（真实模块结构）、按样本打乱的数据
    （毁掉基因-基因相关、保留边缘分布）、log 变换后的计数样数据；
    同时报告各 β 下的平均连接度（讲义 ⑥-6.1：R² 与连接度要并读）。

正文引用的输出（手算可对）：
  - 链式伪边 cor(A,C) ≈ 0.88、p ≈ 1e-7，偏相关 ≈ 0（给定 B，多次模拟均值）；
  - 脆弱网在报告区间 [0.65, 0.75] 边数 -77%，稳健网 -7%；脆弱网 0.05 步长的
    最大单步相对跌落 >50%（阈值轻微扰动即崩塌，§4.9 的合成复现）；
  - 结构数据的 R² 在 β=10 跨 0.8（平均连接度仍 ≈4）；打乱数据与计数样数据
    在连接度有意义区间（k̄ ≥ 1）内 R² 不达 0.5——高 β 下 R² 会因网络稀疏化
    虚高，须与平均连接度并读；R² 本身不是检验（⑦-7.2），计数样低位徘徊
    复现讲义 ⑨-E2。

参数：
  --n             部分 A/B 的样本量（默认 20）
  --p-nodes       部分 B 的节点数（默认 60）
  --weak-rho      脆弱网块内相关（默认 0.60）
  --strong-rho    稳健网块内相关（默认 0.95）
  --n-genes       部分 C 的基因数（默认 400）
  --seed          随机种子（默认 20261105）

合成数据不得写成真实样本结果。只依赖 numpy/scipy；约 2 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch22_network_threshold_partial.py --selftest
"""
import argparse

import numpy as np


def part_a(n, seed, n_sim=3000):
    from scipy import stats
    r_ac, p_ac, pvals = [], [], []
    for s in range(n_sim):
        r = np.random.default_rng(seed + 1 + s)
        B = r.standard_normal(n)
        A = 1.5 * B + r.normal(0.0, 0.5, n)
        C = 1.5 * B + r.normal(0.0, 0.5, n)
        r_ac.append(np.corrcoef(A, C)[0, 1])
        Xd = np.column_stack([np.ones(n), B])
        ra = A - Xd @ np.linalg.lstsq(Xd, A, rcond=None)[0]
        rc = C - Xd @ np.linalg.lstsq(Xd, C, rcond=None)[0]
        p_ac.append(np.corrcoef(ra, rc)[0, 1])
        t = r_ac[-1] * np.sqrt((n - 2) / (1.0 - r_ac[-1] ** 2))
        pvals.append(2.0 * stats.t.sf(abs(t), df=n - 2))
    return dict(r_ac=float(np.mean(r_ac)), p_ac=float(np.mean(p_ac)),
                pval=float(np.median(pvals)),
                frac_sig=float(np.mean(np.array(pvals) < 0.05)))


def part_b(n, p_nodes, weak_rho, strong_rho, seed):
    thr = np.arange(0.50, 0.951, 0.05)

    def counts(rho):
        rng = np.random.default_rng(seed + 2)
        Z = rng.standard_normal((n, p_nodes))
        for b in range(p_nodes // 4):
            idx = np.arange(4 * b, 4 * b + 4)
            z0 = Z[:, idx[0]] / Z[:, idx[0]].std()
            for j in idx[1:]:
                Z[:, j] = rho * z0 + np.sqrt(1.0 - rho ** 2) * rng.standard_normal(n)
        M = np.corrcoef(Z.T)
        iu = np.triu_indices(p_nodes, 1)
        return np.array([(np.abs(M[iu]) >= t).sum() for t in thr])

    cw, cs = counts(weak_rho), counts(strong_rho)
    # 报告区间 [0.65, 0.75] 内的相对变化（阈值索引 3 与 5）
    loss_w = 1.0 - cw[5] / max(cw[3], 1)
    loss_s = 1.0 - cs[5] / max(cs[3], 1)
    step_w = max(abs(cw[i + 1] - cw[i]) / max(cw[i], 1)
                 for i in range(len(cw) - 1))
    step_s = max(abs(cs[i + 1] - cs[i]) / max(cs[i], 1)
                 for i in range(len(cs) - 1))
    return dict(thr=thr, cw=cw, cs=cs, loss_w=loss_w, loss_s=loss_s,
                step_w=step_w, step_s=step_s)


def scale_free_scan(dat, powers=(2, 4, 6, 8, 10, 12, 14, 16)):
    """复刻 WGCNA pickSoftThreshold 的 scale-free 拟合口径（简化版）：
    邻接 a=|cor|^β，连接度 k=Σa；10 个等宽 k 箱，log10(密度) 对
    log10(箱中点) 线性拟合的 R²；同时返回平均连接度。"""
    C = np.corrcoef(dat.T)
    np.fill_diagonal(C, 0.0)
    r2, kbar = [], []
    for beta in powers:
        A = np.abs(C) ** beta
        k = A.sum(axis=1)
        kk = k[k > 0]
        if kk.size < 20:
            r2.append(np.nan)
            kbar.append(0.0)
            continue
        dens, edges = np.histogram(kk, bins=10)
        mid = 0.5 * (edges[1:] + edges[:-1])
        m = dens > 0
        ld = np.log10(dens[m])
        slope, icept = np.polyfit(np.log10(mid[m]), ld, 1)
        pred = slope * np.log10(mid[m]) + icept
        ss_res = ((ld - pred) ** 2).sum()
        ss_tot = ((ld - ld.mean()) ** 2).sum()
        r2.append(float(1.0 - ss_res / ss_tot) if ss_tot > 0 else np.nan)
        kbar.append(float(kk.mean()))
    return np.array(r2), np.array(kbar)


def part_c(n_genes, seed):
    r = np.random.default_rng(seed + 3)
    n = 20
    nF = 5
    W = np.exp(r.normal(0.0, 1.0, (nF, n_genes))) * r.choice([-1.0, 1.0], (nF, n_genes))
    F = r.standard_normal((n, nF))
    X = F @ W + 2.0 * r.standard_normal((n, n_genes))
    X = (X - X.mean(axis=0)) / X.std(axis=0)
    Xp = X.copy()
    for j in range(n_genes):
        Xp[:, j] = X[r.permutation(n), j]          # 毁掉基因-基因相关
    lam = np.exp(r.normal(3.0, 1.0, (n, n_genes)))
    cnt = r.poisson(lam)
    Xc = np.log2(cnt + 1.0)                         # 计数样输入（log 后）
    powers = (2, 4, 6, 8, 10, 12, 14, 16)
    r2_real, kb_real = scale_free_scan(X, powers)
    r2_perm, kb_perm = scale_free_scan(Xp, powers)
    r2_cnt, kb_cnt = scale_free_scan(Xc, powers)  # 计数样输入（log 后）

    def meaningful_max(r2, kb):
        m = np.array(kb) >= 1.0
        return float(np.nanmax(np.array(r2)[m])) if m.any() else np.nan

    return dict(powers=powers, r2_real=r2_real, kb_real=kb_real,
                r2_perm=r2_perm, kb_perm=kb_perm, r2_cnt=r2_cnt, kb_cnt=kb_cnt,
                mm_real=meaningful_max(r2_real, kb_real),
                mm_perm=meaningful_max(r2_perm, kb_perm),
                mm_cnt=meaningful_max(r2_cnt, kb_cnt))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--p-nodes", type=int, default=60)
    ap.add_argument("--weak-rho", type=float, default=0.60)
    ap.add_argument("--strong-rho", type=float, default=0.95)
    ap.add_argument("--n-genes", type=int, default=400)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    a = part_a(args.n, args.seed)
    b = part_b(args.n, args.p_nodes, args.weak_rho, args.strong_rho, args.seed)
    c = part_c(args.n_genes, args.seed)

    print("合成算例（不基于任何真实样本）")
    print()
    print(f"部分 A 间接连锁伪边（B 同时驱动 A 与 C，A-C 无直接联系，n={args.n}，"
          f"多次模拟均值）：")
    print(f"  Pearson cor(A,C) = {a['r_ac']:+.3f}（p 中位 = {a['pval']:.1e}，"
          f"p<0.05 比例 {a['frac_sig']:.0%}——『显著』但纯属间接）")
    print(f"  给定 B 的偏相关   = {a['p_ac']:+.3f}（直接相关被条件独立破除）")
    print()
    print(f"部分 B 阈值敏感性（{args.p_nodes} 节点 15 块，块内相关 "
          f"{args.weak_rho}(脆弱) / {args.strong_rho}(稳健)，n={args.n}）：")
    print("  阈值:      " + " ".join(f"{t:.2f}" for t in b["thr"]))
    print("  脆弱网边数: " + " ".join(str(int(v)) for v in b["cw"]))
    print("  稳健网边数: " + " ".join(str(int(v)) for v in b["cs"]))
    print(f"  报告区间 [0.65, 0.75] 内边数跌落：脆弱网 {b['loss_w']:.0%}，"
          f"稳健网 {b['loss_s']:.0%}")
    print(f"  0.05 步长最大单步相对跌落：脆弱网 {b['step_w']:.0%}，"
          f"稳健网 {b['step_s']:.0%}（稳健网的跌落只在阈值逼近真实 ρ 的尾端）")
    print()
    print(f"部分 C 软阈值 R²（{args.n_genes} 基因 × 20 样本，复刻 "
          f"pickSoftThreshold 拟合口径；R² 与平均连接度并读）：")
    print("  β        : " + " ".join(f"{p:d}" for p in c["powers"]))
    print("  结构数据 : R² " + " ".join(f"{v:.2f}" for v in c["r2_real"]) +
          " | k̄ " + " ".join(f"{v:.0f}" for v in c["kb_real"]))
    print("  打乱数据 : R² " + " ".join(f"{v:.2f}" for v in c["r2_perm"]) +
          " | k̄ " + " ".join(f"{v:.1f}" for v in c["kb_perm"]))
    print("  计数样   : R² " + " ".join(f"{v:.2f}" for v in c["r2_cnt"]) +
          " | k̄ " + " ".join(f"{v:.0f}" for v in c["kb_cnt"]))
    print("  连接度有意义区间（k̄ ≥ 1）内的最大 R²：结构数据 {:.2f}，"
          "打乱数据 {:.2f}，计数样 {:.2f}——高 β 下任何数据的 R² 都会因网络"
          "稀疏化而虚高，只有 k̄ 仍可观时的 R² 才作数".format(
              c["mm_real"], c["mm_perm"], c["mm_cnt"]))

    if args.selftest:
        checks = [
            (f"间接伪边显著（cor={a['r_ac']:+.3f}，p<0.05 比例 {a['frac_sig']:.0%}）",
             a["frac_sig"] > 0.9),
            (f"偏相关破除伪边（均值 {a['p_ac']:+.3f}，|·| < 0.1）",
             abs(a["p_ac"]) < 0.1),
            (f"脆弱网报告区间内跌落 {b['loss_w']:.0%} > 40%",
             b["loss_w"] > 0.4),
            (f"稳健网报告区间内几乎不变（跌落 {b['loss_s']:.0%} < 10%）",
             b["loss_s"] < 0.10),
            (f"结构数据 R² 跨 0.8 时连接度仍可观（β=10: "
             f"R²={c['r2_real'][4]:.2f}, k̄={c['kb_real'][4]:.0f}）",
             c["r2_real"][4] >= 0.8 and c["kb_real"][4] >= 2),
            (f"打乱数据在 k̄≥1 区间 R² 不达 0.8（max={c['mm_perm']:.2f}）"
             f"——R² 不是检验（⑦-7.2）", c["mm_perm"] < 0.8),
            (f"计数样在 k̄≥1 区间 R² 低位徘徊（max={c['mm_cnt']:.2f} < 0.5，"
             f"复现讲义 E2）", c["mm_cnt"] < 0.5),
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch22_injection_order_confounding.py — 进样顺序是协变量：仪器漂移与非随机进样
把零差异特征读成生物差异（合成算例）

服务于：教材第 22 章（多组学整合分析）§22.4 概念与方法（QC 样本与批次漂移）、
§22.5 失效条件第 1 条（进样顺序是协变量：QC 样本漂移不校正会被读成生物差异），
对应讲义 p06 §4.2（仪器漂移的物理机理、Pooled QC 的三重使命）、
⑥-6.1 排查矩阵第一行（qc_drift_pca：QC 被拉成顺进样顺序的线 = 未校正漂移）。

合成设定（不基于任何真实样本；固定种子可复现）：
  - 20 个生物学样本、200 个特征，特征真实丰度组间无差异（零假设为真）；
  - 仪器灵敏度随进样针数单调衰减（总衰减约 57%，合成设定的强漂移情形）；
  - 场景 A（顺序设计）：对照组 10 个样本先进完、处理组 10 个样本后进——
    进样顺序与分组 100% 共线（讲义 §4.2 批评的非随机化上机）；
  - 场景 B（随机设计）：同样的 20 个样本、同样的漂移，进样顺序随机打乱；
  - 场景 C（QC-RSD 过滤）：一半特征带小仪器噪声（5%）、一半带大噪声（35%），
    按讲义 §4.2 / 06_metabolome_preprocess.R 的 RSD ≤ 20% 规则过滤。

正文引用的输出（手算可对）：
  - 场景 A 零差异特征的假阳性率 ≫ 名义 5%，场景 B 回到名义附近——
    「进样顺序与处理效应 100% 统计共线混杂，任何统计模型都无法把仪器衰减与
    生物学应答分离」（讲义 §4.2）的合成复现；
  - 场景 A 的 PCA 第一主成分与进样顺序强相关（组结构被顺序主导）；
  - QC 漂移轨迹的单调性（Spearman ≈ −1）与 RSD 过滤的保留率。

参数：
  --n-per-group   每组样本数（默认 10，共 20 个生物学样本）
  --n-features    特征数（默认 200）
  --drift-k       漂移指数衰减系数（默认 0.045，全程总衰减约 57%）
  --n-sim         场景 B 的重复次数（默认 1；>1 时报告假阳性率均值）
  --seed          随机种子（默认 20261105）

合成数据不得写成真实样本结果。只依赖 numpy/scipy；约 2 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch22_injection_order_confounding.py --selftest
"""
import argparse

import numpy as np
from scipy import stats


def simulate(n_per_group, n_feat, drift_k, n_sim, seed):
    rng = np.random.default_rng(seed)
    n = 2 * n_per_group
    order = np.arange(1, n + 1)
    drift = np.exp(-drift_k * order)
    group = np.array([0] * n_per_group + [1] * n_per_group)  # 0=对照 1=处理

    def fpr(X):
        pvals = np.empty(n_feat)
        for i in range(n_feat):
            pvals[i] = stats.ttest_ind(X[i, group == 0],
                                       X[i, group == 1]).pvalue
        return float(np.mean(pvals < 0.05))

    # 真实丰度（组间无差异）× 漂移；每次场景 B 重抽丰度、重打乱顺序
    fpr_ordered, fpr_random = [], []
    pc1_order_rho = []
    for s in range(max(n_sim, 1)):
        r = np.random.default_rng(seed + 1000 * s)
        F = np.exp(r.normal(0.0, 0.5, (n_feat, n))) * 1000.0
        X = F * drift[None, :]
        fpr_ordered.append(fpr(X))
        # PCA 第一主成分与进样顺序的相关（仅第一次重复记录）
        Xc = X - X.mean(1, keepdims=True)
        _, sv, vt = np.linalg.svd(Xc, full_matrices=False)
        pc1 = vt[0] * sv[0]
        pc1_order_rho.append(float(stats.spearmanr(pc1, order).statistic))
        perm = r.permutation(n)
        fpr_random.append(fpr(F * drift[perm][None, :]))

    # QC 漂移轨迹：QC 样本总强度 ~ 进样顺序（单调衰减 => Spearman ≈ −1）
    rho_qc = float(stats.spearmanr(order, drift).statistic)

    # QC-RSD 过滤：50% 特征噪声 SD 5%（稳定），50% 噪声 SD 35%（不稳定）
    r = np.random.default_rng(seed + 7)
    qc = np.empty((n_feat, 6))
    hi_noise = r.random(n_feat) < 0.5
    qc[hi_noise] = 100.0 * (1.0 + r.normal(0.0, 0.35, (int(hi_noise.sum()), 6)))
    qc[~hi_noise] = 100.0 * (1.0 + r.normal(0.0, 0.05, (int((~hi_noise).sum()), 6)))
    rsd = 100.0 * qc.std(axis=1, ddof=1) / qc.mean(axis=1)
    keep = rsd <= 20.0

    return dict(n=n, decay=1.0 - drift[-1] / drift[0],
                fpr_ordered=float(np.mean(fpr_ordered)),
                fpr_random=float(np.mean(fpr_random)),
                rho_qc=rho_qc,
                pc1_rho=float(np.mean(pc1_order_rho)),
                rsd_stable=float(np.median(rsd[~hi_noise])),
                rsd_unstable=float(np.median(rsd[hi_noise])),
                keep_frac=float(np.mean(keep)),
                keep_stable=float(np.mean(keep[~hi_noise])),
                keep_unstable=float(np.mean(keep[hi_noise])))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n-per-group", type=int, default=10)
    ap.add_argument("--n-features", type=int, default=200)
    ap.add_argument("--drift-k", type=float, default=0.045)
    ap.add_argument("--n-sim", type=int, default=1)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    r = simulate(args.n_per_group, args.n_features, args.drift_k,
                 args.n_sim, args.seed)

    print("合成算例：{} 个样本（对照 {} / 处理 {}，组间真实零差异），{} 个特征，"
          "仪器漂移总衰减 {:.0%}（强漂移情形）".format(
              r["n"], args.n_per_group, args.n_per_group,
              args.n_features, r["decay"]))
    print("  —— 不基于任何真实样本；零假设为真，任何『显著』都是假阳性")
    print()
    print("场景 A 顺序设计（对照先进完、处理后进，顺序与分组 100% 共线）：")
    print("  零差异特征假阳性率 p<0.05 : {:.3f}（名义 0.05）".format(r["fpr_ordered"]))
    print("  PCA PC1 与进样顺序 Spearman : {:+.3f}（顺序主导变异）".format(r["pc1_rho"]))
    print("场景 B 随机进样（同样漂移、顺序打乱）：")
    print("  零差异特征假阳性率 p<0.05 : {:.3f}".format(r["fpr_random"]))
    print()
    print("QC 漂移轨迹：QC 总强度 ~ 进样顺序 Spearman = {:+.3f}（单调衰减应 ≈ −1）".format(r["rho_qc"]))
    print("QC-RSD 过滤（RSD ≤ 20% 保留，讲义 §4.2 / 06_metabolome_preprocess.R）：")
    print("  稳定特征（噪声 5%）RSD 中位 : {:.1f}% → 保留 {:.0%}".format(
        r["rsd_stable"], r["keep_stable"]))
    print("  不稳定特征（噪声 35%）RSD 中位 : {:.1f}% → 保留 {:.0%}".format(
        r["rsd_unstable"], r["keep_unstable"]))
    print("  全体保留率 : {:.0%}".format(r["keep_frac"]))

    if args.selftest:
        checks = [
            (f"顺序设计假阳性率({r['fpr_ordered']:.3f}) ≫ 名义 0.05 "
             f"（漂移被读成生物差异）", r["fpr_ordered"] > 0.25),
            (f"PC1 与进样顺序强相关({r['pc1_rho']:+.3f} > 0.6)",
             r["pc1_rho"] > 0.6),
            (f"随机设计假阳性率({r['fpr_random']:.3f}) 回到名义 5% 附近",
             0.02 <= r["fpr_random"] <= 0.09),
            (f"顺序 vs 随机假阳性率倍数 "
             f"{r['fpr_ordered'] / max(r['fpr_random'], 1e-9):.1f}×",
             r["fpr_ordered"] > 5 * r["fpr_random"]),
            (f"QC 漂移轨迹单调（Spearman {r['rho_qc']:+.3f} ≤ −0.99）",
             r["rho_qc"] <= -0.99),
            (f"稳定特征保留({r['keep_stable']:.0%}) ≫ 不稳定特征保留({r['keep_unstable']:.0%})",
             r["keep_stable"] > 0.9 and r["keep_unstable"] < 0.3),
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

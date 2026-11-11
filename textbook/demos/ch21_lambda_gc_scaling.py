#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch21_lambda_gc_scaling.py — 膨胀因子 λ_GC 的数学本质与多基因标度律
λ ≈ 1 + N·h²_SNP/M_eff、λ_1000 标准化、λ 对尾部的钝感（合成算例）

服务于：教材第 21 章（全基因组关联分析与后 GWAS）§21.4 概念与方法
（诊断三图的阅读顺序）、§21.5 失效条件第 2 条（诊断三图顺序不能反），
对应讲义 p05 ⑦-7.3（λ_GC 定义 median(χ²_obs)/0.4549、
Yang et al. 2011 标度律 λ ≈ 1 + N·h²_SNP/M_eff、标准化
λ_1000 = 1 + (λ−1)·1000/N、「λ<1.05 才算干净」在大样本上是错的）、
⑥-6.1 诊断矩阵（λ≈1.00±0.05 + 仅尾部翘起 = 健康形态），
及 ⑩ 习题 2（n=150 λ=1.05 vs n=3500 λ=1.15 的先验辨析）。

合成设定（不基于任何真实群体；固定种子可复现）：
  - 部分 0（定义核验）：纯中性零假设 p 值（均匀分布）→ λ 应 ≈ 1；
    次序统计量经验分位数核对 E[p_(i)] = i/(M+1)；卡方(df=1) 理论中位数
    核对讲义常数 0.454937。
  - 部分 1（标度律）：把讲义公式当成生成模型——M_eff 个统计独立、等效应
    的「有效检验单位」，每个单位解释方差 h²/M_eff，则每个被试标记的
    非中心参数 nc = N·h²/M_eff，χ² ~ χ²₁(nc)，λ = median(χ²)/0.4549。
    对 (N=413, 3500, 5000, 10000) × (h²=0.5, M_eff=25000) 四个场景
    采样核验 λ ≈ 1 + N·h²/M_eff —— 即讲义「N 扩展至数千甚至上万人时，
    即使完美消除分层，λ 仍自发达到 1.10–1.20」的定量复现
    （N=5000 → 1.10；N=10000 → 1.20；RDP1 规模 N=413 → ≈1.01）。
  - 部分 2（习题 2 算术）：团队 A（n=150, λ=1.05）与团队 B（n=3500,
    λ=1.15）的 λ_1000 标准化与先验结论 —— 手算可对。
  - 部分 3（λ 的钝感与尾部）：在 N=3500 的多基因 p 值里注入 5 个强信号
    （nc=40，p ≈ 1e-10 量级），λ 几乎不动（中位数不受尾部影响），
    而最小 p 值天差地别 —— 「λ 检测整体抬升、不检测尾部离群」正是
    05_gwas_diagnostics.R 注释与 ⑥-6.1「λ≈1 且仅尾部翘起 = 健康」的
    统计根据，也是「先 QQ 后曼哈顿」顺序可行的原因。

正文引用的输出（手算可对）：
  - 四个场景的 λ 观测 vs 理论 1 + N·h²/M_eff（RDP1 规模 ≈1.008；
    3500 → 1.07；5000 → 1.10；10000 → 1.20）；
  - λ_1000：A → 1.3333，B → 1.0429 —— B 的模型控制反而更好；
  - 注入 5 个强信号前后 λ 之差 < 0.005，最小 p 值从 ~1e-6 级跳到 ~1e-10 级；
  - 卡方(df=1) 中位数 = 0.4549（讲义 0.454937）。

参数：
  --m-eff       有效独立检验数 M_eff（默认 25000，对应 ⑩ 习题 3 剪枝子集规模）
  --h2          SNP 遗传力 h²_SNP（默认 0.5）
  --n-rep       每个场景的重复采样数（默认 50，取中位数压噪声）
  --seed        随机种子（默认 20261104）

合成数据不得写成真实群体结果。只依赖 numpy/scipy；约 1 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch21_lambda_gc_scaling.py --selftest
"""
import argparse

import numpy as np
from scipy import stats

CHI2_MEDIAN_DF1 = 0.454936  # qchisq(0.5, df=1)=0.4549364；讲义 ⑦-7.3 写作 0.454937（末位差 1）


def lambda_gc(p):
    """基因组膨胀因子（05_gwas_diagnostics.R lambda_gc 同式）。"""
    p = p[np.isfinite(p) & (p > 0) & (p <= 1)]
    return float(np.median(stats.chi2.ppf(1.0 - p, df=1)) /
                 stats.chi2.ppf(0.5, df=1))


def sim_polygenic_lam(n, h2, m_eff, n_rep, rng):
    """M_eff 个等效应独立单位的标度律采样：返回 n_rep 个 λ 观测。"""
    nc = n * h2 / m_eff
    out = np.empty(n_rep)
    for i in range(n_rep):
        chi2 = rng.noncentral_chisquare(df=1, nonc=nc, size=m_eff)
        out[i] = float(np.median(chi2)) / stats.chi2.ppf(0.5, df=1)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--m-eff", type=int, default=25000)
    ap.add_argument("--h2", type=float, default=0.5)
    ap.add_argument("--n-rep", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)

    # ---- 部分 0：定义核验 ----
    med_theory = stats.chi2.ppf(0.5, df=1)
    m_null = 200000
    p_null = rng.uniform(size=m_null)
    lam_null = lambda_gc(p_null)
    p_sorted = np.sort(p_null)
    idx = np.array([100, m_null // 2, m_null - 2])
    obs_q = p_sorted[idx]
    exp_q = idx / (m_null + 1)

    print("部分 0（λ_GC 定义核验，合成零假设 p ~ Uniform(0,1)，M=200000）")
    print("  卡方(df=1) 理论中位数 = {:.6f}（讲义 ⑦-7.3 常数 0.454937）".format(
        med_theory))
    print("  零假设 p 值的 λ_GC    = {:.4f}（应 ≈ 1）".format(lam_null))
    print("  次序统计量核对 E[p_(i)] = i/(M+1)：")
    for i, o, e in zip(idx, obs_q, exp_q):
        print("    i={:>7}  观测 {:.6f}  期望 {:.6f}".format(i, o, e))
    print()

    # ---- 部分 1：标度律 λ ≈ 1 + N·h²/M_eff ----
    print("部分 1（Yang et al. 2011 标度律核验，h²={}，M_eff={}，{} 次重复中位）".format(
        args.h2, args.m_eff, args.n_rep))
    scenarios = [413, 3500, 5000, 10000]
    lam_obs = {}
    for n in scenarios:
        lo = sim_polygenic_lam(n, args.h2, args.m_eff, args.n_rep, rng)
        lam_obs[n] = float(np.median(lo))
        pred = 1.0 + n * args.h2 / args.m_eff
        tag = {413: "（RDP1 规模）", 3500: "（习题 2 团队 B）",
               5000: "", 10000: ""}[n]
        print("  N={:>6}{:　<12} λ 观测中位 = {:.4f}   理论 1+N·h²/M_eff = {:.4f}"
              .format(n, tag, lam_obs[n], pred))
    print("  —— N=5000 → 1.10、N=10000 → 1.20：讲义「数千至上万时 λ 自发达到")
    print("    1.10–1.20」的定量复现；「λ<1.05 才算干净」在大样本上不成立。")
    print()

    # ---- 部分 2：习题 2 算术（λ_1000 标准化）----
    lam_a, n_a = 1.05, 150
    lam_b, n_b = 1.15, 3500
    l1000_a = 1.0 + (lam_a - 1.0) * 1000.0 / n_a
    l1000_b = 1.0 + (lam_b - 1.0) * 1000.0 / n_b
    print("部分 2（习题 2 先验辨析：λ_1000 = 1 + (λ−1)·1000/N）")
    print("  团队 A：n=150,  λ=1.05 → λ_1000 = {:.4f}".format(l1000_a))
    print("  团队 B：n=3500, λ=1.15 → λ_1000 = {:.4f}".format(l1000_b))
    print("  —— 标准化后 B 的膨胀反而更小：不能凭 λ 原始值断言 B 控制更弱。")
    print()

    # ---- 部分 3：λ 对尾部钝感 ----
    nc = 3500 * args.h2 / args.m_eff
    chi2_base = rng.noncentral_chisquare(df=1, nonc=nc, size=args.m_eff)
    chi2_inj = chi2_base.copy()
    chi2_inj[:5] = rng.noncentral_chisquare(df=1, nonc=40.0, size=5)
    lam_base = float(np.median(chi2_base)) / stats.chi2.ppf(0.5, df=1)
    lam_inj = float(np.median(chi2_inj)) / stats.chi2.ppf(0.5, df=1)
    p_base = stats.chi2.sf(chi2_base, df=1)
    p_inj = stats.chi2.sf(chi2_inj, df=1)
    print("部分 3（λ 只用中位数、对尾部钝感；N=3500 场景注入 5 个 nc=40 强信号）")
    print("  注入前：λ = {:.4f}，min p = {:.2e}，-log10(p) 99.9% 分位 = {:.2f}"
          .format(lam_base, p_base.min(),
                  np.quantile(-np.log10(p_base), 0.999)))
    print("  注入后：λ = {:.4f}，min p = {:.2e}，-log10(p) 99.9% 分位 = {:.2f}"
          .format(lam_inj, p_inj.min(),
                  np.quantile(-np.log10(p_inj), 0.999)))
    print("  —— λ 几乎不动（中位数不受 5/25000 的尾部影响），尾部却翘起：")
    print("    ⑥-6.1「λ≈1 且仅尾部翘起 = 健康形态」的统计根据。")

    if args.selftest:
        checks = [
            ("卡方(df=1) 中位数 = 0.454936（讲义 0.454937 末位差 1）",
             abs(med_theory - CHI2_MEDIAN_DF1) < 1e-5),
            (f"零假设 λ({lam_null:.4f}) ≈ 1", 0.97 <= lam_null <= 1.03),
            ("次序统计量与 i/(M+1) 吻合（最大偏差 < 3e-3）",
             float(np.max(np.abs(obs_q - exp_q))) < 3e-3),
        ]
        for n in scenarios:
            pred = 1.0 + n * args.h2 / args.m_eff
            checks.append(
                (f"N={n}：λ 观测 {lam_obs[n]:.4f} ≈ 理论 {pred:.4f}（<0.02）",
                 abs(lam_obs[n] - pred) < 0.02))
        checks += [
            (f"λ_1000(A) = {l1000_a:.4f} = 1.3333（手算）",
             abs(l1000_a - 1.333333) < 1e-3),
            (f"λ_1000(B) = {l1000_b:.4f} = 1.0429（手算）",
             abs(l1000_b - 1.042857) < 1e-3),
            (f"注入强信号前后 λ 之差({abs(lam_inj - lam_base):.5f}) < 0.005"
             " —— λ 对尾部钝感", abs(lam_inj - lam_base) < 0.005),
            (f"注入后 min p({p_inj.min():.2e}) << 注入前({p_base.min():.2e})"
             " —— 尾部翘起可见", p_inj.min() < p_base.min() / 100),
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

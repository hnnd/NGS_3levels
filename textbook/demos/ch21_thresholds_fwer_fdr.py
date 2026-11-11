#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch21_thresholds_fwer_fdr.py — GWAS 显著性阈值的定量推演：M_eff Bonferroni、
人类 5e-8 的代价、LD 重复计数失真、置换检验金标准（合成算例）

服务于：教材第 21 章（全基因组关联分析与后 GWAS）§21.4 概念与方法
（显著性阈值：为什么 GWAS 严禁照搬转录组的常规校正）、§21.5 失效条件第 2 条
（照搬转录组 FDR 习惯定阈值），对应讲义 p05 §4.3（FWER vs FDR、M_eff、
人类 5×10⁻⁸ 的来历与移植后果、置换检验是公认最诚实的金标准）、⑦-7.4
（Bonferroni 与 FDR 分工）、⑩ 习题 3（50 万 SNP / 2.5 万剪枝子集的阈值
推演）、⑥-6.1 第四行（严禁私自放宽阈值）。

合成设定（不基于任何真实群体；固定种子可复现）：
  - 部分 A（算术锚点，手算规则）：M=500,000、M_eff=25,000 →
    0.05/M=1e-7、0.05/M_eff=2e-6（FWER）、1/M_eff=4e-5（suggestive）；
    人类 5e-8 = 0.05/1e6；RDP1 实测 M=36,901（06_data/phd/README.md p05
    实测规格）→ 0.05/M = 1.35e-6。
  - 部分 B（功效代价）：定量性状、SNP 解释方差份额 q 时非中心参数
    nc ≈ N·q；用 scipy 非中心卡方解 80% 功效所需 nc，再换算样本量 —
    — α=5e-8 比 α=2e-6 多需约 27% 样本；RDP1 规模（N=413）在 α=2e-6
    下 80% 功效只能检出解释 ≥ ~7.6% 方差的位点 —— 习题 3「假阴性灾难」
    的定量答案。
  - 部分 C（LD 重复计数失真）：B=2000 个连锁块 × 每块 L=25 个 SNP
    （块内共享潜因子，等效相关 ρ=0.95）；1 个因果块的全部 25 个标签
    SNP 带相同非中心参数 nc=40（合成设定：因果变异被 25 个等强度标签
    标记）。三种判读对照：① 全部 50000 个单 SNP 做 BH-FDR(q=0.05)，
    数「显著 SNP」；② 按块归并（理想化 --clump）数「独立位点」；
    ③ 块内 Bonferroni 得到有效位点 p（P<p 的均匀性在任意相关下成立），
    再跨块 BH —— 唯一在统计上合法的位点水平 FDR。
  - 部分 D（置换金标准）：纯零假设下模拟表型置换 1000 次，每次记录
    全基因组最小 p（LD 结构同上），经验 5% 分位即 FWER 阈值；与两个
    解析猜测对照——朴素 0.05/(B·L)（过度严格：经验 FWER ≈ 0.01）与
    块数口径 0.05/B（过度宽松：经验 FWER ≈ 0.21）。置换不依赖任何
    独立性假设，两个方向都猜错的场景它直接给出正确答案。

正文引用的输出（手算可对）：
  - 阈值算术：2e-6 / 4e-5 / 1e-7 / 5e-8 / 1.35e-6（RDP1）；
    人类阈值比 M_eff 口径严 40 倍、比朴素 0.05/M 严 2 倍；
  - 80% 功效所需 nc：α=2e-6 → ≈31（正态近似 (z+z₀.₈)²≈31.3），
    α=5e-8 → ≈40，样本量代价 ≈ +27%；RDP1 N=413 检出限 q ≈ 7.6%；
  - LD 失真：SNP 水平 BH 报 25 个「显著 SNP」全部来自同 1 个因果块，
    按块归并与合法位点检验都只报 1 个位点 —— §4.3「同源信号被反复
    多次计数」的量化；
  - 置换阈值 3.8e-6 ≈ 朴素口径的 3.8 倍（有效检验数 ≈ 1.3 万 vs
    名义 5 万）；朴素口径 FWER 0.01（过严）、块数口径 FWER 0.21（过松）。

参数：
  --blocks      连锁块数 B（默认 2000）
  --block-size  每块 SNP 数 L（默认 25）
  --rho         块内等效相关 ρ（默认 0.95）
  --nc          因果块每个标签 SNP 的非中心参数（默认 40）
  --perms       置换次数（默认 1000）
  --seed        随机种子（默认 20261104）

合成数据不得写成真实群体结果。只依赖 numpy/scipy；约 3 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch21_thresholds_fwer_fdr.py --selftest
"""
import argparse

import numpy as np
from scipy import stats


def bh_rejects(p, q):
    """Benjamini-Hochberg step-up：返回布尔拒绝向量。"""
    p = np.asarray(p, dtype=float)
    m = p.size
    order = np.argsort(p)
    ranked = p[order]
    thresh = q * (np.arange(1, m + 1) / m)
    below = ranked <= thresh
    if not below.any():
        return np.zeros(m, dtype=bool)
    k = np.max(np.nonzero(below)[0])
    rejected = np.zeros(m, dtype=bool)
    rejected[order[: k + 1]] = True
    return rejected


def nc_for_power(alpha, power, df=1):
    """使 P(χ²_df(nc) > χ²_df⁻¹(1−α)) = power 的非中心参数（二分求解）。"""
    crit = stats.chi2.ppf(1.0 - alpha, df=df)

    def pw(nc):
        return stats.ncx2.cdf(crit, df=df, nc=nc)

    lo, hi = 0.0, 200.0
    while pw(hi) > 1.0 - power:
        hi *= 2.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if pw(mid) > 1.0 - power:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--blocks", type=int, default=2000)
    ap.add_argument("--block-size", type=int, default=25)
    ap.add_argument("--rho", type=float, default=0.95)
    ap.add_argument("--nc", type=float, default=40.0)
    ap.add_argument("--perms", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    B, L, rho = args.blocks, args.block_size, args.rho
    m_total = B * L

    # ---- 部分 A：阈值算术 ----
    print("部分 A（阈值算术锚点，手算规则）")
    bonf_naive = 0.05 / 500000
    bonf_eff = 0.05 / 25000
    sug = 1.0 / 25000
    human = 5e-8
    rdp1 = 0.05 / 36901
    print("  0.05/500000（朴素 Bonf）        = {:.1e}".format(bonf_naive))
    print("  0.05/25000（M_eff Bonf，FWER） = {:.1e}".format(bonf_eff))
    print("  1/25000（suggestive）           = {:.1e}".format(sug))
    print("  5e-8（人类，= 0.05/1e6）        = {:.1e}".format(human))
    print("  0.05/36901（RDP1 实测 M）       = {:.2e}".format(rdp1))
    print("  人类阈值严格倍数：vs M_eff 口径 {:.0f}×；vs 朴素口径 {:.0f}×".format(
        bonf_eff / human, bonf_naive / human))
    print()

    # ---- 部分 B：功效代价 ----
    nc_2e6 = nc_for_power(2e-6, 0.8)
    nc_5e8 = nc_for_power(5e-8, 0.8)
    approx_2e6 = (stats.norm.ppf(1 - 1e-6) + stats.norm.ppf(0.8)) ** 2
    q_rdp1 = nc_2e6 / 413.0
    print("部分 B（80% 功效所需非中心参数 nc ≈ N·q，q = SNP 解释方差份额）")
    print("  α=2e-6 ：nc = {:.1f}（正态近似锚点 (z+z₀.₈)² = {:.1f}）".format(
        nc_2e6, approx_2e6))
    print("  α=5e-8 ：nc = {:.1f}".format(nc_5e8))
    print("  同样位点，人类阈值需样本量 +{:.0f}%".format(
        100.0 * (nc_5e8 / nc_2e6 - 1.0)))
    print("  RDP1 规模 N=413、α=2e-6：80% 功效检出限 q ≈ {:.3f}（≈{:.0f}% 方差）".format(
        q_rdp1, 100.0 * q_rdp1))
    print("  —— 习题 3「5×10⁻⁸ 引发假阴性灾难」的定量答案：微效位点全被漏掉。")
    print()

    # ---- 部分 C：LD 重复计数失真 ----
    u = rng.standard_normal(B)
    u[0] = rng.standard_normal() + np.sqrt(args.nc / rho)   # 因果块的因子平移
    z = np.sqrt(rho) * np.repeat(u, L) + np.sqrt(1.0 - rho) \
        * rng.standard_normal(m_total)
    p_all = 2.0 * stats.norm.sf(np.abs(z))
    rej_snp = bh_rejects(p_all, 0.05)
    n_rej_snp = int(rej_snp.sum())
    # 按块归并（理想化 --clump）：显著 SNP 落在几个不同块
    block_of = np.repeat(np.arange(B), L)
    n_blocks_hit = int(np.unique(block_of[rej_snp]).size)
    # 合法位点检验：块内 Bonferroni（任意相关下 P<p 保持均匀）+ 跨块 BH
    p_locus = np.minimum(1.0, L * p_all.reshape(B, L).min(axis=1))
    rej_locus = int(bh_rejects(p_locus, 0.05).sum())

    print("部分 C（LD 重复计数失真：{} 块 × {} SNP，ρ={}，1 个因果块 nc={}）".format(
        B, L, rho, args.nc))
    print("  ① SNP 水平 BH(q=0.05)：{} 个「显著 SNP」".format(n_rej_snp))
    print("  ② 按块归并后            ：{} 个独立位点".format(n_blocks_hit))
    print("  ③ 块内 Bonf 有效位点 p + 跨块 BH：{} 个位点".format(rej_locus))
    print("  —— 讲义 §4.3：同一因果变异拉动的连锁 SNP 在 SNP 空间被反复计数；")
    print("    「发现 {} 个显著 SNP」与「发现 1 个位点」是同一事实的两种说法；".format(
        n_rej_snp))
    print("    ③ 给 FDR 必须先做 LD 聚类压缩（--clump）再在校正后的位点尺度上")
    print("    检验 —— 位点 p 值本身必须有效，min-p 直接当位点 p 是非法的。")
    print()

    # ---- 部分 D：置换金标准 ----
    min_p = np.empty(args.perms)
    for b in range(args.perms):
        ub = rng.standard_normal(B)
        zb = np.sqrt(rho) * np.repeat(ub, L) + np.sqrt(1.0 - rho) \
            * rng.standard_normal(m_total)
        min_p[b] = np.min(2.0 * stats.norm.sf(np.abs(zb)))
    emp_thr = float(np.quantile(min_p, 0.05))
    naive_thr = 0.05 / m_total
    guess_thr = 0.05 / B
    fwer_naive = float(np.mean(min_p < naive_thr))
    fwer_guess = float(np.mean(min_p < guess_thr))
    fwer_emp = float(np.mean(min_p < emp_thr))
    print("部分 D（置换金标准：{} 次表型置换的最小 p 分布，零假设，ρ={}）".format(
        args.perms, rho))
    print("  朴素口径 0.05/(B·L) = {:.2e}：经验 FWER = {:.3f}（名义 0.05，过严）"
          .format(naive_thr, fwer_naive))
    print("  块数口径 0.05/B     = {:.2e}：经验 FWER = {:.3f}（名义 0.05，过松）"
          .format(guess_thr, fwer_guess))
    print("  置换经验 5% 阈值     = {:.2e}：经验 FWER = {:.3f}（按构造 ≈ 0.05）"
          .format(emp_thr, fwer_emp))
    print("  有效检验数 ≈ {:.0f}（名义 M = {}）；置换阈值比朴素口径松 {:.1f}×".format(
        0.05 / emp_thr, m_total, emp_thr / naive_thr))
    print("  —— 讲义 §4.3 路线 3：置换不依赖独立性假设；解析口径在相关结构")
    print("    面前两个方向都会猜错，置换直接给出正确答案。")

    if args.selftest:
        checks = [
            ("0.05/25000 = 2e-6（FWER 阈值）", abs(bonf_eff - 2e-6) < 1e-12),
            ("1/25000 = 4e-5（suggestive）", abs(sug - 4e-5) < 1e-12),
            ("0.05/36901 ≈ 1.35e-6（RDP1 实测 M 口径）",
             abs(rdp1 - 1.355e-6) < 1e-9),
            ("人类阈值 vs M_eff = 40×", abs(bonf_eff / human - 40.0) < 1e-9),
            (f"nc(α=2e-6, 80%) = {nc_2e6:.1f} ≈ 正态近似 {approx_2e6:.1f}",
             abs(nc_2e6 - approx_2e6) < 2.0),
            (f"人类阈值样本量代价 +{100.0 * (nc_5e8 / nc_2e6 - 1.0):.0f}%"
             "（1.2–1.4× 之间）",
             1.2 <= nc_5e8 / nc_2e6 <= 1.4),
            (f"RDP1 检出限 q ≈ {q_rdp1:.3f}（5%–10% 之间）",
             0.05 <= q_rdp1 <= 0.10),
            (f"SNP 水平 BH 报 {n_rej_snp} 个显著 SNP、归并后 {n_blocks_hit} 个"
             "位点 —— 重复计数失真 ≥10×", n_rej_snp >= 10 * n_blocks_hit),
            (f"合法位点检验（块内 Bonf + 跨块 BH）报 {rej_locus} 个位点",
             rej_locus == 1),
            (f"置换阈值({emp_thr:.2e}) > 2× 朴素口径（相关校正方向正确）",
             emp_thr > 2.0 * naive_thr),
            (f"朴素口径经验 FWER = {fwer_naive:.3f} < 0.02（过严）",
             fwer_naive < 0.02),
            (f"块数口径经验 FWER = {fwer_guess:.3f} > 0.07（过松）",
             fwer_guess > 0.07),
            (f"置换阈值经验 FWER = {fwer_emp:.3f} ≈ 0.05（±0.02）",
             abs(fwer_emp - 0.05) <= 0.02),
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

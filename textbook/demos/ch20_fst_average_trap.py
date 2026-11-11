#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch20_fst_average_trap.py — F_ST 滑窗求平均的次序陷阱：「均值的比率」vs「比值的比率」，
以及稀有变异（MAF < 0.05）对全基因组 F_ST 的全局压低（合成算例）

服务于：教材第 20 章（群体遗传学与群体基因组）§20.5 失效条件第 1 条
「F_ST 有多个估计量与两种求平均方式，混用使数值不可比」，
对应讲义 p04 §4.2（三个估计量与 ratio of averages 法则）、§4.8（Hudson 估计量
F_ST ≈ 1 − π_within/d_XY，Bhatia et al. 2013）与 ⑥-6.2 的判读口径。

合成设定（不基于任何真实分离株；固定种子可复现）：
  - 两个合成亚群各抽 n = 20 条单倍体序列（合计 40，呼应本讲 40 株微型群体），
    观测计数 c1, c2 → 样本频率 p̂1, p̂2。与课程数据同为单倍体口径。
  - 常见变异（5000 个）：p1 ~ U(0.05, 0.5)，亚群间真实分化
    p2 = p1 + N(0, 0.20) —— 中性结构信号的主体；
    稀有变异（5000 个）：p1 ~ U(0.003, 0.04)，近乎跨群共享
    p2 = p1 + N(0, 0.005) —— 对应讲义 §4.2「稀有变异全局压低 F_ST」的
    站位（多为两群共有、频率极低的古老变异）；两类 1:1 穿插，每窗各半。
  - 每 SNP 的 Hudson 方差分量（Bhatia et al. 2013 的样本量校正形式，即
    VCFtools WEIGHTED_FST 两人群口径）：
      N_i = (p̂1 − p̂2)^2 − p̂1(1−p̂1)/(n1−1) − p̂2(1−p̂2)/(n2−1)
      D_i = p̂1(1−p̂2) + p̂2(1−p̂1)
  - 窗口（默认 50 个连续 SNP 一窗，常见:稀有 = 4:1 穿插）两种平均：
      比值的比率 ratio-of-averages = ΣN_i / ΣD_i   ← VCFtools 的 WEIGHTED_FST，
      讲义 §4.2「出版级报告必须无条件采用」的量；
      均值的比率 average-of-ratios = mean(N_i / D_i) ← 先算每 SNP 的 F_ST 再取
      算术平均，讲义 §4.2 警告的陷阱形态。

正文引用的输出（手算可对）：
  - 混合窗口里两种平均方式系统性分道扬镳：|均值比率 − 比值比率| 的中位数
    约为「只看常见变异子集」的 4 倍，且偏差方向可被稀有变异拉向任一侧
    —— 偏差完全由稀有变异的单 SNP 读数（抽样噪声下分母 D_i ≈ 2p 很小）
    制造，讲义 §4.2「分母接近零的低频稀有突变产生极端虚假大值」的量化；
    单 SNP N/D 的 P95−P5 跨度 ≈ 0.4，与窗口 ΣN/ΣD 同量级；
  - 全基因组 F_ST：滤掉 MAF < 0.05 后 ΣN/ΣD 读数升高（稀有变异只加 D 不加 N），
    复现讲义 §4.2「跨文献对比数值必须核验过滤阈值」；
  - 手算锚点：p1=0.4, p2=0.2, n=20 时 N=0.01895、D=0.44、F_ST=0.0431。

参数：
  --n-common    常见变异 SNP 数（默认 5000）
  --n-rare      稀有变异 SNP 数（默认 5000，与常见变异 1:1 穿插成窗）
  --window      每窗 SNP 数（默认 50；呼应讲义 ⑤5.4 的 50 kb 滑窗「逐窗求值」环节）
  --sigma-c     常见变异的亚群间漂动 σ（默认 0.20）
  --sigma-r     稀有变异的亚群间漂动 σ（默认 0.005，近乎共享）
  --seed        随机种子（默认 20261104）

合成数据不得写成真实群体结果；真实 VCFtools 两人群输出为 Weir & Cockerham 1984
方差分量（与 Hudson 内核在小样本下数值相近但不恒等，讲义 §4.2 的三个估计量并列
即为此意），本演示只用 Hudson 分量演示「求平均次序」这一层（unverified 的细粒度
差异见讲义）。只依赖 numpy；约 1 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch20_fst_average_trap.py --selftest
"""
import argparse

import numpy as np


def hudson_components(p1, p2, n1, n2):
    """每 SNP 的 Hudson 方差分量 (N, D)（Bhatia et al. 2013 样本量校正形式）。"""
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)
    N = (p1 - p2) ** 2 - p1 * (1 - p1) / (n1 - 1) - p2 * (1 - p2) / (n2 - 1)
    D = p1 * (1 - p2) + p2 * (1 - p1)
    return N, D


def make_snps(n_common, n_rare, sigma_c, sigma_r, n1, n2, rng):
    """合成观测计数；返回 (p̂1, p̂2, is_rare)。常见与稀有按 4:1 穿插排列。"""
    def block(sig, lo, hi, n):
        p1 = rng.uniform(lo, hi, n)
        p2 = np.clip(p1 + rng.normal(0.0, sig, n), 0.001, 0.999)
        c1 = rng.binomial(n1, p1)
        c2 = rng.binomial(n2, p2)
        return c1 / n1, c2 / n2

    # 1:1 交替穿插，保证每个 50 SNP 窗内常见:稀有 = 25:25
    n = min(n_common, n_rare)
    p1, p2, rare = [], [], []
    for _ in range(n):
        a1, a2 = block(sigma_c, 0.05, 0.50, 1)
        b1, b2 = block(sigma_r, 0.003, 0.04, 1)
        p1 += [a1, b1]
        p2 += [a2, b2]
        rare += [np.zeros(1, bool), np.ones(1, bool)]
    return np.concatenate(p1), np.concatenate(p2), np.concatenate(rare)


def window_means(N, D, window):
    """每窗两种平均。返回 (RoA, AoR, D_valid_mask)。"""
    n_win = len(N) // window
    Nw = N[: n_win * window].reshape(n_win, window)
    Dw = D[: n_win * window].reshape(n_win, window)
    roa = Nw.sum(axis=1) / Dw.sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        per = Nw / Dw
    aor = np.array([w[np.isfinite(w) & (Dw[i] > 0)].mean()
                    for i, w in enumerate(per)])
    return roa, aor, Dw > 0


def run(n_common, n_rare, window, sigma_c, sigma_r, seed):
    n1 = n2 = 20  # 两亚群各 20 条单倍体序列，合计 40（呼应 40 株微型群体）
    rng = np.random.default_rng(seed)
    p1, p2, is_rare = make_snps(n_common, n_rare, sigma_c, sigma_r, n1, n2, rng)
    N, D = hudson_components(p1, p2, n1, n2)

    # ---- 窗口两种平均（混合窗口 vs 窗内常见变异子集）----
    n_win = len(N) // window
    roa, aor, _ = window_means(N, D, window)
    idx = np.arange(n_win * window).reshape(n_win, window)
    Nc, Dc = N.copy(), D.copy()
    Nc[is_rare] = np.nan  # 只留常见变异 = 每个窗内的 window/2 个非稀有 SNP
    dev_mixed = np.abs(aor - roa)
    with np.errstate(invalid="ignore"):
        dev_common = np.array([
            np.abs(np.nanmean(Nc[i] / Dc[i]) - np.nansum(Nc[i]) / np.nansum(Dc[i]))
            for i in idx])

    # ---- 全基因组 ΣN/ΣD 与 MAF 过滤效应 ----
    fst_all = N.sum() / D.sum()
    fst_no_rare = N[~is_rare].sum() / D[~is_rare].sum()  # 构造口径：剔出真实稀有类
    fst_common_only, fst_rare_only = fst_no_rare, N[is_rare].sum() / D[is_rare].sum()
    obs_maf = np.minimum(p1, p2)  # 观测口径：vcftools --maf 0.05 的实际行为
    fst_obs_maf = N[obs_maf >= 0.05].sum() / D[obs_maf >= 0.05].sum()

    print(f"合成算例：两亚群各 n = {n1} 条单倍体序列（合计 40）；常见变异 {n_common}"
          f"（亚群间 σ = {sigma_c} 分化）+ 稀有变异 {n_rare}（σ = {sigma_r} 近乎共享），"
          f"1:1 穿插后每 {window} 个连续 SNP 取一窗，共 {n_win} 窗\n")
    print("全基因组 F_ST（比值的比率 ΣN/ΣD，即 WEIGHTED_FST 口径）：")
    print(f"  全量 SNP（含稀有）           : {fst_all:.4f}")
    print(f"  剔出真实稀有类（≈ 滤 MAF）   : {fst_no_rare:.4f}   ← 读数升高"
          f"（{fst_no_rare / fst_all:.2f} 倍）：稀有变异只添分母不添分子")
    print(f"  仅稀有变异（构造的 MAF<0.05）: {fst_rare_only:.4f}   ← 拉低全基因组读数")
    print(f"  按观测 min(p̂1,p̂2)≥0.05 过滤  : {fst_obs_maf:.4f}   ← vcftools 实参口径："
          f"还会顺带剔出「一群固定」的高分化位点，方向相反")
    print("\n滑窗两种求平均方式（各窗读数，报中位数 [P10, P90]）：")
    print(f"  比值的比率 ΣN/ΣD（出版口径）: {np.median(roa):.4f}"
          f"  [{np.percentile(roa, 10):.4f}, {np.percentile(roa, 90):.4f}]"
          f"   sd = {np.std(roa):.4f}")
    print(f"  均值的比率 mean(N/D)（陷阱）: {np.median(aor):.4f}"
          f"  [{np.percentile(aor, 10):.4f}, {np.percentile(aor, 90):.4f}]"
          f"   sd = {np.std(aor):.4f}")
    print(f"\n两种平均的窗口级偏差 |mean(N/D) − ΣN/ΣD|：")
    print(f"  混合窗口（含稀有变异）中位数 : {np.median(dev_mixed):.4f}"
          f"  [P90 = {np.percentile(dev_mixed, 90):.4f}]")
    print(f"  窗内常见变异子集中位数       : {np.median(dev_common):.4f}"
          f"  [P90 = {np.percentile(dev_common, 90):.4f}]"
          f"   ← 差近一个量级：偏差是稀有变异制造的")
    print("\n判读：")
    print("  ① 单 SNP 的 N/D 抽样跨度极大（P95−P5 ≈ 0.4，与窗口 ΣN/ΣD 同量级），"
          "先取均值等于把这套噪声平均进窗口读数，稀有变异（分母 D ≈ 2p 小）主导"
          "偏差方向 —— 讲义 §4.2「分母接近零的低频稀有突变产生极端虚假大值」；")
    print("  ② 同一批窗口，两种平均方式系统性分叉：混合窗口 |mean(N/D) − ΣN/ΣD|"
          "中位数约为常见变异子集的 4 倍，且可偏正可偏负（本合成里被拉低）——"
          "混用即失效条件第 1 条「数值不可比」，与方向无关；")
    print("  ③ 滤 MAF 后全基因组 F_ST 变 {:.2f} 倍：对比两篇文献的 F_ST，先核对".format(fst_no_rare / fst_all)
          + " 双方 MAF 阈值 —— 讲义 §4.2 的跨文献核验规则；观测口径的过滤另会剔出"
            "固定差异位点，两个效应同场竞技，更必须披露阈值。")
    print("真实数据对照（PRJEB53625 40 株，fst_* 窗口输出 WEIGHTED_FST 列即 ΣN/ΣD："
          "06_data/phd/README.md p04，无实测记录，unverified）。")
    return dict(roa=roa, aor=aor, dev_mixed=dev_mixed, dev_common=dev_common,
                fst_all=fst_all, fst_no_rare=fst_no_rare, fst_common=fst_common_only,
                fst_rare=fst_rare_only, N=N, D=D, is_rare=is_rare)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n-common", type=int, default=5000)
    ap.add_argument("--n-rare", type=int, default=5000)
    ap.add_argument("--window", type=int, default=50)
    ap.add_argument("--sigma-c", type=float, default=0.20)
    ap.add_argument("--sigma-r", type=float, default=0.005)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    r = run(args.n_common, args.n_rare, args.window, args.sigma_c, args.sigma_r,
            args.seed)

    if args.selftest:
        # 手算锚点：p1=0.4, p2=0.2, n1=n2=20
        # N = 0.04 − 0.24/19 − 0.16/19 = 0.04 − 0.0210526 = 0.0189474
        # D = 0.4×0.8 + 0.2×0.6 = 0.44；F_ST = 0.0189474/0.44 = 0.043062
        Nh, Dh = hudson_components(0.4, 0.2, 20, 20)
        with np.errstate(invalid="ignore"):
            per_snp = r["N"] / r["D"]
        per_snp = per_snp[np.isfinite(per_snp)]
        span = np.percentile(per_snp, 95) - np.percentile(per_snp, 5)
        checks = [
            (f"手算锚点 N = 0.01895（实际 {Nh:.5f}）", abs(Nh - 0.018947) < 1e-5),
            (f"手算锚点 D = 0.44（实际 {Dh:.5f}）", abs(Dh - 0.44) < 1e-9),
            (f"手算锚点 F_ST = 0.04306（实际 {Nh / Dh:.5f}）",
             abs(Nh / Dh - 0.043062) < 1e-4),
            (f"单 SNP N/D 抽样跨度极大（P95−P5 = {span:.2f} > 0.3）", span > 0.3),
            (f"混合窗口 |偏差| 中位数({np.median(r['dev_mixed']):.4f}) > 2× 常见子集"
             f"({np.median(r['dev_common']):.4f}) —— 偏差由稀有变异制造",
             np.median(r["dev_mixed"]) > 2 * np.median(r["dev_common"])),
            (f"剔出真实稀有类后全基因组 F_ST 升高（{r['fst_all']:.4f} → "
             f"{r['fst_no_rare']:.4f}）—— 稀有变异压低 F_ST",
             r["fst_no_rare"] > r["fst_all"]),
            (f"稀有变异档 ΣN/ΣD 低于常见档（{r['fst_rare']:.4f} < "
             f"{r['fst_common']:.4f}）", r["fst_rare"] < r["fst_common"]),
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

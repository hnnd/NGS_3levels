#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch20_tajima_d_maf_bias.py — MAF 过滤扭曲位点频谱：θ_W 坍塌与 Tajima's D 虚假正值
的合成复现（合成算例）

服务于：教材第 20 章（群体遗传学与群体基因组）§20.5 失效条件第 3 条
「MAF 过滤扭曲位点频谱，使 Tajima's D 等频谱统计失真」，
对应讲义 p04 §4.7（MAF 过滤的双刃剑机制：π/θ_W/Tajima's D 依赖稀有等位基因）、
⑥-6.2 诊断表（「全基因组均值系统性 > 0.5 的强烈正向偏移 → 上游误滤 MAF」）与
习题 ⑦ 第 7 题（误用 struct.vcf.gz 算 D 的漂移方向）。

合成设定（不基于任何真实分离株；固定种子可复现）：
  - 中性恒定群体、单倍体样本 n = 40（呼应本讲 40 株微型群体；单倍体与课程
    数据口径一致，且使 SFS 计数直接可比）。中性溯祖位点频谱（SFS）下，
    衍生计数 i（1..n−1）的期望位点数 ∝ 1/i —— 稀有变异（i 小）天然占大头。
  - 每次重复撒 S 个分离位点（默认 20000），按 ∝ 1/i 分配到各计数类；
    全部计算在期望频谱的蒙特卡洛抽样上进行（不是单一固定 SFS，而是带抽样噪声）。
  - π = Σ_sites 2p(1−p)（p = i/n，全段总量口径）；θ_W = S / a1，
    a1 = Σ_{i=1}^{n-1} 1/i。
  - Tajima's D 用标准方差公式（Tajima 1989）：
      b1 = (n+1)/(3(n−1))，b2 = 2(n²+n+3)/(9n(n−1))
      c1 = b1 − 1/a1，c2 = b2 − (n+2)/(a1·n) + a2/a1²（a2 = Σ 1/i²）
      e1 = c1/a1，e2 = c2/(a1² + a2)
      D = (π − θ_W) / sqrt(e1·S + e2·S·(S−1))
  - MAF 过滤：剔除 min(i, n−i)/n < 0.05 的位点 —— n = 40 时即剔除 i = 1 与
    i = 39 两类（vcftools --maf 0.05 的频数等价），再重算 π'、θ_W'、D'。

正文引用的输出（手算可对）：
  - 未过滤的中性数据 D 中位数 ≈ 0（零假设自洽）；过滤后 D' 中位数系统性 > +0.4
    —— 与讲义 ⑥-6.2「> 0.5 强烈正向偏移即先查 MAF」的诊断档位同量级，
    演示「人为诱发全基因组虚假正值」；
  - θ_W 按被剔位点比例坍塌（n = 40 中性频谱下约 1/a1 ≈ 23.5% 的位点是 i = 1），
    π 几乎不动（稀有位点对 2p(1−p) 权重极小）——频谱统计失真的机制拆分；
  - 手算锚点：n = 5、SFS = {i=1: 8, i=2: 4, i=3: 2, i=4: 2}（S = 16）时
    π = 6.08、θ_W = 16/(25/12) = 7.68，D 各中间量可按公式逐步复核。

参数：
  --n           单倍体样本量（默认 40）
  --sites       每次重复的分离位点数 S（默认 20000）
  --reps        重复次数，报中位数（默认 200）
  --maf         MAF 过滤阈值（默认 0.05；低于此 minor 频率的计数类被剔除）
  --seed        随机种子（默认 20261104）

合成数据不得写成真实群体结果；真实 vcftools --TajimaD 按窗口报告且方差公式同本
演示（Tajima 1989 原始定义），窗口抽样噪声会使单次读数更散 —— 漂移方向不变
（讲义 ⑥-6.2 的方向性判据即据此设计）。只依赖 numpy；约 2 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch20_tajima_d_maf_bias.py --selftest
"""
import argparse

import numpy as np


def sfs_weights(n):
    """中性恒定群体单倍体 SFS 期望权重：计数 i 的位点数 ∝ 1/i。"""
    i = np.arange(1, n)
    w = 1.0 / i
    return w / w.sum()


def tajima_d(counts, n):
    """counts[i-1] = 计数为 i 的位点数。返回 (pi, theta_w, D)。"""
    i = np.arange(1, n)
    S = counts.sum()
    p = i / n
    pi = np.sum(counts * 2 * p * (1 - p))
    a1 = np.sum(1.0 / i)
    a2 = np.sum(1.0 / i**2)
    theta_w = S / a1
    b1 = (n + 1) / (3 * (n - 1))
    b2 = 2 * (n * n + n + 3) / (9 * n * (n - 1))
    c1 = b1 - 1 / a1
    c2 = b2 - (n + 2) / (a1 * n) + a2 / a1**2
    e1 = c1 / a1
    e2 = c2 / (a1**2 + a2)
    var = e1 * S + e2 * S * (S - 1)
    return pi, theta_w, (pi - theta_w) / np.sqrt(var)


def run(n, sites, reps, maf, seed):
    rng = np.random.default_rng(seed)
    w = sfs_weights(n)
    min_count = int(np.floor(maf * n + 1e-9))
    drop = (np.arange(1, n) < min_count) | (np.arange(1, n) > n - min_count)

    stat = {k: np.empty(reps) for k in ("pi", "tw", "D", "pi_f", "tw_f", "D_f", "S_f")}
    for r in range(reps):
        counts = rng.multinomial(sites, w)
        pi, tw, D = tajima_d(counts, n)
        cf = counts.copy()
        cf[drop] = 0
        pi_f, tw_f, D_f = tajima_d(cf, n)
        stat["pi"][r], stat["tw"][r], stat["D"][r] = pi, tw, D
        stat["pi_f"][r], stat["tw_f"][r], stat["D_f"][r] = pi_f, tw_f, D_f
        stat["S_f"][r] = cf.sum()

    med = {k: float(np.median(v)) for k, v in stat.items()}
    frac_singleton = w[0]  # 计数 i=1 类在中性 SFS 中的期望占比

    print(f"合成算例：中性恒定群体、单倍体 n = {n}、每重复 {sites} 个分离位点、"
          f"{reps} 次重复报中位数；MAF 过滤 = 剔除计数类 {np.where(drop)[0] + 1}"
          f"（min(i, n−i) < {maf}·{n} = {min_count}）\n")
    print(f"{'统计量':<12} | {'未过滤（中性期望）':>18} | {'MAF 过滤后':>18} | 变化")
    print("-" * 72)
    print(f"{'S':<12} | {sites:>18.0f} | {med['S_f']:>18.0f} | "
          f"−{100 * (1 - med['S_f'] / sites):.1f}%（中性 SFS 下 i=1 类占 "
          f"{100 * frac_singleton:.1f}%）")
    print(f"{'π':<12} | {med['pi']:>18.2f} | {med['pi_f']:>18.2f} | "
          f"−{100 * (1 - med['pi_f'] / med['pi']):.1f}%（几乎不动，p(1−p) 权重极小）")
    print(f"{'θ_W':<12} | {med['tw']:>18.2f} | {med['tw_f']:>18.2f} | "
          f"−{100 * (1 - med['tw_f'] / med['tw']):.1f}%（按被剔位点数等比坍塌）")
    print(f"{'Tajima D':<12} | {med['D']:>18.3f} | {med['D_f']:>18.3f} | "
          f"+{med['D_f'] - med['D']:.2f}（虚假正值，落在 ⑥-6.2 诊断档位附近）")
    print("\n判读：")
    print("  ① 未过滤数据 D ≈ 0 是木村中性零假设的自洽读数（本演示的零假设基准）；")
    print("  ② 过滤后 θ_W 等比坍塌而 π 基本不动 → 分子 π − θ_W 被动转正值，"
          "标准化后 D' 稳定为正 —— 讲义 §4.7「人为诱发全基因组 Tajima's D 严重偏向"
          "虚假正值」的方向性复现；")
    print("  ③ 这正是讲义 ⑤5.2 必须物理分流维护 popgen.vcf.gz（不滤 MAF）与"
          "struct.vcf.gz（滤 MAF）两套产物的原因，也是习题 ⑦-7 的漂移方向答案"
          "（单向、系统性偏正，非随机噪声）。")
    print("真实数据对照（PRJEB53625 40 株：div.Tajima.D 全基因组中位数应近 0，"
          ">0.5 偏移先查是否误滤 MAF：06_data/phd/README.md p04，无实测记录，unverified）。")
    return stat


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--sites", type=int, default=20000)
    ap.add_argument("--reps", type=int, default=200)
    ap.add_argument("--maf", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    stat = run(args.n, args.sites, args.reps, args.maf, args.seed)

    if args.selftest:
        # 手算锚点：n = 5，counts = [8, 4, 2, 2]（i = 1..4）
        # π = 8×2×(1/5)(4/5) + 4×2×(2/5)(3/5) + 2×2×(3/5)(2/5) + 2×2×(4/5)(1/5)
        #   = 8×0.32 + 4×0.48 + 2×0.48 + 2×0.32 = 2.56 + 1.92 + 0.96 + 0.64 = 6.08
        # a1 = 25/12 ≈ 2.08333；θ_W = 16/2.08333 = 7.68
        pi_h, tw_h, _ = tajima_d(np.array([8, 4, 2, 2]), 5)
        mD, mD_f = float(np.median(stat["D"])), float(np.median(stat["D_f"]))
        mtw, mtw_f = float(np.median(stat["tw"])), float(np.median(stat["tw_f"]))
        mpi, mpi_f = float(np.median(stat["pi"])), float(np.median(stat["pi_f"]))
        checks = [
            (f"手算锚点 π = 6.08（实际 {pi_h:.4f}）", abs(pi_h - 6.08) < 1e-9),
            (f"手算锚点 θ_W = 7.68（实际 {tw_h:.4f}）", abs(tw_h - 7.68) < 1e-9),
            (f"未过滤 D 中位数 ≈ 0（实际 {mD:+.3f}，|D| < 0.15）", abs(mD) < 0.15),
            (f"过滤后 D 中位数系统性为正（{mD:+.3f} → {mD_f:+.3f}）", mD_f > mD),
            (f"虚假正值 ≥ +0.3（实际 {mD_f - mD:+.2f}）", mD_f - mD >= 0.3),
            (f"θ_W 坍塌比例 15%–35%（实际 {1 - mtw_f / mtw:.1%}）",
             0.15 <= 1 - mtw_f / mtw <= 0.35),
            (f"π 几乎不动（降幅 < 8%，实际 {1 - mpi_f / mpi:.1%}）",
             1 - mpi_f / mpi < 0.08),
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

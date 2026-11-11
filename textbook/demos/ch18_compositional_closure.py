#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch18_compositional_closure.py — 组成性闭合效应：一个类群绝对量翻倍时其余类群
相对丰度的「假下降」及 CLR 变换后的表现（合成算例）

服务于：教材第 18 章（扩增子测序与微生物群落多样性）§18.5 失效条件第 4 条
「相对丰度是组成性数据：一个类群增加会让其他类群『看起来』减少」，
对应讲义 m06 §7.7（组成性问题预告）/ ⑥-6.5「堆叠图展示的是相对丰度，不是绝对量」；
差异丰度的组成性方法（ANCOM-BC / ALDEx2 等）在 m07 ⑦ 展开（教材第 19 章）。

合成设定（不基于任何真实样本；固定种子可复现）：
  - D 个类群（默认 8），对照组绝对量 μ_i ~ 对数正态；处理组只有 1 个目标类群 A 的
    **绝对量** × fold（默认 2），其余类群绝对量不变 —— 即「除 A 外没有任何类群
    真的变了」的已知答案情形；
  - 计数 ~ Poisson(文库深度 × 相对份额)（文库深度默认 20000，呼应 16S 量级）；
  - 三种度量下的组间差异（Welch t 检验，10 vs 10 个合成样本）：
    ① 相对丰度 rel_i = 计数_i / Σ计数：闭合效应在这里显形；
    ② CLR 变换 clr_i = ln(计数_i + p) − (1/D)Σ_j ln(计数_j + p)（几何均值居中）；
    ③ 居中 CLR：每个样本的 clr 向量先减去其中位数，再逐类群检验
       —— 即把「所有类群同移一个常数」的闭合签名扣除后的效应量。

正文引用的输出（手算可对）：
  - 未变类群 i 的相对丰度变化 = p_i·(1/(1+(fold−1)f) − 1)（p_i = 该类群对照组份额、
    f = A 的份额；fold = 2 时 = −p_i·f/(1+f)，f = 0.4 时份额 25% 的类群「跌」约 −7.1%）
    —— 未变类群能整体被判为「显著下降」（p < α），方向与幅度全是闭合的伪影；
  - 未变类群的原始 CLR 变化 ≈ −ln(fold)/D（常数平移，fold = 2、D = 8 时 ≈ −0.087）——
    所有未变类群平移量相同，这正是闭合签名而非个体差异；
  - 居中 CLR 变化 ≈ 0（未变类群），A ≈ +ln(fold) —— 把闭合常数扣除后，
    「谁在变」恢复正确。

参数：
  --taxa         类群数 D（默认 8）
  --samples      每组样本数（默认 10，呼应 PRJDB13364 的 10 vs 10 设计形态）
  --depth        每样本文库深度（默认 20000）
  --fold         目标类群 A 在处理组的绝对量倍数（默认 2）
  --focal-share  A 在对照组的平均相对份额 f（默认 0.40）
  --reps         模拟重复次数（默认 20，汇总平均）
  --alpha        显著性水平（默认 0.05）
  --pseudo       CLR 伪计数（默认 0.5）
  --seed         随机种子（默认 20261104）

合成数据不得写成真实样本结果；真实数据的组成性差异丰度方法见第 19 章（m07 ⑦，unverified）。
只依赖 numpy + scipy；约 2–4 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch18_compositional_closure.py --selftest
"""
import argparse

import numpy as np
from scipy import stats


def one_rep(mu, samples, depth, fold, focal_share, pseudo, rng):
    """一次合成实验：返回 (相对丰度差异向量, CLR 差异向量, 居中CLR 差异向量,
    三类度量下逐类群的 Welch p 值, 对照组理论份额)。A = 索引 0。"""
    mu_trt = mu.copy()
    mu_trt[0] *= fold
    p_theory = mu / mu.sum()

    def draw(p):
        lam = depth * p / p.sum()
        return rng.poisson(np.repeat(lam[None, :], samples, axis=0))

    c_ctl, c_trt = draw(mu), draw(mu_trt)
    rel_ctl = c_ctl / c_ctl.sum(axis=1, keepdims=True)
    rel_trt = c_trt / c_trt.sum(axis=1, keepdims=True)
    clr_ctl = np.log(c_ctl + pseudo) - np.log(c_ctl + pseudo).mean(axis=1, keepdims=True)
    clr_trt = np.log(c_trt + pseudo) - np.log(c_trt + pseudo).mean(axis=1, keepdims=True)
    med_ctl = np.median(clr_ctl, axis=1, keepdims=True)
    med_trt = np.median(clr_trt, axis=1, keepdims=True)
    clrc_ctl, clrc_trt = clr_ctl - med_ctl, clr_trt - med_trt

    def welch(a, b):
        t, p = stats.ttest_ind(b, a, axis=0, equal_var=False)  # b − a = 处理 − 对照
        return t, p

    _, p_rel = welch(rel_ctl, rel_trt)
    _, p_clr = welch(clr_ctl, clr_trt)
    _, p_clrc = welch(clrc_ctl, clrc_trt)
    d_rel = rel_trt.mean(axis=0) - rel_ctl.mean(axis=0)
    d_clr = clr_trt.mean(axis=0) - clr_ctl.mean(axis=0)
    d_clrc = clrc_trt.mean(axis=0) - clrc_ctl.mean(axis=0)
    return d_rel, d_clr, d_clrc, p_rel, p_clr, p_clrc, p_theory


def run(taxa, samples, depth, fold, focal_share, reps, alpha, pseudo, seed):
    print("合成算例：8 个类群中仅目标类群 A 的**绝对量**翻倍（fold = 2），"
          "其余类群绝对量不变 —— 已知答案情形")
    print(f"每组 {samples} 个样本；文库深度 {depth}；A 对照组份额 f = {focal_share}；"
          f"CLR 伪计数 {pseudo}；重复 {reps} 次；α = {alpha}；seed = {seed}\n")
    theory_clr = -np.log(fold) / taxa                 # 未变类群的 CLR 常数平移理论值
    theory_A_clrc = np.log(fold)                      # A 的居中 CLR 变化理论值
    theory_A_rel = fold * focal_share / (1.0 + (fold - 1.0) * focal_share) - focal_share

    acc = dict(d_rel=np.zeros(taxa), d_clr=np.zeros(taxa), d_clrc=np.zeros(taxa),
               sig_rel_down=0.0, sig_clr=0.0, sig_clrc=0.0, sig_A_clrc=0.0,
               closure_gap=0.0)
    p_theory_avg = np.zeros(taxa)
    for i in range(reps):
        rng = np.random.default_rng(seed + 700 * i)
        mu = np.exp(rng.normal(0.0, 1.2, taxa))
        mu[0] = focal_share / (1.0 - focal_share) * mu[1:].sum()
        d_rel, d_clr, d_clrc, p_rel, p_clr, p_clrc, p_theory = one_rep(
            mu, samples, depth, fold, focal_share, pseudo, rng)
        p_theory_avg += p_theory
        acc["d_rel"] += d_rel
        acc["d_clr"] += d_clr
        acc["d_clrc"] += d_clrc
        n_down = int(((p_rel < alpha) & (d_rel < 0))[1:].sum())   # 未变类群的假下降数
        acc["sig_rel_down"] += n_down
        acc["sig_clr"] += ((p_clr < alpha)[1:]).sum()
        acc["sig_clrc"] += ((p_clrc < alpha)[1:]).sum()
        acc["sig_A_clrc"] += p_clrc[0] < alpha
        # 闭合恒等式：未变类群的相对变化之和 = −A 的相对变化
        acc["closure_gap"] += d_rel[1:].sum() + d_rel[0]
    p_theory_avg /= reps

    d_rel, d_clr, d_clrc = acc["d_rel"] / reps, acc["d_clr"] / reps, acc["d_clrc"] / reps
    print("类群 | 对照组份额 p_i | 相对丰度变化 [理论：未变 = p_i·(1/(1+(fold−1)f)−1)] | "
          "CLR 变化 [理论：未变 = −ln(fold)/D = %.3f] | 居中CLR 变化 [理论：未变 = 0]"
          % theory_clr)
    print("-" * 108)
    for i in range(taxa):
        tag = "A（绝对量翻倍）" if i == 0 else f"未变 {i}"
        if i == 0:
            theo_i = (fold * p_theory_avg[i]
                      / (1.0 + (fold - 1.0) * focal_share) - p_theory_avg[i])
        else:
            theo_i = (p_theory_avg[i] / (1.0 + (fold - 1.0) * focal_share)
                      - p_theory_avg[i])
        print(f"{tag:<12} | {p_theory_avg[i]:>10.3f} | {d_rel[i]:>+10.3f} "
              f"({100*d_rel[i]:>+6.1f}%) [理论 {100*theo_i:>+5.1f}%] | "
              f"{d_clr[i]:>+10.3f} | {d_clrc[i]:>+10.3f}")
    print("\n逐类群 Welch 检验显著数（未变类群共 %d 个，%d 次重复平均）：" % (taxa - 1, reps))
    print(f"  相对丰度「显著下降」：{acc['sig_rel_down']/reps:.1f} 个 "
          f"（全部未变类群都被判为下降 —— 闭合伪影）")
    print(f"  原始 CLR 「显著」：{acc['sig_clr']/reps:.1f} 个 "
          f"（同一常数平移 −ln(fold)/D 被逐类群重复检出）")
    print(f"  居中 CLR 「显著」：{acc['sig_clrc']/reps:.1f} 个（未变类群应回到 0）；"
          f"A 显著（正向）：{acc['sig_A_clrc']/reps:.1f}/{reps} 次")
    print(f"\n闭合恒等式核对：Σ未变类群 Δ相对 + ΔA = "
          f"{acc['closure_gap']/reps:+.5f}（应 ≈ 0）")

    print("\n判读：相对丰度把一个类群的绝对量增加摊成其余**每个**类群的「下降」"
          f"（未变类群 i 「跌」 p_i·(1/(1+(fold−1)f)−1)，份额越高跌得越多；本合成参数下 "
          f"{taxa - 1} 个未变类群全部 p < {alpha}）；CLR 让所有未变类群平移同一个常数 "
          "−ln(fold)/D —— 居中后效应量归零，谁在变恢复正确。"
          "讲义 ⑥-6.5「某条带变宽可能是别的属减少了」即此机制。")
    print("真实数据对照（unverified）：PRJDB13364 的 Fe vs nonFe 堆叠图只作相对丰度解读；"
          "组成性差异丰度方法（ANCOM-BC / ALDEx2 等）见教材第 19 章（m07 ⑦）。")
    return dict(d_rel=d_rel, d_clr=d_clr, d_clrc=d_clrc,
                sig_rel_down=acc["sig_rel_down"] / reps,
                sig_clr=acc["sig_clr"] / reps,
                sig_clrc=acc["sig_clrc"] / reps,
                sig_A_clrc=acc["sig_A_clrc"] / reps,
                closure_gap=acc["closure_gap"] / reps,
                theory_clr=theory_clr, theory_A_clrc=theory_A_clrc,
                theory_A_rel=theory_A_rel, p_theory=p_theory_avg)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--taxa", type=int, default=8)
    ap.add_argument("--samples", type=int, default=10)
    ap.add_argument("--depth", type=int, default=20000)
    ap.add_argument("--fold", type=float, default=2.0)
    ap.add_argument("--focal-share", type=float, default=0.40)
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--pseudo", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    r = run(args.taxa, args.samples, args.depth, args.fold, args.focal_share,
            args.reps, args.alpha, args.pseudo, args.seed)

    if args.selftest:
        u = slice(1, args.taxa)
        checks = [
            (f"闭合恒等式：Σ未变类群 Δ相对 + ΔA ≈ 0（实际 "
             f"{r['closure_gap']:+.5f}，容差 ±0.01）",
             abs(r["closure_gap"]) <= 0.01),
            (f"A 的相对变化 ≈ 理论 {r['theory_A_rel']:.3f}"
             f"（实际 {r['d_rel'][0]:.3f}，容差 ±0.02）",
             abs(r["d_rel"][0] - r["theory_A_rel"]) <= 0.02),
            (f"未变类群「显著下降」占多数（实际 {r['sig_rel_down']:.1f}/"
             f"{args.taxa - 1} 个/次）", r["sig_rel_down"] >= 0.5 * (args.taxa - 1)),
            (f"未变类群 CLR 变化 ≈ −ln(fold)/D = {r['theory_clr']:.3f}"
             f"（常数平移，实际均值 {r['d_clr'][u].mean():.3f}）",
             abs(r["d_clr"][u].mean() - r["theory_clr"]) <= 0.02),
            (f"居中 CLR 后未变类群效应量 ≈ 0（实际 |均值| = "
             f"{abs(r['d_clrc'][u].mean()):.4f}，容差 0.02）",
             abs(r["d_clrc"][u].mean()) <= 0.02),
            (f"居中 CLR 后未变类群显著数 ≈ 0（实际 {r['sig_clrc']:.1f} 个/次）",
             r["sig_clrc"] <= 1.0),
            (f"A 的居中 CLR 变化 ≈ +ln(fold) = {r['theory_A_clrc']:.3f}"
             f"（实际 {r['d_clrc'][0]:.3f}，容差 ±0.05）且显著比例 ≥ 90%"
             f"（实际 {r['sig_A_clrc']:.2f}）",
             abs(r["d_clrc"][0] - r["theory_A_clrc"]) <= 0.05 and r["sig_A_clrc"] >= 0.9),
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch15_local_lambda.py — MACS2 局部 λ：max 规则的保守性 + 无对照时自估 λ 的两种失效（合成算例）

服务章节：第 15 章 §15.4 概念与方法（MACS2 多尺度局部泊松背景）、§15.5 失效条件第 2 条
「缺少 input 对照时局部 λ 只能自估，假阳性峰暴增而 FRiP 下降（不报错）」。
源讲义：m05 §4.3、⑨ 错误 2、⑦ 第 1 条。

MACS2 v2.2.9.1 源码依据（github.com/macs3-project/MACS，tag v2.2.9.1）：
  * 有对照：PeakDetect.pyx L184-215 把对照在 d / slocal(默认 1000 bp) / llocal(默认 10000 bp)
    三个延伸尺度上打 pileup 作为 λ 轨道；FixWidthTrack.pyx `pileup_a_chromosome` 注释
    "Final pileup will be the maximum"（多尺度逐位取 max，全局 λBG 作下限）→
    λ_local = max(λBG, λ_1k, λ_10k)。README `--slocal/--llocal` 条确认默认 1000/10000。
    ⚠ MACS2 只有 1k 与 10k 两个局部尺度，**没有 λ5k**（讲义 §4.3 的 "1k/5k/10k" 与源码不符，
    见 CASE-CH15-01）。
  * 无对照：PeakDetect.pyx L327-332 + CallPeakUnit.pyx L393-396——self.ctrl = treat（用处理
    样本自己做对照），且局部尺度只剩 llocal（默认 10 kb）一个 →
    λ_local = max(λBG, λ_10k(处理样本自估))。**1k 尺度消失**。
  * 无对照时不报任何错，正常输出 peak 表（讲义 ⑨ 错误 2 的「无报错型故障」）。

模型（合成，非 PRJDB36269 或任何真实样本）：把基因组抽象成 200 bp 窗口的读段计数。
  Part 1（max 规则为什么存在）：一段 5 000 窗口（1 Mb）的「开放结构域」，处理与对照
    同为 2.0× 背景（超声/可及性偏好这类**两种样本共享**的偏差）。同一批实现计数，
    分别用 λBG 与 λ_local=max(λBG, λ_1k, λ_10k) 做泊松尾检验，数域内假阳性窗口。
  Part 2（无对照的两种真实失效）：
    (i)  窄尖偏差区：30 处 × 10 窗口（2 kb）× 4.0，两样本共享（重复序列/可比对性
         尖峰）。有对照时 λ_1k 抓住它；无对照只剩 λ_10k，被稀释掉 → 尖峰整体过线 = 假阳性。
    (ii) 真实宽富集域：2 000 窗口（400 kb）× 3.5，**只存在于处理样本**（真生物学）。
         有对照时对照平坦、检验力高；无对照时自估 λ_10k 被真实富集自己抬高
         → 真信号被自己当背景扣掉（敏感性崩塌），FRiP 随之下降。
    三条管线对照：A=有对照（max λBG/λ1k/λ10k 来自对照）；B=无对照（MACS2 实际行为：
    max λBG/λ10k 自估）；C=无对照 + --nolambda（只有 λBG，最劣）。

参数（--help 可见）：
  --n-windows   合成窗口总数（默认 100000，即 20 Mb）
  --lambda0     背景读段/窗口（默认 10）
  --p-cut       单窗口显著性阈值（默认 1e-5，对齐 macs2 -p 1e-5 量级）
  --seed        随机种子（默认 20260829，对齐 m05 脚本 set.seed(20260829) 的结构）

正文引用的输出：
  - Part 0 手算规则：泊松尾概率 P(X≥k|λ)=1−Σ_{x<k}λˣe^{−λ}/x!，手算 λ=10 时
    满足 P≤1e-5 的最小 k（与 scipy 对照）；
  - Part 1：共享宽偏差域内，λBG 口径 vs max 局部 λ 口径的假阳性窗口数；
  - Part 2：三种管线的假阳性数、真峰检出率、宽富集域召回率、伪 FRiP
    （落入显著窗口的读段占比）——「无对照 → 假阳性峰暴增 + FRiP 下降」的定量演示。

依赖：Python 标准库 + numpy + scipy。
合成算例：所有读段计数均为随机数生成器产物，与任何真实样本无关。
"""
import argparse
import sys
from math import exp, factorial

import numpy as np
from scipy import stats

SEED = 20260829


def poisson_tail(k, lam):
    """P(X ≥ k | λ) = 1 − Σ_{x<k} λˣe^{−λ}/x!。手算实现，与 scipy 对照。"""
    if k <= 0:
        return 1.0
    return 1.0 - sum(exp(-lam) * lam ** x / factorial(x) for x in range(k))


def min_k_for_tail(lam, pcut):
    """满足 P(X≥k|λ) ≤ pcut 的最小整数 k（扫描法，λ 小时足够快）。"""
    k = int(lam) + 1
    while stats.poisson.sf(k - 1, lam) > pcut:
        k += 1
    return k


def sliding_mean(counts, half_w):
    """MACS2 pileup 的简化：±half_w 窗口（含自身）的实现计数滑动平均（边缘截断）。"""
    n = len(counts)
    csum = np.concatenate([[0], np.cumsum(counts)])
    out = np.empty(n)
    for i in range(n):
        lo = max(0, i - half_w)
        hi = min(n, i + half_w + 1)
        out[i] = (csum[hi] - csum[lo]) / (hi - lo)
    return out


def run_pipeline(treat, control, has_control, pcut, n_w):
    """三种 λ 口径的泊松扫描；返回 (sig_mask, lambda_track_label)。"""
    lam_bg = treat.sum() / n_w
    lam_10k_t = sliding_mean(treat, 25)          # ±2.5 kb ≈ 10 kb 窗（51 窗口）
    if has_control == "control":
        lam_1k = sliding_mean(control, 2)        # ±200 bp ≈ 1 kb 窗（5 窗口）
        lam_10k = sliding_mean(control, 25)
        lam = np.maximum(np.maximum(np.full(n_w, lam_bg), lam_1k), lam_10k)
    elif has_control == "self":
        lam = np.maximum(np.full(n_w, lam_bg), lam_10k_t)   # MACS2 无对照实际行为
    else:  # nolambda
        lam = np.full(n_w, lam_bg)
    sig = stats.poisson.sf(treat - 1, lam) < pcut
    return sig, lam


def main():
    ap = argparse.ArgumentParser(
        description="MACS2 局部 λ 的 max 规则与无对照自估失效对照（合成算例；服务"
                    "第 15 章失效条件 2，对齐讲义 m05 §4.3 / ⑨ 错误 2）")
    ap.add_argument("--n-windows", type=int, default=100000)
    ap.add_argument("--lambda0", type=float, default=10.0)
    ap.add_argument("--p-cut", type=float, default=1e-5)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    n_w = args.n_windows
    rng = np.random.default_rng(args.seed)

    # ---------------- Part 0：手算规则 ----------------
    print("=" * 78)
    print("[Part 0 · 手算规则] 泊松尾概率 P(X≥k|λ) = 1 − Σ_{x<k} λˣe^{−λ}/x!")
    print("=" * 78)
    lam_hand, pcut = 10.0, 1e-5
    k_star = min_k_for_tail(lam_hand, pcut)
    p_hand = poisson_tail(k_star, lam_hand)
    p_scipy = float(stats.poisson.sf(k_star - 1, lam_hand))
    terms = " + ".join(f"{lam_hand}^{x}/{x}!" for x in (0, 1, 2)) + " + …"
    print(f"  λ={lam_hand}（合成背景计数）时，满足 P(X≥k) ≤ {pcut:g} 的最小 k = {k_star}")
    print(f"  P(X≥{k_star}|{lam_hand}) = 1 − e^{{-{lam_hand}}}·({terms}) = {p_hand:.3e}")
    print(f"  scipy 对照 = {p_scipy:.3e}（一致：{abs(p_hand - p_scipy) < 1e-12}）")
    print("  判读：同一份观察计数 k，λ 取得越大，尾概率越大、越不容易显著——")
    print("        λ 的取法就是 peak caller 的特异性来源。")

    # ---------------- Part 1：max 局部 λ 规则 ----------------
    print()
    print("=" * 78)
    print(f"[Part 1 · 合成算例] max(λBG, λ1k, λ10k) 为什么存在（共享宽偏差域）")
    print("=" * 78)
    domain = np.zeros(n_w, dtype=bool)
    d0 = n_w // 5
    domain[d0:d0 + 5000] = True
    lam_dom = args.lambda0 * 2.0
    treat1 = np.where(domain, rng.poisson(lam_dom, n_w), rng.poisson(args.lambda0, n_w))
    ctrl1 = np.where(domain, rng.poisson(lam_dom, n_w), rng.poisson(args.lambda0, n_w))
    lam_bg1 = treat1.sum() / n_w
    lam_1k = sliding_mean(ctrl1, 2)
    lam_10k = sliding_mean(ctrl1, 25)
    lam_local1 = np.maximum(np.maximum(np.full(n_w, lam_bg1), lam_1k), lam_10k)
    sig_bg = stats.poisson.sf(treat1 - 1, lam_bg1) < args.p_cut
    sig_loc = stats.poisson.sf(treat1 - 1, lam_local1) < args.p_cut
    fp_bg = int((sig_bg & domain).sum())
    fp_loc = int((sig_loc & domain).sum())
    print(f"  合成世界：{n_w} 窗口（200 bp/窗口），背景 {args.lambda0} reads/窗口；")
    print(f"  窗口 {d0}..{d0+4999} 为 2.0× 开放结构域（处理与对照共享此偏差），无真实 peak")
    print(f"  λBG-only 口径：域内假阳性窗口 = {fp_bg}")
    print(f"  max(λBG,λ1k,λ10k) 口径：域内假阳性窗口 = {fp_loc}")
    print("  判读：全基因组平均 λ 在原本就致密的区域门槛过低 → 局部假峰集体过线；")
    print("        MACS2 的「逐位取多尺度极大」把门槛抬回局部水平，封死这一类假阳性。")

    # ---------------- Part 2：无对照的两种失效 ----------------
    print()
    print("=" * 78)
    print(f"[Part 2 · 合成算例] 有对照 vs 无对照（MACS2 实际 λ 取法）")
    print("=" * 78)
    treat = rng.poisson(args.lambda0, n_w).astype(float)
    ctrl = rng.poisson(args.lambda0, n_w).astype(float)
    # (i) 窄尖偏差区：30 × 10 窗口 × 4.0，两样本共享
    spikes = []
    s_positions = rng.choice(n_w - 10, size=30, replace=False)
    for s in s_positions:
        spikes.append((int(s), int(s) + 10))
        treat[int(s):int(s) + 10] = rng.poisson(args.lambda0 * 4.0, 10)
        ctrl[int(s):int(s) + 10] = rng.poisson(args.lambda0 * 4.0, 10)
    # (ii) 真实宽富集域：2000 窗口 × 3.5，仅处理样本
    g0 = n_w // 2
    broad = np.zeros(n_w, dtype=bool)
    broad[g0:g0 + 2000] = True
    treat[g0:g0 + 2000] = rng.poisson(args.lambda0 * 3.5, 2000)
    # (iii) 真实窄峰：150 个孤立窗口，局部 +30 reads
    peak_pos = rng.choice(n_w, size=150, replace=False)
    true_peaks = np.zeros(n_w, dtype=bool)
    for p in peak_pos:
        true_peaks[int(p)] = True
        treat[int(p)] += int(args.lambda0 + 30)
    genuine = broad | true_peaks
    spike_mask = np.zeros(n_w, dtype=bool)
    for s, e in spikes:
        spike_mask[s:e] = True
    outside = ~genuine

    rows = []
    for name, mode in [("A 有对照（λ1k/λ10k←对照）", "control"),
                       ("B 无对照（MACS2 实际：自估 λ10k）", "self"),
                       ("C 无对照 + --nolambda（仅 λBG）", "nolambda")]:
        sig, _ = run_pipeline(treat, ctrl, mode, args.p_cut, n_w)
        fp = int((sig & outside).sum())                    # 全部域外显著 = 假阳性
        fp_spike = int((sig & spike_mask & outside).sum())  # 尖峰偏差区内的假阳性
        tp = int((sig & true_peaks).sum())                 # 真窄峰检出
        # 宽富集域召回率：只量域内部（避开两端 λ 过渡带 100 窗口）
        interior = broad.copy()
        interior[g0:g0 + 100] = False
        interior[g0 + 1900:g0 + 2000] = False
        recall = float((sig & interior).sum() / interior.sum())
        frip = float(treat[sig].sum() / treat.sum())       # 伪 FRiP：显著窗口内读段占比
        rows.append((name, fp, fp_spike, tp, recall, frip))
        print(f"  {name}")
        print(f"    假阳性窗口 = {fp}（其中尖峰偏差区贡献 {fp_spike}）；"
              f"真窄峰检出 {tp}/150")
        print(f"    宽富集域召回率 = {recall:.3f}；伪 FRiP = {frip:.4f}")
    fpA, fpB, fpC = rows[0][1], rows[1][1], rows[2][1]
    recA, recB = rows[0][4], rows[1][4]
    fripA, fripB = rows[0][5], rows[1][5]
    print()
    print("  判读（对齐讲义 ⑨ 错误 2 / §4.3，MACS2 v2.2.9.1 源码口径）：")
    print(f"  · 尖峰偏差区：A 的 λ1k(对照) 把局部 λ 抬到尖峰自身的密度水平，"
          f"假阳性 ≈ 0；B 只剩自估 λ10k（2 kb 尖峰被 10 kb 窗稀释成 ~16），"
          f"30 处尖峰整体过线。")
    print(f"  · 宽富集域：B 的自估 λ10k 被真实富集自己抬高（~{args.lambda0*3.5:.0f}），"
          f"召回率 {recA:.2f} → {recB:.2f}——真信号被自己当背景扣掉；FRiP 随之 "
          f"{fripA:.3f} → {fripB:.3f}。A 有对照（对照平坦）则两项都保住。")
    print("  · 全程无报错：B/C 正常输出 peak 表，这就是「无报错型故障」。")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        check(f"手算泊松尾与 scipy 一致（|{p_hand:.3e} − {p_scipy:.3e}| < 1e-12）",
              abs(p_hand - p_scipy) < 1e-12)
        check(f"Part 1：λBG-only 域内假阳性 {fp_bg} 远高于 max 局部 λ 口径 {fp_loc}"
              f"（≥ 10 倍）", fp_bg >= 10 * max(fp_loc, 1))
        check(f"Part 2：有对照假阳性 ≈ 0（{fpA} ≤ 10）", fpA <= 10)
        check(f"Part 2：无对照假阳性暴增（{fpB} ≥ 200，主要来自尖峰偏差区）",
              fpB >= 200)
        check(f"Part 2：宽富集域召回 有对照 {recA:.2f} ≥ 0.5，无对照 {recB:.2f} ≤ 0.1"
              f"（自估 λ 自掩蔽）", recA >= 0.5 and recB <= 0.1)
        check(f"Part 2：伪 FRiP 有对照 {fripA:.3f} ≥ 2 × 无对照 {fripB:.3f}",
              fripA >= 2 * fripB)
        check("真窄峰（+30 reads）在 A/B/C 均高检出（≥ 130/150）",
              all(r[3] >= 130 for r in rows))
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

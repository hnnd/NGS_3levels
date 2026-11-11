#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch20_ld_r2_baseline.py — 连锁为零时样本 r² 的本底抽样期望 E[r̂²] ≈ 1/n：
基线垫高、跨样本曲线不可直视、半衰/标记密度读数偏差（合成算例）

服务于：教材第 20 章（群体遗传学与群体基因组）§20.4 概念与方法（LD 衰减的
统计插件）、§20.5 失效条件第 4 条（群体结构可伪装成 LD 平台高企）的判读前提，
对应讲义 p04 ⑦-7.3（「E[r̂²] ≈ 1/n；n = 30 时基线被垫高至 0.033，n = 200 时
0.005；样本量不等严禁直接视觉比对衰减曲线」）、⑥-6.1（LD 曲线正常/病态表型）
与 04_ld_decay_plot.R 的 baseline_1_over_n 输出行。

合成设定（不基于任何真实分离株；固定种子可复现；单倍体口径，与稻瘟菌一致）：
  - 两位点等位指示变量 X, Y ∈ {0,1}，给定边际频率与连锁不平衡系数 D 时
    配子型概率 P(1,1) = pX·pY + D，r² = D² / (pX·pX'·pY·pY')。
  - 部分 1（基线）：D = 0（完全无连锁），pX = pY = 0.5，抽 n 个单倍体个体
    算样本 r̂²（指示变量皮尔逊相关系数平方），大量位点对取均值 → 应 ≈ 1/n。
  - 部分 2（衰减曲线）：真实衰减 r²(d) = 0.8·2^(−d/H)（H 为半衰距离，合成设定
    H = 50 kb，即 r² 从峰值 0.8 衰减一半到 0.4 要走 50 kb），d 按 1 kb 分箱到
    200 kb；每箱抽若干位点对、n 个个体，观测均值曲线 = 真实值 + ≈1/n 基线。
    对 n = 30 与 n = 200 各做一条，按「naive（直接读观测曲线）」与
    「baseline-adjusted（每箱减 1/n）」两种口径报两个读数：
    半衰距离（峰值 0.8 减半到 0.4 的分箱）与 r̂² = 0.2 的距离
    （讲义 §4.4 的标记密度下限定义）。

正文引用的输出（手算可对）：
  - E[r̂²] ≈ 1/n 的蒙特卡洛核验：n = 30 → ≈ 0.0333、n = 200 → ≈ 0.005
    （讲义 ⑦-7.3 的两个原值）；
  - 同一真实衰减下 naive 读数：n = 30 半衰 ≈ 56 kb vs n = 200 ≈ 51 kb
    （解析期望 56.3 / 50.9）；r̂²=0.2 距离 ≈ 113 kb vs ≈ 102 kb
    （解析期望 113 / 102）—— 生物学完全相同，读数随样本量漂移，
    「跨样本直接视觉比对」是 ⑦-7.3 明文禁止的动作；
  - 扣 1/n 基线后两个样本量的读数都回到真实半衰 50 kb / 真实 0.2 距离
    100 kb 附近 —— 04_ld_decay_plot.R 同时输出两种口径的理由。

参数：
  --n-small     小样本量（默认 30，对应讲义 ⑦-7.3 例值）
  --n-large     大样本量（默认 200）
  --pairs       基线部分每位点对的重复数（默认 20000）
  --pairs-bin   衰减曲线每箱位点对数（默认 5000）
  --half-life   合成真实半衰距离 H（bp，默认 50000）
  --seed        随机种子（默认 20261104）

合成数据不得写成真实群体结果；真实 PLINK --r2 输出受 --ld-window-r2 0 是否
显式给出、分箱宽度与 Hill-Weir 拟合收敛影响（讲义 ⑨-E5、⑦-7.3 披露四要素），
本演示只复现「1/n 抽样基线 + 读数口径」这一层（unverified 的细粒度差异
见讲义）。只依赖 numpy；约 1 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch20_ld_r2_baseline.py --selftest
"""
import argparse

import numpy as np

R2_TRUE_MAX = 0.8  # 合成真实衰减曲线的峰值


def batch_r2(n, p_x, p_y, D, npairs, rng):
    """向量化：一次抽 npairs 个位点对、每对 n 个单倍体个体，返回各对样本 r̂²。"""
    p11 = p_x * p_y + D
    p_y_x1 = p11 / p_x          # P(Y=1 | X=1)
    p_y_x0 = (p_y - p11) / (1 - p_x)  # P(Y=1 | X=0)
    X = rng.random((npairs, n)) < p_x
    Y = rng.random((npairs, n)) < np.where(X, p_y_x1, p_y_x0)
    xm, ym = X.mean(axis=1), Y.mean(axis=1)
    cov = (X * Y).mean(axis=1) - xm * ym
    with np.errstate(divide="ignore", invalid="ignore"):
        r2 = cov ** 2 / (X.var(axis=1) * Y.var(axis=1))
    return r2[np.isfinite(r2)]


def mean_r2_unlinked(n, npairs, seed):
    """D = 0 时大量位点对的样本 r̂² 均值（应 ≈ 1/n）。"""
    rng = np.random.default_rng(seed)
    return float(batch_r2(n, 0.5, 0.5, 0.0, npairs, rng).mean())


def decay_curve(n, half_life, pairs_bin, seed, bin_bp=1000, max_kb=200):
    """返回 (bins_bp, observed_mean_r2)，真实曲线 r²(d) = 0.8·2^(−d/half_life)。"""
    rng = np.random.default_rng(seed)
    bins = np.arange(bin_bp, max_kb * 1000 + 1, bin_bp, dtype=float)
    obs = np.empty_like(bins)
    for j, d in enumerate(bins):
        r2_true = R2_TRUE_MAX * 2.0 ** (-d / half_life)
        D = np.sqrt(r2_true * 0.5 ** 4)
        obs[j] = batch_r2(n, 0.5, 0.5, D, pairs_bin, rng).mean()
    return bins, obs


def first_below(bins, curve, target):
    """首次降至 target 的分箱距离（讲义 04_ld_decay_plot.R 的 first_below 口径）。"""
    idx = np.nonzero(curve <= target)[0]
    return float(bins[idx[0]]) if len(idx) else float("nan")


def run(n_small, n_large, pairs, pairs_bin, half_life, seed):
    base_s = mean_r2_unlinked(n_small, pairs, seed + 7)
    base_l = mean_r2_unlinked(n_large, pairs, seed + 13)

    bins, obs_s = decay_curve(n_small, half_life, pairs_bin, seed + 21)
    _, obs_l = decay_curve(n_large, half_life, pairs_bin, seed + 33)
    adj_s, adj_l = obs_s - 1.0 / n_small, obs_l - 1.0 / n_large

    half_target = R2_TRUE_MAX / 2  # 峰值减半 = 半衰（讲义 ⑦-7.3 判定标准之一）
    naive_hd_s = first_below(bins, obs_s, half_target)
    naive_hd_l = first_below(bins, obs_l, half_target)
    adj_hd_s = first_below(bins, adj_s, half_target)
    adj_hd_l = first_below(bins, adj_l, half_target)
    # r̂² = 0.2 的距离：讲义 §4.4「标记间距必须小于 LD 降到 0.2 的距离」
    naive_02_s = first_below(bins, obs_s, 0.2)
    naive_02_l = first_below(bins, obs_l, 0.2)
    adj_02_s = first_below(bins, adj_s, 0.2)
    adj_02_l = first_below(bins, adj_l, 0.2)

    print(f"合成算例：单倍体个体，两位点指示变量；真实衰减 r²(d) = "
          f"{R2_TRUE_MAX}·2^(−d/{half_life / 1000:.0f}kb)（半衰 {half_life / 1000:.0f} kb）；"
          f"1 kb 分箱到 200 kb，每箱 {pairs_bin} 对\n")
    print("部分 1：连锁为零（D = 0）时的样本 r̂² 本底（讲义 ⑦-7.3 原值核对）")
    print(f"  n = {n_small:<4} mean r̂² = {base_s:.4f}   1/n = {1 / n_small:.4f}"
          f"   （讲义：基线被垫高至 0.033）")
    print(f"  n = {n_large:<4} mean r̂² = {base_l:.4f}   1/n = {1 / n_large:.4f}"
          f"   （讲义：回落至 0.005）")
    print("\n部分 2：同一真实衰减、两种样本量的两个读数（判定分箱 1 kb）")
    print(f"  半衰距离（峰值 {R2_TRUE_MAX:.1f} 减半到 {half_target:.2f}）：")
    print(f"    n = {n_small:<4} naive = {naive_hd_s / 1000:.1f} kb；adjusted = "
          f"{adj_hd_s / 1000:.1f} kb（真实 {half_life / 1000:.0f} kb）")
    print(f"    n = {n_large:<4} naive = {naive_hd_l / 1000:.1f} kb；adjusted = "
          f"{adj_hd_l / 1000:.1f} kb（真实 {half_life / 1000:.0f} kb）")
    print(f"  r̂² = 0.2 的距离（讲义 §4.4 标记密度下限）：")
    print(f"    n = {n_small:<4} naive = {naive_02_s / 1000:.1f} kb；adjusted = "
          f"{adj_02_s / 1000:.1f} kb（解析 {half_life / 1000 * 2:.0f} kb）")
    print(f"    n = {n_large:<4} naive = {naive_02_l / 1000:.1f} kb；adjusted = "
          f"{adj_02_l / 1000:.1f} kb（解析 {half_life / 1000 * 2:.0f} kb）")
    print("\n判读：")
    print("  ① 1/n 基线使小样本衰减曲线整体抬高、尾部下不去 —— ⑥-6.1「远距离平台"
          "异常高企」首先要与抽样基线区分（再怀疑群体分层）；")
    print("  ② naive 半衰与 0.2 距离都随 n 漂移而生物学相同 —— ⑦-7.3「严禁直接"
          "视觉比对绝对高度」的量化；")
    print("  ③ 扣基线后两样本读数收敛到真实值附近 —— 04_ld_decay_plot.R 同时输出"
          " naive 与 baseline-adjusted 两行的理由；")
    print("  ④ 方法学四要素（n、MAF 阈值、分箱宽度、半衰判定标准）缺一，半衰距离"
          "不可比 —— 讲义 ⑦-7.3 披露要求。")
    print("真实数据对照（PRJEB53625 40 株：ld_decay.txt 的 baseline_1_over_n = "
          "0.025 与 n = 40 一致；06_data/phd/README.md p04，无实测记录，unverified）。")
    return dict(base_s=base_s, base_l=base_l, bins=bins, obs_s=obs_s, obs_l=obs_l,
                adj_s=adj_s, adj_l=adj_l, naive_hd_s=naive_hd_s, naive_hd_l=naive_hd_l,
                adj_hd_s=adj_hd_s, adj_hd_l=adj_hd_l)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n-small", type=int, default=30)
    ap.add_argument("--n-large", type=int, default=200)
    ap.add_argument("--pairs", type=int, default=20000)
    ap.add_argument("--pairs-bin", type=int, default=5000)
    ap.add_argument("--half-life", type=float, default=50000)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    r = run(args.n_small, args.n_large, args.pairs, args.pairs_bin, args.half_life,
            args.seed)

    if args.selftest:
        # 解析对照：真实半衰处（d = H）观测曲线 ≈ 峰值/2 + 1/n
        idx_h = int(np.argmin(np.abs(r["bins"] - args.half_life)))
        expect_s = R2_TRUE_MAX / 2 + 1 / args.n_small
        expect_l = R2_TRUE_MAX / 2 + 1 / args.n_large
        checks = [
            (f"E[r̂²] ≈ 1/n，n = {args.n_small}（{r['base_s']:.4f} vs "
             f"{1 / args.n_small:.4f}，|Δ| < 0.004）",
             abs(r["base_s"] - 1 / args.n_small) < 0.004),
            (f"E[r̂²] ≈ 1/n，n = {args.n_large}（{r['base_l']:.4f} vs "
             f"{1 / args.n_large:.4f}，|Δ| < 0.004）",
             abs(r["base_l"] - 1 / args.n_large) < 0.004),
            (f"n = {args.n_small} 基线 > n = {args.n_large} 基线 6 倍以上"
             f"（{r['base_s'] / r['base_l']:.1f}×）",
             r["base_s"] > 6 * r["base_l"]),
            (f"观测曲线贴解析式：半衰处 n = {args.n_small}（{r['obs_s'][idx_h]:.4f}"
             f" vs {expect_s:.4f}）", abs(r["obs_s"][idx_h] - expect_s) < 0.02),
            (f"观测曲线贴解析式：半衰处 n = {args.n_large}（{r['obs_l'][idx_h]:.4f}"
             f" vs {expect_l:.4f}）", abs(r["obs_l"][idx_h] - expect_l) < 0.02),
            (f"naive 半衰：n = {args.n_small}({r['naive_hd_s'] / 1000:.1f} kb) > "
             f"n = {args.n_large}({r['naive_hd_l'] / 1000:.1f} kb) —— 基线拖长读数",
             r["naive_hd_s"] > r["naive_hd_l"]),
            (f"扣基线后两样本半衰收敛（|{r['adj_hd_s'] / 1000:.1f} − "
             f"{r['adj_hd_l'] / 1000:.1f}| < |{r['naive_hd_s'] / 1000:.1f} − "
             f"{r['naive_hd_l'] / 1000:.1f}| kb）",
             abs(r["adj_hd_s"] - r["adj_hd_l"]) < abs(r["naive_hd_s"] - r["naive_hd_l"])),
            (f"两样本扣基线半衰都落在真实半衰 ±30%（真实 {args.half_life / 1000:.0f}"
             f" kb；{r['adj_hd_s'] / 1000:.1f} / {r['adj_hd_l'] / 1000:.1f} kb）",
             abs(r["adj_hd_s"] - args.half_life) < 0.3 * args.half_life
             and abs(r["adj_hd_l"] - args.half_life) < 0.3 * args.half_life),
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

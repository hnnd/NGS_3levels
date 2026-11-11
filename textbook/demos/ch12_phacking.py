#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch12_phacking.py — 先看结果再换检验 / 删「离群」点 / 放宽阈值：I 类错误率到底膨胀多少（合成算例）

服务章节：第 12 章 §12.4 概念与方法（p 值的认识论语义）、§12.5 失效条件第 4 条
（先看结果再换检验或删「离群」样本 = p-hacking；PCA 上分开不等于统计显著）。
源讲义：l0_06_stats「常见错误与排查」第 7 条与 §3「学术违规歧途」。

机制（蒙特卡洛，全部合成数据，H0 为真：两组都是 N(0,1)，真差异为 0）：
  每组 5 个样本、重复 n_iter 次「一次完整的分析会话」。每种「分析习惯」对应一条
  决策链，观测其在零假设下的拒绝率（= 实际 I 类 错误率）。关键发现分两层：
    * 换「同类」检验（t 不显著改 Wilcoxon）膨胀极小 —— 两种统计量高度相关，
      朴素独立上限 1-(1-α)² ≈ 0.098 只是天花板，实测几乎不涨；
    * 真正的大头是「依赖结果改数据」（删掉最偏离的点重跑，选择性缩小组内方差）
      与「放宽阈值」（0.05 → 0.10）—— 两者叠加可到名义 α 的 5 倍。
  红线不变：无论膨胀大小，「换到显著为止」使报告的 p 值失去意义（失效条件 4）；
  本脚本给的是「哪一步有多伤」的定量注脚。

  策略链（每步都「看结果再决定」，逐步加码）：
    S1 预注册 t（只此一次）                    → 应恰为 α
    S2 = S1 不显著就改 Wilcoxon（同类替换）    → 实测几乎不涨（相关性保护了你）
    S3 = S2 再删 1 个「离群」点重跑 t（改数据） → 猛涨（选择性缩方差）
    S4 只把同一 t 的阈值放宽到 0.10（改阈值）  → ≈ 2α
    S5 = S3 链上阈值再放宽到 0.10（改数据+阈值）→ α 的 ~5 倍
    S6 预注册置换检验（n_perm 次，一步定死）    → 仍 ≈ α（正路对照）

参数（--help 可见）：
  --n-iter      蒙特卡洛迭代数（默认 8000；S6 用其 1/8，置换检验单iter较贵）
  --n-per-group 每组样本量（默认 5）
  --n-perm      S6 置换次数（默认 999，+1 校正）
  --alpha       名义显著性水准（默认 0.05）
  --seed        随机种子（默认固定）

正文引用的输出：
  - 六行「拒绝率 × 平均检验次数」对照表：p-hacking 的伤害排序
    改数据 ≳ 改阈值 ≫ 换同类检验；朴素上限 1-(1-α)^k 是天花板不是预测
  - S6 对照：预注册置换检验拒绝率仍贴 α —— 救功效的正路是「预先声明且
    检验水平正确」的方法，不是「换到显著为止」

依赖：Python 标准库 + numpy + scipy（t 分布 CDF；MW 精确分布用组合枚举自建
并逐点对照 scipy.stats.mannwhitneyu(method='exact')）。
合成算例：所有样本均为 N(0,1) 伪随机数，与任何真实样本无关。
"""
import argparse
import sys
from itertools import combinations

import numpy as np
from scipy import stats

SEED = 20261104


def mw_exact_two_sided_pvalues(U, n):
    """无结 Mann-Whitney U（1-based 秩口径，U ∈ [0, n²]）的精确双侧 p：
    枚举全部 C(2n,n) 种秩分配，p = 2 × min(P(U≤u), P(U≥u))，封顶 1 —
    与 scipy.stats.mannwhitneyu(method='exact') 同约定（selftest 逐点对照）。"""
    counts = {}
    for comb in combinations(range(2 * n), n):
        u = sum(comb) - n * (n - 1) // 2     # 1-based：sum(1..2n 选 n 个) − n(n−1)/2
        counts[u] = counts.get(u, 0) + 1
    n_perm = sum(counts.values())
    tot = np.array([counts.get(u, 0) for u in range(n * n + 1)], dtype=float)
    lo = np.cumsum(tot) / n_perm             # P(U ≤ u)
    hi = (np.cumsum(tot[::-1]) / n_perm)[::-1]  # P(U ≥ u)
    p = 2.0 * np.where(U <= n * n / 2, lo[U], hi[U])
    return np.minimum(p, 1.0)


def vectorized_mw_p(X, Y):
    """对 (k,n)+(k,n) 批量算 MW 精确双侧 p（数据连续无结）。
    双 argsort 给 0-based 秩，U_1based = Σ秩(0based) − n(n−1)/2 ∈ [0, n²]。"""
    pooled = np.concatenate([X, Y], axis=1)
    ranks = pooled.argsort(axis=1).argsort(axis=1)   # 0-based 秩 0..2n-1
    n = X.shape[1]
    U = ranks[:, :n].sum(axis=1) - n * (n - 1) // 2
    return mw_exact_two_sided_pvalues(U.astype(int), n)


def t_p(x, y):
    """等方差两样本 t 检验双侧 p（与 R t.test(var.equal=TRUE) 同公式）。"""
    n1, n2 = len(x), len(y)
    df = n1 + n2 - 2
    sp2 = ((n1 - 1) * x.var(ddof=1) + (n2 - 1) * y.var(ddof=1)) / df
    t = (x.mean() - y.mean()) / np.sqrt(sp2 * (1.0 / n1 + 1.0 / n2))
    return float(2.0 * stats.t.cdf(-abs(t), df))


def drop_outlier(x, y):
    """删去「与所属组均值偏离最大」的观测（依赖结果的数据改写），
    返回删点后的两组（一组 5 个、另一组 4 个）。"""
    dx = np.abs(x - x.mean())
    dy = np.abs(y - y.mean())
    if dx.max() >= dy.max():
        return np.delete(x, int(dx.argmax())), y
    return x, np.delete(y, int(dy.argmax()))


def permutation_p(x, y, rng, n_perm):
    """两组置换检验（打乱组别标签），p = (1 + #{|t_perm| ≥ |t_obs|})/(n_perm+1)。"""
    z = np.concatenate([x, y])
    n = len(x)
    sp = np.sqrt((x.var(ddof=1) + y.var(ddof=1)) / 2 * (1.0 / n + 1.0 / n))
    t_obs = abs((x.mean() - y.mean()) / sp)
    idx = rng.random((n_perm, 2 * n)).argpartition(n, axis=1)[:, :n]
    mask = np.zeros((n_perm, 2 * n), dtype=bool)
    mask[np.arange(n_perm)[:, None], idx] = True
    mx = (z[None, :] * mask).sum(1) / n
    my = (z[None, :] * ~mask).sum(1) / n
    vx = (((z[None, :] - mx[:, None]) ** 2) * mask).sum(1) / (n - 1)
    vy = (((z[None, :] - my[:, None]) ** 2) * ~mask).sum(1) / (n - 1)
    tp = (mx - my) / np.sqrt((vx + vy) / 2 * (2.0 / n))
    return float((1.0 + (np.abs(tp) >= t_obs).sum()) / (n_perm + 1.0))


def main():
    ap = argparse.ArgumentParser(
        description="p-hacking 各策略的 I 类错误率蒙特卡洛（合成算例；服务第 12 章"
                    "失效条件 4，对齐讲义常见错误第 7 条）")
    ap.add_argument("--n-iter", type=int, default=8000)
    ap.add_argument("--n-per-group", type=int, default=5)
    ap.add_argument("--n-perm", type=int, default=999)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    a = args.alpha
    n = args.n_per_group
    rng = np.random.default_rng(args.seed)

    print("=" * 78)
    print(f"[合成算例 · 蒙特卡洛] H0 为真：两组均为 N(0,1)，每组 n={n}；"
          f"{args.n_iter} 次「分析会话」（seed={args.seed}）")
    print("=" * 78)
    X = rng.standard_normal((args.n_iter, n))
    Y = rng.standard_normal((args.n_iter, n))

    df = 2 * n - 2
    sp2 = (X.var(axis=1, ddof=1) + Y.var(axis=1, ddof=1)) / 2
    t1 = (X.mean(axis=1) - Y.mean(axis=1)) / np.sqrt(sp2 * 2.0 / n)
    p_t = 2.0 * stats.t.cdf(-np.abs(t1), df)

    # S1：预注册 t
    rej_s1 = p_t < a
    # S2：t 不显著 → Mann-Whitney 精确（同类替换；向量化）
    need2 = ~rej_s1
    p_mw = np.full(args.n_iter, np.inf)
    idx2 = np.flatnonzero(need2)
    p_mw[idx2] = vectorized_mw_p(X[idx2], Y[idx2])
    rej_s2 = rej_s1 | (p_mw < a)
    # S3：还不显著 → 删 1 个「离群」点重跑 t（改数据）
    need3 = ~rej_s2
    p_drop = np.full(args.n_iter, np.inf)
    for i in np.flatnonzero(need3):
        xd, yd = drop_outlier(X[i], Y[i])
        p_drop[i] = t_p(xd, yd)
    rej_s3 = rej_s2 | (p_drop < a)
    # S4：只放宽阈值（同一 t，p < 0.10）
    rej_s4 = p_t < 2 * a
    # S5：改数据 + 放宽阈值叠加
    rej_s5 = rej_s3 | (np.minimum(np.minimum(p_t, p_mw), p_drop) < 2 * a)
    # S6：预注册置换检验（独立小样本迭代）
    n_s6 = max(args.n_iter // 8, 500)
    rej_s6 = np.empty(n_s6, dtype=bool)
    for i in range(n_s6):
        rej_s6[i] = permutation_p(X[i], Y[i], rng, args.n_perm) < a

    k23 = 1.0 + need2.mean() + need3.mean()
    print(f"{'策略':<36} {'拒绝率':>8} {'名义 α':>7} {'平均检验次数':>10}")
    table = [
        ("S1 预注册 t（只此一次）", rej_s1.mean(), 1.0),
        ("S2 = S1 不显著就改 Wilcoxon", rej_s2.mean(), k23),
        ("S3 = S2 再删 1 个「离群」点重跑", rej_s3.mean(), k23),
        ("S4 只把同一 t 的阈值放宽到 0.10", rej_s4.mean(), 1.0),
        ("S5 = 删点链 + 阈值放宽（叠加）", rej_s5.mean(), k23),
        (f"S6 预注册置换检验（{args.n_perm}+1 校正）", rej_s6.mean(), 1.0),
    ]
    for name, rate, kt in table:
        print(f"{name:<36} {rate:>8.3f} {a:>7.2f} {kt:>10.2f}")
    naive = 1 - (1 - a) ** 2
    print(f"读法（失效条件 4 的定量注脚）：")
    print(f"  · 换同类检验（S2）几乎不涨：{table[1][1]:.3f} vs 朴素独立上限 "
          f"{naive:.3f} —— t 与 Wilcoxon 高度相关，天花板远达不到；")
    print(f"  · 改数据（S3，依赖结果删「离群」点）{table[2][1]:.3f} 与放宽阈值"
          f"（S4）{table[3][1]:.3f} ≈ 2α 才是大头，叠加（S5）到 "
          f"{table[4][1]:.3f} ≈ {table[4][1] / max(table[0][1], 1e-9):.1f} 倍 α；")
    print("  · 红线不变：无论涨多少，「换到显著为止」都让 p 值失去意义；"
          "正路是 S6 —— 预注册一个检验水平正确的方法（置换检验），拒绝率仍贴 α。")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        r = [row[1] for row in table]
        check(f"S1 预注册 t 拒绝率 {r[0]:.3f} ≈ α={a}（±0.01）",
              abs(r[0] - a) <= 0.01)
        check(f"S6 预注册置换检验拒绝率 {r[5]:.3f} ≈ α={a}（±0.02）",
              abs(r[5] - a) <= 0.02)
        check(f"S2 换同类检验增量 < 0.02（实测 {r[1] - r[0]:+.3f}；"
              "t 与 Wilcoxon 高度相关，够不到独立上限）",
              r[1] - r[0] < 0.02)
        check(f"S3 删「离群」点 ≥ 2×S1（实测 {r[2] / max(r[0], 1e-9):.1f}×）",
              r[2] >= 2 * r[0])
        check(f"S4 放宽阈值到 0.10 ∈ [1.5α, 2.5α]（实测 {r[3]:.3f}）",
              1.5 * a <= r[3] <= 2.5 * a)
        check(f"S5 叠加 ≥ 3×S1（实测 {r[4] / max(r[0], 1e-9):.1f}×）",
              r[4] >= 3 * r[0])
        check("S6 < S5：正路对照不受 p-hacking 影响",
              r[5] < r[4] - 0.05)
        # MW 精确分布自建表与 scipy 逐点对照（200 个随机场合）
        rs = np.random.default_rng(args.seed + 7)
        Xs = rs.standard_normal((200, n))
        Ys = rs.standard_normal((200, n))
        mine = vectorized_mw_p(Xs, Ys)
        ref = np.array([stats.mannwhitneyu(Xs[i], Ys[i], alternative="two-sided",
                                           method="exact").pvalue
                        for i in range(200)])
        check("自建 MW 精确分布与 scipy exact 逐点一致（max|Δ| < 1e-12）",
              float(np.max(np.abs(mine - ref))) < 1e-12)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

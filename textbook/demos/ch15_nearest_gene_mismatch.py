#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch15_nearest_gene_mismatch.py — 「最近基因 ≠ 靶基因」的几何错配率（合成算例）

服务章节：第 15 章 §15.4 概念与方法（ChIPseeker 最近基因注释的局限）、
§15.5 失效条件第 3 条「最近基因不等于靶基因；远端调控元件被错配」。
源讲义：m05 §4.5、⑦ 第 6 条、⑨ 错误 4、⑩ 练习 3。

机制（讲义 §4.5）：增强子经染色质环作用于几十 kb 外的基因是常态，中间可能隔着
好几个无关基因。ChIPseeker 的默认规则把 peak 关联到**最近 TSS**——只要增强子与
真实靶基因之间存在更近的无关 TSS，关联就错。几何判据（Part 0）：真实距离 r 内
出现无关 TSS 即错配。因此错配率由 **真实距离 ÷ 基因间距** 的比值驱动，而不是
密度或距离各自单独决定——这同时解释了讲义 §4.5 第 ③ 条「紧凑基因组里最近基因
规则反而更可靠」的成立条件：紧凑基因组的调控距离**也随之变短**（d/间距 比值小），
不是密度本身带来可靠性。本合成算例把两个因素拆开演示（Part 2 / Part 2b）。

模型（合成，非 PRJDB36269 或任何真实样本）：
  * 一条合成染色体（单位 kb），TSS 按 Poisson 过程撒布，间距 ~ Exp(1/密度)，
    链向 ± 各半；E 个增强子，各配一个真实靶基因（取距随机落点最近的 TSS）；
    d 两种抽法（Part 1/2 固定口径；Part 2b 比值扫描）见正文。
  * 最近基因规则：全基因组离增强子最近的 TSS（不分链向，同 distanceToNearest 口径）；
    错配 = 最近基因 ≠ 真实靶基因。

参数（--help 可见）：
  --mean-tss-compact / --mean-tss-sparse   两档 TSS 间距均值 kb（默认 8 / 25）
  --n-enh                                  合成增强子数（默认 400）
  --dist-mean-kb / --dist-sigma            固定口径的真实距离几何均值与 sigma
  --chrom-mb                               合成染色体长度 Mb（默认 120）
  --seed                                   随机种子（默认 20260829）

正文引用的输出：
  - Part 0 手算规则：等距基因下的错配判据；
  - Part 1：错配率按真实距离分层 + 错配事件「中间隔了几个无关基因」（机制）；
  - Part 2：同一真实距离分布下，密度越高错配率越高（中间插入无关基因是机制）；
  - Part 2b：d/间距 比值扫描——错配率随比值单调上升；紧凑基因组「更可靠」的
    成立条件是真实调控距离显著小于基因间距（讲义 §4.5 ③ 的完整表述）；
  - Part 3：「只信 ≤10 kb」截断规则的对照——错配率压不下来、覆盖先丢一半。

依赖：Python 标准库 + numpy。
合成算例：所有 TSS 布局与增强子–靶配对均为随机数生成器产物，与任何真实基因组无关。
"""
import argparse
import sys

import numpy as np

SEED = 20260829


def build_tss(rng, chrom_kb, mean_spacing):
    """TSS 位置：Poisson 过程间距 Exp(mean_spacing)，链向随机。"""
    n = int(rng.poisson(chrom_kb / mean_spacing))
    pos = np.sort(rng.uniform(0, chrom_kb, size=n))
    return pos


def nearest_gene(tss_pos, query):
    """离 query 最近的 TSS 索引（不分链向）。"""
    return int(np.argmin(np.abs(tss_pos - query)))


def simulate(rng, chrom_kb, mean_spacing, n_enh, dist_mu, dist_sigma,
             d_min=3.0, d_max=150.0):
    tss_pos = build_tss(rng, chrom_kb, mean_spacing)
    n_genes = len(tss_pos)
    enh_pos = np.sort(rng.uniform(0, chrom_kb, size=n_enh))
    mism = np.zeros(n_enh, dtype=bool)
    skipped = np.zeros(n_enh, dtype=int)     # 增强子与靶基因之间的无关基因数
    dists = np.empty(n_enh)
    nearest_dist = np.empty(n_enh)
    for i, e in enumerate(enh_pos):
        d = float(np.clip(rng.lognormal(dist_mu, dist_sigma), d_min, d_max))
        side = rng.choice([-1, 1])
        target_pos = e + side * d
        if target_pos < 0 or target_pos > chrom_kb:      # 出界则换向，保底可配对
            target_pos = e - side * d
        true_gene = nearest_gene(tss_pos, target_pos)
        ni = nearest_gene(tss_pos, e)
        mism[i] = ni != true_gene
        lo, hi = sorted([e, tss_pos[true_gene]])
        skipped[i] = int(((tss_pos > lo) & (tss_pos < hi)).sum())
        dists[i] = abs(tss_pos[true_gene] - e)
        nearest_dist[i] = abs(tss_pos[ni] - e)
    return mism, skipped, dists, nearest_dist, n_genes


def stratify(mism, dists):
    out = []
    for lo, hi in [(0, 10), (10, 30), (30, 60), (60, 150)]:
        m = (dists >= lo) & (dists < hi)
        if m.sum():
            out.append((lo, hi, int(m.sum()), mism[m].mean()))
    return out


def main():
    ap = argparse.ArgumentParser(
        description="最近基因 ≠ 靶基因的几何错配率（合成算例；服务第 15 章失效条件 3，"
                    "对齐讲义 m05 §4.5）")
    ap.add_argument("--mean-tss-compact", type=float, default=8.0)
    ap.add_argument("--mean-tss-sparse", type=float, default=25.0)
    ap.add_argument("--n-enh", type=int, default=400)
    ap.add_argument("--dist-mean-kb", type=float, default=25.0)
    ap.add_argument("--dist-sigma", type=float, default=0.6)
    ap.add_argument("--chrom-mb", type=float, default=120.0)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    chrom_kb = args.chrom_mb * 1000.0

    # ---------------- Part 0：手算规则 ----------------
    print("=" * 78)
    print("[Part 0 · 手算规则] 等距基因下的错配判据")
    print("=" * 78)
    spacing, r, d_un = 20, 15, 20 - 15
    print(f"  基因等距 {spacing} kb，增强子在真实靶 G2 上游 {r} kb 处：")
    print(f"  中间的无关基因 G1 距增强子 {spacing} − {r} = {d_un} kb < {r} kb")
    print("  → 最近基因规则把该增强子关联给 G1，错配。判据：真实距离 r 内存在更近的")
    print("    无关 TSS 即错配——错配率由「真实距离 ÷ 基因间距」的比值驱动。")

    # ---------------- Part 1：距离分层（稀疏基因组） ----------------
    print()
    print("=" * 78)
    print("[Part 1 · 合成算例] 错配率按真实距离分层（稀疏基因组，mean 间距 25 kb）")
    print("=" * 78)
    res = {}
    mism, skipped, dists, ndist, n_genes = simulate(
        rng, chrom_kb, args.mean_tss_sparse, args.n_enh,
        np.log(args.dist_mean_kb), args.dist_sigma)
    res["sparse_fixed"] = (mism, skipped, dists, ndist)
    print(f"  合成染色体 {args.chrom_mb:.0f} Mb，{n_genes} 个基因，{args.n_enh} 个增强子；"
          f"总错配率 {mism.mean():.1%}")
    for lo, hi, n, rate in stratify(mism, dists):
        print(f"    真实距离 {lo:>3}–{hi:<3} kb：错配率 {rate:.1%}（n={n}）")
    med_skip = int(np.median(skipped[mism])) if mism.any() else 0
    print(f"  错配事件中位「中间隔的无关基因数」 = {med_skip}")
    print("  判读：距离越远、中间插入无关基因越多，错配率单调上升——这是失效条件 3 的"
    )
    print("        机制本体，与物种无关。")

    # ---------------- Part 2：密度对照（固定距离分布） ----------------
    print()
    print("=" * 78)
    print("[Part 2 · 合成算例] 同一距离分布：密度越高，错配率越高")
    print("=" * 78)
    mism_c, skipped_c, dists_c, ndist_c, n_genes_c = simulate(
        rng, chrom_kb, args.mean_tss_compact, args.n_enh,
        np.log(args.dist_mean_kb), args.dist_sigma)
    res["compact_fixed"] = (mism_c, skipped_c, dists_c, ndist_c)
    print(f"  紧凑（mean 间距 {args.mean_tss_compact:.0f} kb，{n_genes_c} 基因） vs "
          f"稀疏（mean 间距 {args.mean_tss_sparse:.0f} kb，{n_genes} 基因），"
          f"真实距离同一分布（几何均值 {args.dist_mean_kb:.0f} kb）")
    print(f"    紧凑错配率 = {mism_c.mean():.1%}；稀疏错配率 = {mism.mean():.1%}")
    print("  判读：插入无关基因的机制在**高密度**基因组里更频繁——所以「紧凑基因组更")
    print("        可靠」绝不能从密度单独推出；它依赖紧凑基因组的调控距离也短。")

    # ---------------- Part 2b：比值扫描（讲义 §4.5 ③ 的成立条件） ----------------
    print()
    print("=" * 78)
    print("[Part 2b · 合成算例] d/间距 比值扫描：什么条件下紧凑基因组才更可靠")
    print("=" * 78)
    sweep = []
    for d_geo in (6.0, args.dist_mean_kb, 60.0):
        m_s, _, _, _, _ = simulate(rng, chrom_kb, args.mean_tss_sparse, args.n_enh,
                                   np.log(d_geo), args.dist_sigma)
        sweep.append((d_geo, m_s.mean()))
        print(f"  稀疏（间距 {args.mean_tss_sparse:.0f} kb），真实距离几何均值 {d_geo:.0f} kb"
              f"（比值 {d_geo/args.mean_tss_sparse:.2f}）→ 错配率 {m_s.mean():.1%}")
    m_c_short, _, _, _, _ = simulate(rng, chrom_kb, args.mean_tss_compact, args.n_enh,
                                     np.log(4.0), args.dist_sigma)
    print(f"  紧凑（间距 {args.mean_tss_compact:.0f} kb），真实距离几何均值 4 kb"
          f"（比值 0.50）→ 错配率 {m_c_short.mean():.1%}")
    print("  判读：错配率由 d/间距 比值单调驱动；紧凑基因组要「更可靠」，真实调控距离")
    print("        必须显著小于基因间距（比值 < 1）——这才是讲义 §4.5 ③「紧凑基因组里")
    print("        最近基因规则反而更可靠」的完整成立条件，只谈密度会把远端元件的错配")
    print("        风险（Part 2）一并放大。")

    # ---------------- Part 3：「只信 ≤10 kb」截断规则 ----------------
    print()
    print("=" * 78)
    print("[Part 3 · 合成算例] 补救规则的代价：≤10 kb 截断")
    print("=" * 78)
    for label, (mism_x, _, _, ndist_x) in [("稀疏（Part 1 设定）", res["sparse_fixed"]),
                                           ("紧凑（Part 2 设定）", res["compact_fixed"])]:
        keep = ndist_x <= 10.0
        if keep.sum():
            print(f"  {label}：只采用「最近基因且 ≤10 kb」的增强子"
                  f"（可注释 {keep.mean():.0%}）→ 错配率 {mism_x[keep].mean():.1%}")
    print("  判读：截断压不下错配（近距离里照样错），却先丢掉一半以上远端元件——")
    print("        讲义 §4.5 的措辞边界：注释表给的是「peak 的最近基因」，确认靶基因")
    print("        关系需要 Hi-C / HiChIP 互作数据或功能验证（报告基因、CRISPR 敲除、EMSA）。")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        check("Part 0：手算判据成立（无关基因更近：5 < 15）", d_un < r)
        rates = [r4 for _, _, _, r4 in stratify(mism, dists)]
        check(f"Part 1：错配率随真实距离单调上升（{['%.1f%%' % (100*r) for r in rates]}）",
              all(b >= a for a, b in zip(rates, rates[1:])))
        check(f"Part 1：错配事件中间隔 ≥1 个无关基因（中位 {med_skip} ≥ 1）",
              med_skip >= 1)
        check(f"Part 2：同一距离分布下紧凑错配率（{mism_c.mean():.1%}）高于稀疏"
              f"（{mism.mean():.1%}）", mism_c.mean() > mism.mean())
        sw = [r for _, r in sweep]
        check(f"Part 2b：错配率随 d/间距 比值单调上升"
              f"（{['%.1f%%' % (100*r) for r in sw]}）",
              all(b > a for a, b in zip(sw, sw[1:])))
        check(f"Part 2b：紧凑基因组短距离（比值 0.50，{m_c_short.mean():.1%}）优于稀疏"
              f"比值 1.0（{sweep[1][1]:.1%}）——讲义 ③ 的成立条件",
              m_c_short.mean() < sweep[1][1])
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

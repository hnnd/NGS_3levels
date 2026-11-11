#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch10_pcr_duplicate_support.py — PCR 重复伪造等位支持度（合成算例）

服务章节：第 10 章 §10.4「MarkDuplicates 的统计作用」（源讲义 m03 §4.3），
失效条件第 1 条（PCR 重复伪造等位支持度，抬高假变异置信度）的定量版；
呼应讲义 ⑥ 6.2.3「AD 是 VCF 里最诚实的字段」与 ⑦ 7.1。

模型（全部为合成模型，非任何真实样本结果）：
  * 一个纯合参考位点（haploid 口径，或二倍体纯合），共有 n 个独立原始分子
    覆盖。若建库早期某个分子被聚合酶引入错配（「早期错误」），后续 PCR 把它
    扩增成 K 份拷贝；MarkDuplicates 按 5' 坐标 + 方向 + 插入长度应把这 K 份
    判为重复并只留 1 份证据（讲义 §4.3：保留碱基质量最高的一对）。
  * 去重前：观测到 K 条 ALT read / D 条总 read（D = n-1 + K）。
    去重后：观测到 1 条 ALT read / n 条总 read（每个原始分子一票）。
  * QUAL 代理分：朴素二项尾概率 Phred = -10·log10 P(X >= x | Binom(D, q))，
    q = 单 read 测序错误率（默认 0.01，即 Q20——放宽到对假变异有利的一侧；
    真实 caller 的 Pair-HMM 更复杂，本 demo 只对比「重复前后同一打分函数」
    下结论怎么变）。x = 0 时 Phred = 0。
  * 「判为变异」判据（合成判据，非 GATK 内部逻辑）：x >= --min-alt 且
    Phred >= --phred-cut（默认 20，即错误率 < 1%）。

参数（--help 可见）：
  --loci            模拟位点数（默认 2000）
  --molecules       每个位点的独立原始分子数 n（默认 24；≈ 去重后有效深度）
  --amp             早期错误分子的扩增拷贝数 K（默认 8；(K-1)/(n-1+K) 即该位点
                    表观重复率，默认 7/31 ≈ 22.6%）
  --locus-error-rate 某位点出现早期错误分子的概率（默认 0.05）
  --seq-error       打分用的单 read 测序错误率 q（默认 0.01 = Q20）
  --min-alt/--phred-cut  判为变异的合成判据（默认 2 / 20）
  --seed            随机种子（默认固定）

正文引用的输出：
  - 重复前后 AD（ALT 支持条数）与 QUAL 代理分的中位/均值对照
  - 「判为变异」的位点占比：去重前 vs 去重后（失效条件第 1 条的量化）
  - 放大倍数 K 的直接读数：假变异的 ALT 支持条数 ≈ K、去重后 = 1
"""
import argparse
import math
import sys

import numpy as np

SEED = 20261104


def phred_tail(x, d, q):
    """P(X >= x | Binom(d, q)) 的 Phred 分；x=0 返回 0。"""
    if x <= 0:
        return 0.0
    #  survival = 1 - CDF(x-1)
    cdf = 0.0
    for k in range(x):
        cdf += math.comb(d, k) * q ** k * (1.0 - q) ** (d - k)
    return -10.0 * math.log10(max(1.0 - cdf, 1e-300))


def main():
    ap = argparse.ArgumentParser(
        description="PCR 重复伪造等位支持度（合成算例；源讲义 m03 §4.3，失效条件 1）")
    ap.add_argument("--loci", type=int, default=2000, help="模拟位点数")
    ap.add_argument("--molecules", type=int, default=24, help="每点位独立分子数 n")
    ap.add_argument("--amp", type=int, default=8, help="早期错误分子的扩增拷贝数 K")
    ap.add_argument("--locus-error-rate", type=float, default=0.05,
                    help="某位点出现早期错误分子的概率")
    ap.add_argument("--seq-error", type=float, default=0.01,
                    help="打分用单 read 错误率 q（默认 0.01 = Q20）")
    ap.add_argument("--min-alt", type=int, default=2, help="判变异的最少 ALT 条数")
    ap.add_argument("--phred-cut", type=float, default=20.0, help="判变异的 Phred 阈值")
    ap.add_argument("--seed", type=int, default=SEED, help="随机种子")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    n, K = args.molecules, args.amp
    D = n - 1 + K                     # 去重前总 read 数（合成布局下为定值）
    dup_rate = (K - 1) / D
    q = args.seq_error
    rng = np.random.default_rng(args.seed)

    err_loci = rng.random(args.loci) < args.locus_error_rate
    x_before = np.where(err_loci, K, 0)   # 去重前 ALT 支持
    d_before = np.full(args.loci, D)
    x_after = np.where(err_loci, 1, 0)    # 去重后每个错误分子只剩 1 票
    d_after = np.full(args.loci, n)

    ph_before = np.array([phred_tail(int(x), int(d), q)
                          for x, d in zip(x_before, d_before)])
    ph_after = np.array([phred_tail(int(x), int(d), q)
                         for x, d in zip(x_after, d_after)])
    called_before = (x_before >= args.min_alt) & (ph_before >= args.phred_cut)
    called_after = (x_after >= args.min_alt) & (ph_after >= args.phred_cut)

    print("=" * 78)
    print(f"[合成布局] 每点 {n} 个独立分子；早期错误分子扩增为 {K} 份拷贝，"
          f"其余 {n-1} 个分子各 1 份")
    print(f"           去重前总深度 D = {D}（表观重复率 (K-1)/D = "
          f"{dup_rate * 100:.1f}%）；去重后有效深度 = {n}")
    print(f"           早期错误位点占比（seed={args.seed}）："
          f"{err_loci.sum()}/{args.loci} = {err_loci.mean() * 100:.1f}%")
    print("=" * 78)
    print("[Part 1] 单个早期错误位点的重复前/后对照（手算锚点）")
    print("-" * 78)
    print(f"去重前: AD = {D - K},{K}（REF,ALT 顺序；ALT 占比 {K / D * 100:.1f}%）；"
          f"QUAL 代理 = {phred_tail(K, D, q):.1f}")
    print(f"去重后: AD = {n - 1},1（REF,ALT 顺序；ALT 占比 {1 / n * 100:.1f}%）；"
          f"QUAL 代理 = {phred_tail(1, n, q):.1f}")
    print(f"判据 x>={args.min_alt} 且 Phred>={args.phred_cut:.0f}："
          f"去重前 → 判为变异；去重后 → 证据不足，丢弃")

    print()
    print("=" * 78)
    print(f"[Part 2] {args.loci} 个合成位点的批对照")
    print("=" * 78)
    print(f"{'':<14}{'ALT 支持(中位)':>14}{'ALT 占比%':>10}{'Phred 中位':>12}"
          f"{'判为变异%':>10}")
    print("-" * 62)
    print(f"{'去重前':<14}{np.median(x_before):>14.0f}"
          f"{np.median(x_before / d_before) * 100:>10.1f}"
          f"{np.median(ph_before):>12.1f}"
          f"{called_before.mean() * 100:>10.1f}")
    print(f"{'去重后':<14}{np.median(x_after):>14.0f}"
          f"{np.median(x_after / d_after) * 100:>10.1f}"
          f"{np.median(ph_after):>12.1f}"
          f"{called_after.mean() * 100:>10.1f}")
    print("-" * 62)
    err = err_loci
    print(f"仅看早期错误位点（{err.sum()} 个）：去重前 ALT 支持均值 "
          f"{x_before[err].mean():.2f}（== K = {K}），去重后 "
          f"{x_after[err].mean():.2f}（== 1）")
    print(f"去重前被判为变异的位点全部来自早期错误（"
          f"{int((called_before & ~err).sum())} 个非错误位点过线）；"
          f"去重后过线 {int(called_after.sum())} 个")
    print("→ 失效条件 1 的量化：不去重时 1 个分子的测序/PCR 错误被算成 "
          f"{K} 条独立证据，Phred 从 {phred_tail(1, n, q):.1f} 抬到 "
          f"{phred_tail(K, D, q):.1f}；MarkDuplicates 把这 {K} 票压回 1 票。")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        check("手算锚：去重前 Phred = phred_tail(K, D, q) > 60",
              phred_tail(K, D, q) > 60.0)
        check("手算锚：去重后 Phred = phred_tail(1, n, q) < 10",
              phred_tail(1, n, q) < 10.0)
        check("错误位点去重前 ALT 支持均值 == K",
              abs(x_before[err].mean() - K) < 1e-9)
        check("错误位点去重后 ALT 支持均值 == 1",
              abs(x_after[err].mean() - 1.0) < 1e-9)
        check("去重前判为变异 ⇔ 该位点有早期错误（无非错误位点过线）",
              int((called_before & ~err).sum()) == 0
              and bool((called_before == err).all()))
        check("去重后判为变异数 == 0（min_alt 判据下）",
              int(called_after.sum()) == 0)
        check("表观重复率 == (K-1)/D", abs(dup_rate - (K - 1) / D) < 1e-12)
        check("早期错误位点占比 == locus-error-rate（大数口径）",
              abs(err.mean() - args.locus_error_rate) < 0.03)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

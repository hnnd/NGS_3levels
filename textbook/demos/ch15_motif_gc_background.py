#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch15_motif_gc_background.py — motif 富集：背景序列不做 GC/长度匹配制造假富集（合成算例）

服务章节：第 15 章 §15.4 概念与方法（HOMER motif 分析与背景序列匹配）、
§15.5 失效条件第 4 条「motif 富集的背景序列与前景 GC 不匹配制造假富集」。
源讲义：m05 §4.6、⑤ 步骤 6、⑦ 第 5 条、⑥ 6.6、⑨ 错误 2 末段。

机制（讲义 §4.6 / ⑦ 第 5 条）：
  peak 区（启动子/增强子）的 GC 含量系统性高于基因组平均（启动子富 CpG）。
  已知 motif 富集检验 = 比较「前景序列带 motif 的比例」与「背景序列带 motif 的比例」
  （超几何/二项口径，讲义 ⑦ 第 5 条；HOMER 的 known motif 富集见 Heinz 2010，⑪）。
  若背景不做 GC 与长度匹配，富集到的只是「peak 区 GC 偏高」这一事实：
  GC-rich motif（如 SP1/KLF 的 GC-box）在 GC 高的序列里随机出现率本来就高，
  背景比例被低估 → 假富集、且 p 值极小。HOMER 默认自动生成 GC 与长度匹配的
  背景（讲义 ⑤ 步骤 6；HOMER 官方文档口径）——你必须知道它在做这件事。

模型（合成，非 PRJDB36269 或任何真实样本）：
  * 两个合成 motif，各为 6-mer，扫描 300 bp 序列判定「出现 ≥1 次」：
      GCbox = "GCGCGC"（GC-rich，无生物学：出现概率只随序列 GC 含量走）
      NeuM  = "ATGTAC"（GC 中性，真生物学：peak 里 20%、背景里 10%）
  * 前景 peak 序列 n=2000：GC 含量 0.55（peak 区启动子样偏高，讲义 §4.6 事实的合成化）
  * 背景两口径各 n=2000：
      匹配背景（HOMER 默认口径）：与前景同 GC（0.55）、同长度
      随机背景（错误口径）：基因组平均 GC 0.40
  * 检验：2×2 列联超几何——总体 = 前景+背景（4 000），成功态 = 两边命中总数，
    抽 n = 2 000（前景），P(X ≥ 前景命中数)；讲义 ⑦ 第 5 条「超几何/二项」口径。

参数（--help 可见）：
  --n-seq       前景/背景序列条数（默认 2000；n=500 时检验功效不足、对照不 decisive）
  --seq-len     序列长度 bp（默认 300）
  --gc-peak     前景 peak 区 GC（默认 0.55）
  --gc-genome   基因组平均 GC（默认 0.40）
  --p-neu-peak / --p-neu-bg   NeuM 在前景/背景的出现概率（默认 0.20 / 0.10）
  --seed        随机种子（默认 20260829）

正文引用的输出：
  - Part 0 手算规则：超几何 P(X≥k) = 1 − Σ_{i<k} C(K,i)C(N−K,n−i)/C(N,n)，
    手算例 N=12、K=5、n=4、k=3 → 75/495 = 0.152（scipy 对照）；
  - Part 1：同一前景、两种背景下两个 motif 的富集倍数与超几何 p——
    GCbox 在随机背景下假富集（p 极小）、在匹配背景下消失；NeuM 两口径都显著
    （GC 中性 → 背景口径不影响）。

依赖：Python 标准库 + numpy + scipy。
合成算例：所有序列与 motif 出现事件均为随机数生成器产物，与任何真实样本无关。
"""
import argparse
import sys
from math import comb

import numpy as np
from scipy import stats

SEED = 20260829
GCBOX = "GCGCGC"
NEUM = "ATGTAC"


def hypergeom_sf_hand(k, N, K, n):
    """P(X ≥ k)，X ~ Hypergeometric(总体 N、成功态 K、抽 n 个)。手算实现。"""
    denom = comb(N, n)
    return sum(comb(K, i) * comb(N - K, n - i) for i in range(k, min(K, n) + 1)) / denom


def simulate_sequences(rng, n, gc, seq_len):
    """iid 序列：P(A)=P(T)=(1−gc)/2，P(C)=P(G)=gc/2（A,C,G,T 顺序）。"""
    probs = [(1 - gc) / 2, gc / 2, gc / 2, (1 - gc) / 2]   # A C G T
    return rng.choice(np.array(list("ACGT")), size=(n, seq_len), p=probs)


def motif_hits(seqs, motif):
    """每条序列是否包含 motif（≥1 次，无允许错配的最简扫描）。"""
    hits = np.zeros(len(seqs), dtype=bool)
    for i, s in enumerate(seqs):
        hits[i] = motif in "".join(s)
    return hits


def main():
    ap = argparse.ArgumentParser(
        description="motif 富集背景序列不做 GC 匹配 → 假富集（合成算例；服务"
                    "第 15 章失效条件 4，对齐讲义 m05 §4.6 / ⑦ 第 5 条）")
    ap.add_argument("--n-seq", type=int, default=2000,
                    help="前景/背景序列条数（默认 2000；500 时超几何功效不足、对照不 decisive）")
    ap.add_argument("--seq-len", type=int, default=300)
    ap.add_argument("--gc-peak", type=float, default=0.55)
    ap.add_argument("--gc-genome", type=float, default=0.40)
    ap.add_argument("--p-neu-peak", type=float, default=0.20)
    ap.add_argument("--p-neu-bg", type=float, default=0.10)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    # ---------------- Part 0：手算规则 ----------------
    print("=" * 78)
    print("[Part 0 · 手算规则] 超几何检验 P(X≥k) = 1 − Σ_{i<k} C(K,i)C(N−K,n−i)/C(N,n)")
    print("=" * 78)
    N0, K0, n0, k0 = 12, 5, 4, 3
    p_hand = (comb(K0, k0) * comb(N0 - K0, n0 - k0) + comb(K0, k0 + 1)
              * comb(N0 - K0, n0 - k0 - 1)) / comb(N0, n0)
    p_scipy = float(stats.hypergeom.sf(k0 - 1, N0, K0, n0))
    print(f"  手算例：N={N0}、K={K0}、n={n0}、k={k0}")
    print(f"  P(X≥3) = [C({K0},3)C({N0-K0},{n0-k0}) + C({K0},4)C({N0-K0},{n0-k0-1})]"
          f" / C({N0},{n0}) = {p_hand:.3f}")
    print(f"  scipy 对照 = {p_scipy:.3f}（一致：{abs(p_hand - p_scipy) < 1e-12}）")
    print("  判读：背景集 N 与 K 决定「随机期望命中」n·K/N——背景 GC 不对齐，")
    print("        K/N（motif 背景出现率）就被系统性错估，同一个 k 的 p 随之漂移。")

    # ---------------- Part 1：两种背景口径 ----------------
    print()
    print("=" * 78)
    print("[Part 1 · 合成算例] 同一前景，匹配背景 vs 随机背景")
    print("=" * 78)
    seq_peak = simulate_sequences(rng, args.n_seq, args.gc_peak, args.seq_len)
    seq_bg_match = simulate_sequences(rng, args.n_seq, args.gc_peak, args.seq_len)
    seq_bg_rand = simulate_sequences(rng, args.n_seq, args.gc_genome, args.seq_len)
    gc_of = lambda a: float(np.isin(a, ["C", "G"]).mean())
    print(f"  实测 GC：前景 {gc_of(seq_peak):.3f}（设定 {args.gc_peak}）；"
          f"随机背景 {gc_of(seq_bg_rand):.3f}（设定 {args.gc_genome}）")
    # NeuM（真生物学）：按设定概率注入（GC 中性）
    hits_neu_peak = rng.random(args.n_seq) < args.p_neu_peak
    hits_neu_match = rng.random(args.n_seq) < args.p_neu_bg
    hits_neu_rand = rng.random(args.n_seq) < args.p_neu_bg
    # GCbox（无生物学）：出现完全由序列 GC 决定——扫描真实序列
    hits_gc_peak = motif_hits(seq_peak, GCBOX)
    hits_gc_match = motif_hits(seq_bg_match, GCBOX)
    hits_gc_rand = motif_hits(seq_bg_rand, GCBOX)

    def row(name, hp, hb):
        """2×2 列联超几何：总体 = 前景+背景（2N），成功态 = 两边命中总数，
        抽 n = N（前景），观察 k = 前景命中数。P(X≥k)。"""
        k = int(hp.sum())
        K = int(hb.sum())
        n = args.n_seq
        N_pool = 2 * n
        fold = (k / n) / max(K / n, 1e-12)
        p = float(stats.hypergeom.sf(k - 1, N_pool, k + K, n))
        return name, k, K, fold, p

    results = {}
    for motif_name, hp, hb_m, hb_r in [
            (f"GCbox（GC-rich 诱饵，无生物学）", hits_gc_peak, hits_gc_match, hits_gc_rand),
            ("NeuM（GC 中性，真富集 20% vs 10%）", hits_neu_peak, hits_neu_match, hits_neu_rand)]:
        r_m = row(motif_name, hp, hb_m)
        r_r = row(motif_name, hp, hb_r)
        results[motif_name] = (r_m, r_r)
        print(f"  {motif_name}")
        print(f"    前景命中 {r_m[1]}/{args.n_seq}（{r_m[1]/args.n_seq:.0%}）")
        print(f"    匹配背景（GC={args.gc_peak}）：背景命中 {r_m[2]}/{args.n_seq}（"
              f"{r_m[2]/args.n_seq:.0%}）→ 富集 {r_m[3]:.2f}×，p = {r_m[4]:.3g}")
        print(f"    随机背景（GC={args.gc_genome}）：背景命中 {r_r[2]}/{args.n_seq}（"
              f"{r_r[2]/args.n_seq:.0%}）→ 富集 {r_r[3]:.2f}×，p = {r_r[4]:.3g}")

    # BH 跨 2 motif × 2 背景（演示最小规模）
    gc = results["GCbox（GC-rich 诱饵，无生物学）"]
    neu = results["NeuM（GC 中性，真富集 20% vs 10%）"]
    print()
    print("  判读（对齐讲义 §4.6 / ⑥ 6.6「不对的样子」①）：")
    print(f"  · GCbox 的出现率只随 GC 走：前景 55% GC 下 {gc[0][1]/args.n_seq:.0%}；"
          f"匹配背景同为 55% GC，出现率 {gc[0][2]/args.n_seq:.0%} ≈ 前景"
          f" → 富集 {gc[0][3]:.2f}×，p = {gc[0][4]:.3g}（不显著，诱饵被正确放过）；")
    print(f"    随机背景只有 40% GC，出现率 {gc[1][2]/args.n_seq:.0%} → 假富集 "
          f"{gc[1][3]:.2f}×，p = {gc[1][4]:.3g}——结果表上一个 p 极小的 Top motif，"
          f"生物学信息量 = 0。")
    print(f"  · NeuM 是 GC 中性的真信号：两口径下都显著"
          f"（匹配 p = {neu[0][4]:.3g}，随机 p = {neu[1][4]:.3g}），"
          f"背景口径不影响它——受影响的是 GC-rich 诱饵的排序。")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        check(f"手算超几何与 scipy 一致（|{p_hand:.3f} − {p_scipy:.3f}| < 1e-12）",
              abs(p_hand - p_scipy) < 1e-12)
        gc_m, gc_r = gc
        neu_m, neu_r = neu
        check("合成世界 GC 口径自洽：实测随机背景 GC < 前景 GC",
              gc_of(seq_bg_rand) < gc_of(seq_peak) - 0.05)
        check(f"GCbox 匹配背景不显著（p = {gc_m[4]:.3g} > 0.05，富集 "
              f"{gc_m[3]:.2f}× < 1.3×）", gc_m[4] > 0.05 and gc_m[3] < 1.3)
        check(f"GCbox 随机背景假富集（p = {gc_r[4]:.3g} < 1e-6，富集 "
              f"{gc_r[3]:.2f}× ≥ 2×）", gc_r[4] < 1e-6 and gc_r[3] >= 2)
        check(f"假富集倍数被 GC 差放大：随机背景富集 {gc_r[3]:.2f}× ≥ 1.5 × "
              f"匹配背景 {gc_m[3]:.2f}×", gc_r[3] >= 1.5 * max(gc_m[3], 0.01))
        check(f"NeuM 两口径都显著（匹配 p = {neu_m[4]:.3g}，随机 p = {neu_r[4]:.3g}，"
              f"均 < 0.01）", neu_m[4] < 0.01 and neu_r[4] < 0.01)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

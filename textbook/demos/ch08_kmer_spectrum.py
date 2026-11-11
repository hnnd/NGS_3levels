#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch08_kmer_spectrum.py — 合成 k-mer 频率谱：峰位、错误尾与基因组大小估计（合成算例）

服务章节：第 8 章 §8.4「k-mer 频率谱」概念小节、§8.5 失效条件第 3 条
（高错误率长读长不能直接做 k-mer survey）。

数据性质：【合成算例】基因组为固定种子的均匀随机 DNA 序列，与任何真实菌株无关；
所有输出不得写成真实样本（如 Xoo CIX4481/CIX2779）的实测结果。

正文引用的输出：
  - 主峰测序深度 C_k 与错误尾（深度 1-3）占比 → 讲义 u06 §4.1 谱形四成分
  - G ≈ Σ(i·N_i, i≥min_depth) / C_k           → u06 §4.1 基因组大小换算公式
  - 4^11 / 4^21 空间容量对照                    → u06 §4.2（4^11≈4.2×10^6、4^21≈4.4×10^12）
  - --het-rate>0 时主峰左侧 ≈C_k/2 的杂合半峰   → u06 §4.1「细菌出现半峰=混染警报」、m02 §4.2

参数含义：
  --genome-size  单倍体基因组长度（bp），合成基因组的真实 G
  --depth        标称测序深度（×）；--het-rate>0 时两套单倍型各得一半
  --read-len     读段长度（bp）；--k k 值（奇数为佳，避免 k-mer 与反向互补相同）
  --error-rate   单碱基替换错误率（合成测序错误）
  --het-rate     两套单倍型的分歧率；0=严格单倍体（细菌），>0 模拟杂合二倍体/混染
  --min-depth    估计公式剔除的错误尾深度下界（深度 < 此值视为错误尾）
  --seed         随机种子（固定，保证可复现）
"""
import argparse
import sys

import numpy as np

# 碱基编码 A=0,C=1,G=2,T=3；互补 = 3 - code
COMP = np.array([3, 2, 1, 0], dtype=np.int64)


def random_genome(rng, n):
    return rng.integers(0, 4, n, dtype=np.int8)


def mutate(genome, rate, rng):
    """按 rate 引入随机替换突变，返回新序列。"""
    if rate <= 0:
        return genome.copy()
    m = rng.random(genome.shape) < rate
    out = genome.copy()
    if m.any():
        out[m] = (out[m] + rng.integers(1, 4, int(m.sum()))) % 4
    return out


def simulate_reads(genome, depth, read_len, error_rate, rng):
    """均匀随机起点的合成读段（仅正链；对随机基因组统计上与双链等价）。"""
    n_reads = max(1, int(depth * genome.size / read_len))
    starts = rng.integers(0, genome.size - read_len + 1, n_reads)
    reads = np.stack([genome[s:s + read_len] for s in starts])
    if error_rate > 0:
        m = rng.random(reads.shape) < error_rate
        if m.any():
            reads[m] = (reads[m] + rng.integers(1, 4, int(m.sum()))) % 4
    return [r for r in reads]


def canonical_kmer_hashes(reads, k):
    """全部读段窗口的规范化（canonical）k-mer 整数哈希（MSB 优先，取正/反互补较小者）。"""
    pow4 = (4 ** np.arange(k - 1, -1, -1)).astype(np.int64)  # 4^(k-1)..4^0
    parts = []
    for r in reads:
        if r.size < k:
            continue
        c = r.astype(np.int64)
        fwd = np.convolve(c, pow4[::-1], mode="valid")
        rc = COMP[r[::-1]]
        rch = np.convolve(rc, pow4[::-1], mode="valid")
        parts.append(np.minimum(fwd, rch[::-1]))
    return np.concatenate(parts) if parts else np.empty(0, dtype=np.int64)


def smooth(x, w=5):
    ker = np.ones(w) / w
    return np.convolve(x, ker, mode="same")


def local_maxima(x, min_height):
    idx = []
    for i in range(1, len(x) - 1):
        if x[i] >= min_height and x[i] >= x[i - 1] and x[i] >= x[i + 1] \
                and (x[i] > x[i - 1] or x[i] > x[i + 1]):
            idx.append(i)
    return idx


def run_spectrum(genome_size, depth, read_len, k, error_rate, het_rate,
                 min_depth, seed, tag=""):
    """跑一次合成勘测，打印报告并返回关键数字。"""
    rng = np.random.default_rng(seed)
    haplotypes = [random_genome(rng, genome_size)]
    if het_rate > 0:
        haplotypes.append(mutate(haplotypes[0], het_rate, rng))

    all_hashes = []
    per_hap_depth = depth / len(haplotypes)
    for hap in haplotypes:
        reads = simulate_reads(hap, per_hap_depth, read_len, error_rate, rng)
        all_hashes.append(canonical_kmer_hashes(reads, k))
    hashes = np.concatenate(all_hashes)

    _, counts = np.unique(hashes, return_counts=True)
    maxc = int(counts.max())
    hist = np.bincount(counts, minlength=maxc + 1)  # hist[i] = 恰好出现 i 次的 k-mer 种类数
    distinct = int(hist[1:].sum())

    smin = min_depth
    sm = smooth(hist.astype(float))
    # 显著局部峰（只在 ≥min_depth 的范围内找，错误尾不参与）；
    # 主峰 C_k 取「深度最大的显著峰」：单倍体只有主峰一个；
    # 杂合模式下 ≈C_k/2 的杂合峰常更高，但主峰永远在更深处
    body = sm[smin:]
    sig = [smin + p for p in local_maxima(body, min_height=0.08 * body.max())] \
        if body.max() > 0 else []
    if not sig:  # 深度不足等病态情形下退回全局最大
        sig = [int(smin + np.argmax(body))]
    peak = max(sig)
    err_tail_share = hist[1:min_depth].sum() / distinct
    mass = float(sum(i * hist[i] for i in range(min_depth, len(hist))))
    g_est = mass / peak

    print(f"[{tag}] 合成基因组 G={genome_size:,} bp，标称深度 {depth}×，读长 {read_len} bp，"
          f"k={k}，错误率 {error_rate}，杂合/分歧率 {het_rate}，种子 {seed}")
    print(f"  空间容量 4^11=4,194,304  4^17=17,179,869,184  4^21=4,398,046,511,104  "
          f"4^25=1,125,899,906,842,624；本例 4^{k}={4**k:,.0f}")
    eff = depth * (read_len - k + 1) / read_len
    print(f"  不同 k-mer 种类数 = {distinct:,}；主峰深度 C_k = {peak}×")
    print(f"  （C_k 的理论期望 ≈ 标称深度×(L−k+1)/L×(1−e)^k = {depth}×"
          f"{(read_len-k+1)/read_len:.2f}×{(1-error_rate)**k:.2f} ≈ {eff*(1-error_rate)**k:.1f}×；"
          f"含错 k-mer 向低频尾坍缩）")
    if (1 - error_rate) ** k < 0.30:
        print(f"  警告：理论主峰深度 ≈{eff*(1-error_rate)**k:.1f}× 过低，谱形将失去清晰主峰——"
              f"正是失效条件第 3 条（高错误率长读长不能做 k-mer survey）的合成复现")
    print(f"  错误尾占比（深度 1-{min_depth-1} 的种类数份额）= {err_tail_share:.1%}")
    print(f"  基因组大小估计 G_est = Σ(i·N_i, i≥{min_depth}) / C_k = {g_est:,.0f} bp"
          f"（真值 {genome_size:,} bp，偏差 {abs(g_est-genome_size)/genome_size:.1%}）")

    result = dict(peak=peak, err_tail_share=float(err_tail_share), g_est=g_est,
                  distinct=distinct, het_peak=None, het_height=None)
    top = max(sm[p] for p in sig)
    print(f"  检出显著峰（深度×, 相对高度）："
          + "  ".join(f"{p}×({sm[p]/top:.0%})" for p in sorted(sig)))
    if het_rate > 0:
        half = [p for p in sig if 0.35 * peak < p < 0.65 * peak]
        if half:
            hp = max(half, key=lambda p: sm[p])
            result["het_peak"] = int(hp)
            result["het_height"] = float(sm[hp] / sm[peak])
            print(f"  杂合半峰：主峰 C_k/2 ≈ {peak/2:.1f}× 处检出峰 深度={hp}×（≈{hp/peak:.2f}·C_k），"
                  f"相对主峰高度 {result['het_height']:.0%}"
                  f" —— 细菌单倍体数据出现此峰即混染警报（u06 §4.1）")
        else:
            print("  杂合半峰：未检出（本次合成参数下肩峰不显著）")
    print()
    return result


def selftest():
    """固定种子复现正文引用的关键数字。"""
    print("=== SELFTEST（合成算例，固定种子）===")
    a = run_spectrum(genome_size=40000, depth=30, read_len=100, k=21,
                     error_rate=0.01, het_rate=0.0, min_depth=4, seed=20261102,
                     tag="单倍体")
    # C_k 期望 ≈ 30×(80/100)×0.99^21 ≈ 19.4，主峰允差 ±4
    assert 15 <= a["peak"] <= 24, f"主峰应约 19×（15-24），得 {a['peak']}"
    assert a["err_tail_share"] > 0.60, "错误尾应占绝大多数种类数"
    assert abs(a["g_est"] - 40000) / 40000 < 0.10, "G 估计应接近真值"
    b = run_spectrum(genome_size=40000, depth=60, read_len=100, k=21,
                     error_rate=0.005, het_rate=0.02, min_depth=4, seed=20261103,
                     tag="二倍体/混染")
    # 每单倍型深度 30×：(L−k+1)/L=0.8，主峰期望 ≈ 60×0.8×0.995^21 ≈ 43×，杂合半峰 ≈ 21-22×
    assert 38 <= b["peak"] <= 48, f"杂合模式下主峰应 ≈43×（38-48），得 {b['peak']}"
    assert b["het_peak"] is not None, "杂合半峰应可检出"
    assert 0.40 * b["peak"] < b["het_peak"] < 0.60 * b["peak"]
    assert abs(b["g_est"] - 40000) / 40000 < 0.10, "杂合模式下 G 估计应接近单倍体真值"
    print("SELFTEST PASS：主峰位置、错误尾占比、G 估计、杂合半峰均符合预期")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="合成 k-mer 频率谱演示（合成算例，非真实样本结果）")
    ap.add_argument("--genome-size", type=int, default=40000)
    ap.add_argument("--depth", type=float, default=30)
    ap.add_argument("--read-len", type=int, default=100)
    ap.add_argument("--k", type=int, default=21)
    ap.add_argument("--error-rate", type=float, default=0.01)
    ap.add_argument("--het-rate", type=float, default=0.0,
                    help="两套单倍型分歧率；0=单倍体，>0 模拟杂合/混染")
    ap.add_argument("--min-depth", type=int, default=4)
    ap.add_argument("--seed", type=int, default=20261102)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    run_spectrum(args.genome_size, args.depth, args.read_len, args.k,
                 args.error_rate, args.het_rate, args.min_depth, args.seed)
    return 0


if __name__ == "__main__":
    sys.exit(main())

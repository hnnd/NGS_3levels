#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch08_debruijn_repeat.py — 合成 de Bruijn 图：k−1 与重复长度的三种关系（合成算例）

服务章节：第 8 章 §8.4「OLC 与 de Bruijn 图」概念小节、§8.5 失效条件第 1 条
（重复长于读长或 k−1 时组装在重复处断开或塌缩）。

数据性质：【合成算例】基因组为固定种子的均匀随机 DNA 序列（U1+R+U2+R+U3），
与任何真实菌株无关；输出不得写成真实样本的实测结果。

正文引用的输出：
  - k−1 < R：共享 k-mer 种数 = R−k+1（>0），拷贝在图内叠合、欧拉路径不唯一
    → 组装在重复处断开或塌缩（失效条件第 1 条的机制演示）
  - k−1 = R：共享 k-mer = 0（两条拷贝的配对其实唯一），但重复整体构成一个
    2 入 2 出的共享节点，保守组装器仍在此截断 contig（边界情形）
  - k−1 > R：全部 (k−1)-mer 唯一，图为单链，组装无歧义
  - OLC/读长对照判据：能完整跨过一条重复拷贝的读段起始位点数 = max(0, L−R)
    —— L ≤ R 时信息不存在，任何算法都无法排他地定两侧连接

参数含义：
  --repeat-len  重复序列 R 的长度（bp），两拷贝完全一致
  --flank-len   两侧唯一序列 U1/U2/U3 的长度（bp）
  --k-min/--k-max  扫描的 k 值范围（覆盖 k−1 小于/等于/大于 R 三种情形）
  --read-len-min/--read-len-max  扫描的读长 L 范围（OLC 判据演示）
  --seed        随机种子（固定，保证可复现）
"""
import argparse
import sys
from collections import Counter

import numpy as np

BASES = np.array(list("ACGT"))


def random_dna(rng, n):
    return "".join(BASES[rng.integers(0, 4, n)])


def build_genome(rng, flank_len, repeat_len):
    """构造 U1 + R + U2 + R + U3；保证 R 不出现在侧翼中（重采样直至满足）。"""
    while True:
        u1, u2, u3 = (random_dna(rng, flank_len) for _ in range(3))
        r = random_dna(rng, repeat_len)
        if r not in u1 and r not in u2 and r not in u3:
            break
    genome = u1 + r + u2 + r + u3
    rep1 = (len(u1), len(u1) + repeat_len)          # 第一条重复拷贝区间
    rep2 = (rep1[1] + flank_len, rep1[1] + flank_len + repeat_len)
    return genome, rep1, rep2


def dbg_stats(genome, k):
    """返回（共享 k-mer 种数, 多拷贝节点数, 分叉节点数）。完美覆盖：图直接从真实基因组建。

    - 共享 k-mer：出现 ≥2 次的 k-mer，存在当且仅当重复长度 R ≥ k（即 k−1 < R）；
      此时两条拷贝在图内叠合，欧拉路径不唯一（断开或错配的风险区）
    - 多拷贝节点：出现 ≥2 次的 (k−1)-mer 节点，存在当且仅当 R ≥ k−1
    - 分叉节点：多拷贝节点中入度或出度 >1 者——保守组装器在此截断 contig
    """
    kmers = {genome[i:i + k] for i in range(len(genome) - k + 1)}
    nodes = {genome[i:i + k - 1] for i in range(len(genome) - k + 2)}
    counts = Counter()
    for i in range(len(genome) - k + 1):
        counts[genome[i:i + k]] += 1
    for i in range(len(genome) - k + 2):
        counts[genome[i:i + k - 1]] += 1
    indeg, outdeg = Counter(), Counter()
    for km in kmers:
        outdeg[km[:-1]] += 1
        indeg[km[1:]] += 1
    shared = sum(1 for km in kmers if counts[km] > 1)
    dup_nodes = [n for n in nodes if counts[n] > 1]
    branches = sum(1 for n in dup_nodes
                   if indeg.get(n, 0) > 1 or outdeg.get(n, 0) > 1)
    return shared, len(dup_nodes), branches


def spanning_starts(repeat_len, read_len):
    """一条读长 L 的读段能完全覆盖一条重复拷贝的起始位点数：max(0, L−R)。"""
    return max(0, read_len - repeat_len)


def run(repeat_len, flank_len, k_min, k_max, read_min, read_max, seed):
    rng = np.random.default_rng(seed)
    genome, rep1, rep2 = build_genome(rng, flank_len, repeat_len)
    g_len = len(genome)
    print(f"合成基因组 U1+R+U2+R+U3：全长 {g_len:,} bp，R={repeat_len} bp（两拷贝一致），"
          f"侧翼 {flank_len} bp，种子 {seed}")
    print(f"重复拷贝位置：[{rep1[0]},{rep1[1]}) 与 [{rep2[0]},{rep2[1]})（0-based 半开）\n")

    print("de Bruijn 图判据（节点=(k−1)-mer，边=k-mer，完美覆盖）：")
    print(f"{'k':>4} {'k−1':>5} {'k−1 vs R':>12} {'共享 k-mer':>10} {'多拷贝节点':>10} {'分叉节点':>8}  判读")
    boundary = {}
    for k in range(k_min, k_max + 1):
        shared, dup, branches = dbg_stats(genome, k)
        if k - 1 < repeat_len:
            rel = "k−1 < R"
            verdict = "重复坍缩：拷贝叠合、欧拉路径不唯一，断开或错配"
        elif k - 1 == repeat_len:
            rel = "k−1 = R"
            verdict = "边界：无共享 k-mer（配对唯一），但重复整体是 2/2 度共享节点，保守组装器仍在此断 contig"
        else:
            rel = "k−1 > R"
            verdict = "全部 (k−1)-mer 唯一：单链无歧义"
        boundary[k - 1 - repeat_len] = (shared, dup, branches)
        print(f"{k:>4} {k-1:>5} {rel:>12} {shared:>10} {dup:>10} {branches:>8}  {verdict}")

    print("\nOLC/读长判据（能完整跨越一条重复拷贝的读段起始位点，每条拷贝）：")
    print(f"{'读长 L':>7} {'L vs R':>10} {'跨重复起始位点':>14}")
    for L in range(read_min, read_max + 1, 10):
        n = spanning_starts(repeat_len, L)
        rel = "L ≤ R" if L <= repeat_len else "L > R"
        print(f"{L:>7} {rel:>10} {n:>14}"
              + ("  ← 信息不存在：任何算法都无法定两侧连接" if n == 0 else ""))
    print()
    return boundary


def selftest():
    print("=== SELFTEST（合成算例，固定种子）===")
    boundary = run(repeat_len=100, flank_len=300, k_min=97, k_max=105,
                   read_min=80, read_max=180, seed=20261102)
    lo = boundary[-3]   # k−1 = R−3（小于）
    eq = boundary[0]    # k−1 = R（等于，边界）
    hi = boundary[3]    # k−1 = R+3（大于）
    assert lo[0] > 0 and lo[2] > 0, "k−1 < R 时应有共享 k-mer 与分叉节点"
    assert eq[0] == 0 and eq[1] == 1 and eq[2] == 1, \
        "k−1 = R 时无共享 k-mer，但重复整体是 1 个 2/2 度共享（分叉）节点"
    assert hi[0] == 0 and hi[1] == 0 and hi[2] == 0, "k−1 > R 时应完全可分辨"
    assert spanning_starts(100, 100) == 0, "L = R 时没有读段能严格跨过整条重复"
    assert spanning_starts(100, 150) == 50, "L > R 时跨重复起始位点 = L−R"
    print("SELFTEST PASS：k−1 小于/等于/大于 R 三种情形与读长判据均符合预期")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="合成 de Bruijn 图重复分支演示（合成算例，非真实样本结果）")
    ap.add_argument("--repeat-len", type=int, default=100)
    ap.add_argument("--flank-len", type=int, default=300)
    ap.add_argument("--k-min", type=int, default=97)
    ap.add_argument("--k-max", type=int, default=105)
    ap.add_argument("--read-len-min", type=int, default=80)
    ap.add_argument("--read-len-max", type=int, default=180)
    ap.add_argument("--seed", type=int, default=20261102)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    run(args.repeat_len, args.flank_len, args.k_min, args.k_max,
        args.read_len_min, args.read_len_max, args.seed)
    return 0


if __name__ == "__main__":
    sys.exit(main())

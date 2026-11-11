#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch07_seed_extend.py — FM-index 倒序搜索玩具 + 种子-延伸最小实现与 -k 杠杆（合成算例）

服务章节：第 7 章 §7.4 概念与方法
  - ug 层：BWT/FM-index 直觉（倒序搜索、每碱基常数次查表，与参考长度无关）
  - ug 层：种子-延伸启发式（k-mer 索引 → 对角线链化 → 仿射罚分局部延伸）
  - -k 参数杠杆（讲义 u05 ④4.4 与 ⑩ 习题 4；bwa mem 默认 -k 19 已核 bwa 0.7.17
    源码 mem_opt_init()：o->min_seed_len = 19）

数据性质：【合成算例】参考基因组与读段全部由 numpy Generator(20261103) 生成，
不涉及任何真实基因组或真实测序数据；延伸打分取 bwa 默认口径（match +1 /
mismatch -4 / gap open 6 / gap extend 1，源码 mem_opt_init）。

正文引用的输出：
  - BANANA$ 的 BWT 末列 L = ANNB$AA（与讲义 u05 ④4.2 一致）；
    倒序搜索 ANA → 命中 2 行、原文位置 {1,3}；每次搜索 2·len(pattern) 次 Occ 查表
  - -k × 错误率扫描表（固定种子）：平均 MEM 数、无种子%（≥k 精确匹配一条都没有、
    必然丢失的读段比例）、延伸 DP 带宽窗口单元数 —— 「-k 盲目调大」的定量版
    （u05 ④4.4 与 ⑩ 习题 4；15% 错误档对应种间高度发散）。
    说明：扫描表不在原地执行 DP，窗口单元数是按 align_affine_global 的 band
    循环范围精确计数的（与真跑 DP 的单元计数 1:1，演示读段处已核对）；纯匹配
    的侧翼直通、不计窗口。
  - 演示读段（全长 150 bp、含 2 个 SNP）：CIGAR = 49M1M69M1M30M（M 含错配）、
    NM = 2、score = 140 —— 种子覆盖全长、空隙由仿射罚分 DP 填平

参数含义见 --help；固定随机种子，全部输出可复现。
"""
import argparse
import sys

import numpy as np

SEED = 20261103
COMPLEMENT = str.maketrans("ACGT", "TGCA")

# bwa 0.7.17 mem 默认打分口径（源码 mem_opt_init）：match +1 / mismatch -4 /
# gap open 6 / gap extend 1（空位长度 L 的代价 = open + L×extend）
MATCH_SCORE = 1
MISMATCH_PEN = 4
GAP_OPEN = 6
GAP_EXT = 1


# ---------------------------------------------------------------------------
# Part A：BWT / FM-index 玩具（讲义 u05 ④4.2–4.3 的可复算版本）
# ---------------------------------------------------------------------------

def bwt_rotations(s):
    """s 的全部循环轮转及其原串下标。"""
    return sorted(((s[i:] + s[:i], i) for i in range(len(s))))


def fm_index(s):
    """返回 (L, 排序轮转表, C, Occ)。Occ[c][i] = L 的前 i 个字符中 c 的次数。"""
    rots = bwt_rotations(s)
    mat = [r for r, _ in rots]
    starts = [i for _, i in rots]
    L = "".join(row[-1] for row in mat)
    alphabet = sorted(set(s))
    C = {c: sum(1 for ch in s if ch < c) for c in alphabet}
    Occ = {c: [0] * (len(s) + 1) for c in alphabet}
    for i, ch in enumerate(L):
        for c in alphabet:
            Occ[c][i + 1] = Occ[c][i] + (1 if ch == c else 0)
    return L, (mat, starts), C, Occ


def backward_search(s, pattern, C, Occ):
    """FM-index 倒序搜索。返回 (行区间 [sp, ep), 命中数, Occ 查表次数)。"""
    sp, ep, n_ops = 0, len(s), 0
    for ch in reversed(pattern):
        sp = C[ch] + Occ[ch][sp]
        ep = C[ch] + Occ[ch][ep]
        n_ops += 2
        if sp >= ep:
            return (sp, sp), 0, n_ops
    return (sp, ep), ep - sp, n_ops


def fm_positions(s, pattern):
    """返回 pattern 在 s 中的全部起始位置（用 LF-mapping 还原）。"""
    L, (mat, starts), C, Occ = fm_index(s)
    (sp, ep), n, _ = backward_search(s, pattern, C, Occ)
    return sorted(starts[sp:ep]), n


# ---------------------------------------------------------------------------
# Part B：种子-延伸最小实现（k-mer 索引 → 链化 → 仿射罚分局部延伸）
# ---------------------------------------------------------------------------

def make_genome(rng, n):
    return "".join(rng.choice(np.array(list("ACGT")), size=n))


def build_kmer_index(ref, k):
    """k-mer（bytes）→ 参考上起始位置列表（升序）。"""
    ref_b = ref.encode()
    index = {}
    for i in range(len(ref_b) - k + 1):
        index.setdefault(ref_b[i:i + k], []).append(i)
    return index


def make_reads(rng, genome, n_reads, read_len, err):
    """随机位置取 read_len 读段，逐碱基以 err 概率替换为随机异碱基（只含替换错误）。"""
    starts = rng.integers(0, len(genome) - read_len, size=n_reads)
    reads = []
    for st in starts:
        r = list(genome[st:st + read_len])
        for i in range(read_len):
            if rng.random() < err:
                r[i] = str(rng.choice(np.array(list("ACGT"))))
        reads.append(("".join(r), int(st)))
    return reads


def find_mems(read, ref, index, k):
    """所有长度 ≥ k 的极大精确匹配（简化 SMEM，集合与「逐 k-mer 延伸后去包含」等价）。

    利用 MEM 起点的充要条件裁剪：对命中 (i, pos)，若 i>0、pos>0 且
    read[i-1] == ref[pos-1]，则 (i, pos) 必在更大的 MEM (i-1, pos-1) 内部，
    跳过。每个 MEM 只在延伸运行起点向右延伸到失配为止。

    返回 [(qb, rb, len), ...]，qb/rb 分别为读段/参考上的 0-based 起点。
    """
    read_b, ref_b = read.encode(), ref.encode()
    n, m = len(read_b), len(ref_b)
    mems = []
    for i in range(n - k + 1):
        pos_list = index.get(read_b[i:i + k])
        if not pos_list:
            continue
        for pos in pos_list:
            if i > 0 and pos > 0 and read_b[i - 1] == ref_b[pos - 1]:
                continue  # 左扩一格仍匹配 → 属于更大 MEM，跳过
            j = i + k
            while j < n and pos + (j - i) < m and read_b[j] == ref_b[pos + (j - i)]:
                j += 1
            mems.append((i, pos, j - i))
    return mems


def chain_seeds(mems, w=100):
    """按对角线 rb-qb 贪心链化（同链要求读段与参考共线、间距差 ≤ w bp）。

    返回得分（种子长度和）最高的链。
    """
    by_diag = {}
    for qb, rb, ln in mems:
        by_diag.setdefault(rb - qb, []).append((qb, rb, ln))
    best = []
    for seeds in by_diag.values():
        seeds.sort()
        cur, cov = [], 0
        for s in seeds:
            if cur and (s[0] < cur[-1][0] + cur[-1][2] or s[1] < cur[-1][1] + cur[-1][2]):
                if s[2] > cur[-1][2]:  # 重叠时保留更长的种子
                    cov += s[2] - cur[-1][2]
                    cur[-1] = s
            else:
                cur.append(s)
                cov += s[2]
        if cov > sum(x[2] for x in best):
            best = cur
    return best


def align_affine_global(q, r, match=MATCH_SCORE, mismatch=MISMATCH_PEN,
                        gap_open=GAP_OPEN, gap_ext=GAP_EXT, band=None):
    """两端锚定的全局比对（仿射罚分，bwa 默认打分口径；带 band 限制）。

    用于种子链的空隙与两端延伸：q、r 两段都必须全程消耗。
    返回 (score, cigar, nm, dp_cells)。
    """
    n, m = len(q), len(r)
    if n == 0 or m == 0:
        return 0, "", 0, 0
    if band is None:
        band = abs(n - m) + 4
    NEG = -10 ** 9
    H = [[NEG] * (m + 1) for _ in range(n + 1)]
    E = [[NEG] * (m + 1) for _ in range(n + 1)]  # q 多出（参考空位）
    F = [[NEG] * (m + 1) for _ in range(n + 1)]  # r 多出（读段空位）
    ptr = [[""] * (m + 1) for _ in range(n + 1)]
    H[0][0] = 0
    for i in range(1, n + 1):
        H[i][0] = -gap_open - i * gap_ext
        E[i][0] = H[i][0]
        ptr[i][0] = "u"
    for j in range(1, m + 1):
        H[0][j] = -gap_open - j * gap_ext
        F[0][j] = H[0][j]
        ptr[0][j] = "l"
    cells = 0
    for i in range(1, n + 1):
        lo, hi = max(1, i - band), min(m, i + band)
        for j in range(lo, hi + 1):
            cells += 1
            s = match if q[i - 1] == r[j - 1] else -mismatch
            E[i][j] = max(H[i - 1][j] - gap_open - gap_ext, E[i - 1][j] - gap_ext)
            F[i][j] = max(H[i][j - 1] - gap_open - gap_ext, F[i][j - 1] - gap_ext)
            diag = H[i - 1][j - 1] + s
            v = max(diag, E[i][j], F[i][j])
            H[i][j] = v
            ptr[i][j] = "d" if v == diag else ("u" if v == E[i][j] else "l")
    i, j = n, m
    ops, nm = [], 0
    while i > 0 or j > 0:
        p = ptr[i][j]
        if p == "d":
            ops.append("=" if q[i - 1] == r[j - 1] else "X")
            nm += q[i - 1] != r[j - 1]
            i, j = i - 1, j - 1
        elif p == "u":
            ops.append("I")
            nm += 1
            i -= 1
        else:
            ops.append("D")
            nm += 1
            j -= 1
    ops.reverse()
    cigar, last, cnt = "", "", 0
    for o in ops:
        if o == last:
            cnt += 1
        else:
            if last:
                cigar += f"{cnt}{last}"
            last, cnt = o, 1
    if last:
        cigar += f"{cnt}{last}"
    return H[n][m], cigar, nm, cells


def extend_chain(read, ref, chain):
    """沿链拼接：种子段记 = 长；种子间空隙与两端 flanking 走带 band 的全局延伸
    （对应 bwa mem 从种子向读段两端 banded SW 的玩具版）。

    返回 (score, cigar, nm, dp_cells, coverage_bp)。
    """
    if not chain:
        return 0, "", 0, 0, 0
    score, nm, cells, cov = 0, 0, 0, 0
    cigar_parts = []

    def add_gap(q0, q1, r0, r1, orient):
        """orient: 'end'（左端 flanking，读段贴窗口右端）/ 'start'（右端 flanking）/
        'exact'（种子间空隙，两段等长对齐）。"""
        nonlocal score, nm, cells
        if q1 <= q0 and r1 <= r0:
            return
        qs, win = read[q0:q1], ref[r0:r1]
        L = len(qs)
        if L == 0:  # 纯缺失
            nm += len(win)
            score += -GAP_OPEN - len(win) * GAP_EXT
            cigar_parts.append(f"{len(win)}D")
            return
        if len(win) == 0:  # 纯插入
            nm += L
            score += -GAP_OPEN - L * GAP_EXT
            cigar_parts.append(f"{L}I")
            return
        same = ((orient == "end" and win[-L:] == qs)
                or (orient == "start" and win[:L] == qs)
                or (orient == "exact" and win == qs))
        if same:  # 无空位无错配的直通：绝大多数 flank 走这里，不建 DP 表
            score += L
            cigar_parts.append(f"{L}M")
            return
        gs, gc, gnm, gc_cells = align_affine_global(qs, win)
        score += gs
        nm += gnm
        cells += gc_cells
        if gc:
            cigar_parts.append(gc.replace("=", "M").replace("X", "M"))

    # 左端 flanking：首个种子向左延伸到读段起点（qb0=0 时无 flanking，pad 取 0）
    qb0, rb0, _ = chain[0]
    pad = min(rb0, qb0 + 8) if qb0 > 0 else 0
    add_gap(0, qb0, rb0 - pad, rb0, orient="end")
    prev_end_q, prev_end_r = 0, rb0 - pad
    for qb, rb, ln in chain:
        add_gap(prev_end_q, qb, prev_end_r, rb, orient="exact")
        cigar_parts.append(f"{ln}M")
        score += ln
        prev_end_q, prev_end_r = qb + ln, rb + ln
    # 右端 flanking：末个种子向右延伸到读段终点（tail_q=0 时同样取 0）
    m = len(read)
    tail_q = m - prev_end_q
    tail_r = min(len(ref) - prev_end_r, tail_q + 8) if tail_q > 0 else 0
    add_gap(prev_end_q, m, prev_end_r, prev_end_r + tail_r, orient="start")
    prev_end_q = m
    cov = m
    return score, "".join(cigar_parts), nm, cells, cov


def window_cells(gq, gr, band_pad=4):
    """带 band 全局 DP 实际触碰的单元数（band = |gq-gr|+band_pad；与
    align_affine_global 的循环范围一一对应）。gq 或 gr 为 0 时按纯插入/缺失
    解析处理，不占 DP 单元。"""
    if gq <= 0 or gr <= 0:
        return 0
    band = abs(gq - gr) + band_pad
    total = 0
    for i in range(1, gq + 1):
        lo = max(1, i - band)
        hi = min(gr, i + band)
        if hi >= lo:
            total += hi - lo + 1
    return total


def chain_work_estimate(read, ref, chain):
    """沿最佳链统计延伸工作量：每个空隙/侧翼若纯匹配直通则 0 单元，否则计
    带宽窗口单元数。与 extend_chain 的 fast-path 规则一致。"""
    if not chain:
        return 0
    cells = 0
    qb0, rb0, _ = chain[0]
    pad = min(rb0, qb0 + 8) if qb0 > 0 else 0
    if qb0 > 0 and read[0:qb0] != ref[rb0 - qb0:rb0]:
        cells += window_cells(qb0, pad)
    prev_q, prev_r = 0, rb0 - pad
    for qb, rb, ln in chain:
        gq, gr = qb - prev_q, rb - prev_r
        if (gq > 0 or gr > 0) and read[prev_q:qb] != ref[prev_r:rb]:
            cells += window_cells(gq, gr)
        prev_q, prev_r = qb + ln, rb + ln
    m = len(read)
    tail_q = m - prev_q
    tail_r = min(len(ref) - prev_r, tail_q + 8) if tail_q > 0 else 0
    if tail_q > 0 and read[prev_q:m] != ref[prev_r:prev_r + tail_q]:
        cells += window_cells(tail_q, tail_r)
    return cells


def sweep(genome, reads_by_err, k_list, w):
    """k × 错误率扫描。返回 {(k, err): (mean_mems, unseeded_pct, dp_window_cells)}。

    不在扫描中真跑 DP：DP 列是带宽窗口单元数的精确计数（演示读段的真 DP 在
    main() 里单独跑并核对 CIGAR/NM/score）。
    """
    results = {}
    for err, reads in reads_by_err.items():
        for k in k_list:
            index = build_kmer_index(genome, k)
            n_mem_tot = n_unseeded = dp_tot = 0
            for read, _ in reads:
                mems = find_mems(read, genome, index, k)
                n_mem_tot += len(mems)
                if not mems:
                    n_unseeded += 1
                    continue
                chain = chain_seeds(mems, w=w)
                dp_tot += chain_work_estimate(read, genome, chain)
            results[(k, err)] = (
                n_mem_tot / len(reads), n_unseeded / len(reads) * 100.0, dp_tot)
    return results


def main():
    ap = argparse.ArgumentParser(
        description="FM-index 倒序搜索玩具 + 种子-延伸最小实现与 -k 杠杆（合成算例）")
    ap.add_argument("--seed", type=int, default=SEED, help="随机种子（默认 20261103）")
    ap.add_argument("--genome-len", type=int, default=20000, help="合成参考长度 bp")
    ap.add_argument("--reads", type=int, default=400, help="每个错误率档的读段数")
    ap.add_argument("--read-len", type=int, default=150, help="读段长度 bp")
    ap.add_argument("--k-sweep", default="11,15,19,25,32", help="扫描的种子长度 k 列表")
    ap.add_argument("--error-rates", default="0.01,0.05,0.10,0.15",
                    help="逐碱基替换错误率（0.15 对应「种间高度发散」档）")
    ap.add_argument("--chain-w", type=int, default=100, help="链化允许的最大对角线漂移 bp")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    k_list = [int(x) for x in args.k_sweep.split(",")]
    err_list = [float(x) for x in args.error_rates.split(",")]
    rng = np.random.default_rng(args.seed)

    print("=" * 72)
    print("[Part A] BWT / FM-index 玩具：BANANA$（讲义 u05 ④4.2–4.3 的可复算版本）")
    print("=" * 72)
    s = "BANANA$"
    L, (mat, starts), C, Occ = fm_index(s)
    print("轮转矩阵排序后：")
    for row in mat:
        print("   ", row)
    print(f"BWT 末列 L = {L}（讲义值 ANNB$AA，一致：{L == 'ANNB$AA'}）")
    for pat in ("ANA", "BAN", "NAB"):
        (sp, ep), n, n_ops = backward_search(s, pat, C, Occ)
        pos = sorted(starts[sp:ep]) if n else []
        print(f"倒序搜索 {pat!r}: 命中 {n} 行，原文位置 {pos}，Occ 查表 {n_ops} 次"
              f"（= 2×{len(pat)}，每碱基常数次、与参考长度无关）")

    print()
    print("=" * 72)
    print("[Part B] 种子-延伸最小实现：k-mer 索引 → 对角线链化 → 仿射罚分局部延伸")
    print("=" * 72)
    genome = make_genome(rng, args.genome_len)
    print(f"合成参考: {args.genome_len} bp（seed={args.seed}，iid 随机）")

    # 演示读段：从参考取一条 150 bp，人为引入 2 个 SNP
    demo_start = 3000
    demo = list(genome[demo_start:demo_start + args.read_len])
    demo[49] = {"A": "C", "C": "G", "G": "T", "T": "A"}[demo[49]]
    demo[119] = {"A": "G", "C": "A", "G": "C", "T": "G"}[demo[119]]
    demo = "".join(demo)
    idx19 = build_kmer_index(genome, 19)
    mems = find_mems(demo, genome, idx19, 19)
    chain = chain_seeds(mems, w=args.chain_w)
    score, cigar, nm, cells, cov = extend_chain(demo, genome, chain)
    print(f"演示读段 150 bp（2 个 SNP，k=19）：MEM {len(mems)} 条，链 {len(chain)} 段")
    print(f"  比对 score={score}，CIGAR={cigar}，NM={nm}（覆盖 {cov}/{args.read_len} bp，"
          f"延伸 DP {cells} 单元）")
    print("  （CIGAR 中的 M 含错配——2 个 SNP 都在 M 段里；M≠完全匹配是第 5 章的主题）")

    print()
    print("[k × 错误率扫描] 每档读段数 =", args.reads,
          "（无种子% = 连一条 ≥k 精确匹配都找不到、必然丢失的读段比例）")
    reads_by_err = {
        e: make_reads(np.random.default_rng(args.seed + int(e * 1000)),
                      genome, args.reads, args.read_len, e)
        for e in err_list}
    results = sweep(genome, reads_by_err, k_list, args.chain_w)
    header = f"{'k':>4} {'err':>6} {'平均MEM/读段':>12} {'无种子%':>8} {'DP窗口单元':>12}"
    print(header)
    print("-" * len(header))
    for e in err_list:
        for k in k_list:
            ms, unseeded, dp = results[(k, e)]
            print(f"{k:>4} {e:>6.0%} {ms:>12.2f} {unseeded:>8.2f} {dp:>12d}")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        check("BWT 末列 L == ANNB$AA", L == "ANNB$AA")
        (sp, ep), n, ops = backward_search(s, "ANA", C, Occ)
        check("ANA 命中 2 行", n == 2)
        check("ANA 原文位置 {1,3}", sorted(starts[sp:ep]) == [1, 3])
        check("ANA 查表 6 次 = 2×3", ops == 6)
        (sp2, ep2), n2, _ = backward_search(s, "BAN", C, Occ)
        check("BAN 命中 1 行于位置 0", n2 == 1 and starts[sp2:ep2] == [0])
        (sp3, ep3), n3, _ = backward_search(s, "NAB", C, Occ)
        check("NAB 命中 0 行", n3 == 0)
        check("演示读段 CIGAR=49M1M69M1M30M（M 含 2 个错配）",
              cigar == "49M1M69M1M30M")
        check("演示读段 NM=2", nm == 2)
        check("演示读段 score=140（148-2×4）", score == 140)
        check("演示读段覆盖 150/150 bp", cov == 150)
        check("window_cells(1,1)=1，与真 DP 单元数一致",
              window_cells(1, 1) == 1 and cells == 2)
        check("window_cells(3,3)=9（带内全矩阵）", window_cells(3, 3) == 9)
        max_err = max(err_list)
        # 复现锚：2026-11-03 ta（Python 3.10.12 / numpy 2.2.6）现跑记录的常数
        anchors = {0.01: (1.72, 0.00), 0.05: (2.83, 0.00),
                   0.10: (2.52, 1.00), 0.15: (1.66, 10.25)}
        for e in err_list:
            ms1, unseeded1, _ = results[(19, e)]
            em, eu = anchors[e]
            check(f"k=19, err={e:.0%}: 平均 MEM/读段 == {em}（现跑 {ms1:.2f}）",
                  round(ms1, 2) == em)
            check(f"k=19, err={e:.0%}: 无种子% == {eu}（现跑 {unseeded1:.2f}）",
                  round(unseeded1, 2) == eu)
        dp_anchors = {(19, 0.01): 36882, (11, 0.15): 446711, (32, 0.15): 423881}
        for kk_ee, dv in dp_anchors.items():
            check(f"DP窗口单元 {kk_ee} == {dv}（现跑 {results[kk_ee][2]}）",
                  results[kk_ee][2] == dv)
        hi_32 = results[(32, max_err)][1]
        hi_19 = results[(19, max_err)][1]
        hi_11 = results[(11, max_err)][1]
        check(f"最高错误率({max_err:.0%})下无种子%: k=32({hi_32:.2f}) > k=19({hi_19:.2f})"
              f" > k=11({hi_11:.2f})", hi_32 > hi_19 > hi_11)
        dp_15_11 = results[(11, 0.15)][2]
        dp_15_32 = results[(32, 0.15)][2]
        check(f"15% 错误率下 DP 单元 k=11({dp_15_11}) > k=32({dp_15_32})"
              "（小 k 多做延伸工作的方向性）", dp_15_11 > dp_15_32)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

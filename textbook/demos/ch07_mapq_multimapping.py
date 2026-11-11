#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch07_mapq_multimapping.py — 重复区多重比对把 MAPQ 压到 0（合成算例）

服务章节：第 7 章 §7.4「MAPQ 与 BaseQ 两道质量闸门」、失效条件第 1 条
（重复区读段 MAPQ=0 随机落位，按位置计数会把重复区算成高覆盖）；
呼应 u05 讲义 ④4.6（7 个 rRNA 拷贝 → MAPQ 0）、⑥6.3「高比对率陷阱」与 ⑩ 习题 5/7。

模型声明（重要）：
  * bwa 部分按 bwa 0.7.17 源码 mem_approx_mapq_se() 逐行复刻（bwamem.c；
    本地 bwa 0.7.19 实跑对照见 case.md §③）。只覆盖单端（SE）口径；双端
    比对后 bwa 还会做配对 mapq 调整（bwamem_pair.c），不在本 demo 范围。
  * bowtie2 部分按 bowtie2 2.5.1 源码 unique.h BowtieMapq2（默认计算器，
    bt2_search.cpp: mapqv = 2）的离散查表公式复刻，前提「次优比对已知」
    （等价于穷举候选或 -k/-a 模式）；并演示 255（未知）分支。
  * 合成算例的比对打分简化为 ±2 移码窗口内的无空位扫描（本算例不含 indel，
    与带空位 SW 等价）；bwa 口径 match+1/mismatch-4，bowtie2 端到端口径
    match 0/mismatch-6（--end-to-end 默认 --ma 0 --mp 6，读段按全 Q40 取满罚）。

数据性质：【合成算例】参考 = 40 kb 独特背景 + 5 个拷贝的 1200 bp 重复单元，
全部由 numpy Generator(20261103) 生成。单元内为确定布局：一段全拷贝保守区
（任何拷贝都不放 SNP，保证保守窗读段存在）+ 每拷贝 1 个私有 SNP（间距 >
read_len，保证以它为中心的读段窗口只含这一个私有 SNP）。读段三类：独特区
完美读段、重复区保守窗（5 拷贝完全一致 → 完美平局）、重复区分化窗（只与
来源拷贝完美、对其余拷贝恰 1 个错配）。

正文引用的输出：
  - bwa 公式锚点：完美唯一 → 60（封顶）；并列次优 sub≥score → 0；
    sub_n 与 frac_rep 的扣减各一手算例
  - bowtie2 公式锚点：端到端唯一 → 42；并列 → 1；local 唯一 → 44；
    次优差 24/90（4 个错配）→ 31；未穷举且无次优 → 255
  - 三类读段的 bwa/bowtie2 MAPQ 分布对照（同一批读段、同一打分事实，
    两列数字不可直接比——u05 ⑩ 习题 7 的定量版）
  - MAPQ≥30 过滤后重复区保留率 ≈ 0（失效条件第 1 条，扩展参考方向：
    随机落位/过滤归零）
  - Part 3 对偶演示（塌缩参考方向）：5 个生物学来源的读段在只含 1 个代表
    拷贝的参考上全部贴到同一坐标 → 深度 ≈5× 背景而 MAPQ 全部满分
    （高深度 + 高 MAPQ，与 Part 2 的低 MAPQ 分散组合对偶）
"""
import argparse
import math
import sys

import numpy as np

SEED = 20261103

# bwa 0.7.17 mem_opt_init 默认参数（源码已核）
BWA_A, BWA_B = 1, 4                    # match +1 / mismatch -4
BWA_MIN_SEED = 19                      # -k 默认 19
BWA_MAPQ_COEF_LEN = 50                 # mapQ_coef_len
BWA_MAPQ_COEF_FAC = math.log(50.0)     # mapQ_coef_fac = log(mapQ_coef_len)
BWA_SUB_TMP = max(BWA_A + BWA_B, 6 + 1, 6 + 1)  # max(a+b, o_del+e_del, o_ins+e_ins)=7
BWA_MAX_OCC = 500                      # max_occ：出现次数超过它才算重复种子

# bowtie2 2.5.1 默认打分（--ma 2 --mp 6，全 Q40 读段取满罚 6）
BT2_MATCH, BT2_MM = 0, 6  # 端到端：匹配 0 分、高质量错配罚 6（--end-to-end 默认）


# ---------------------------------------------------------------------------
# 公式复刻：bwa mem_approx_mapq_se（bwa 0.7.17, bwamem.c）
# ---------------------------------------------------------------------------

def bwa_mem_mapq_se(score, sub, csub=0, sub_n=0, frac_rep=0.0, l=150):
    """bwa 0.7.17 mem_approx_mapq_se 逐行复刻。返回 MAPQ（0–60）。"""
    sub = sub if sub else BWA_MIN_SEED * BWA_A
    sub = max(sub, csub)
    if sub >= score:
        return 0
    identity = 1.0 - (l * BWA_A - score) / (BWA_A + BWA_B) / l
    if score == 0:
        mapq = 0
    else:
        tmp = 1.0 if l < BWA_MAPQ_COEF_LEN else BWA_MAPQ_COEF_FAC / math.log(l)
        tmp *= identity * identity
        mapq = int(6.02 * (score - sub) / BWA_A * tmp * tmp + 0.499)
    if sub_n > 0:
        mapq -= int(4.343 * math.log(sub_n + 1) + 0.499)
    mapq = min(60, max(0, mapq))
    mapq = int(mapq * (1.0 - frac_rep) + 0.499)
    return mapq


# ---------------------------------------------------------------------------
# 公式复刻：bowtie2 BowtieMapq2（bowtie2 2.5.1, unique.h；默认 mapqv=2）
# ---------------------------------------------------------------------------

def bowtie2_mapq2(best, secbest, sc_per, sc_min, monotone=True,
                  is_primary=True, can_max=True, exhausted=True):
    """BowtieMapq2 查表公式复刻（end-to-end = monotone，local = 非 monotone）。

    secbest=None 表示「没有已知次优」。返回 MAPQ；255 为「未知」。
    """
    has_sec = secbest is not None
    if not is_primary or (not can_max and not exhausted and not has_sec):
        return 255
    diff = max(1, sc_per - sc_min)
    best_over = best - sc_min
    if not has_sec:
        if monotone:  # 端到端
            if best_over >= diff * 0.8:
                return 42
            if best_over >= diff * 0.7:
                return 40
            if best_over >= diff * 0.6:
                return 24
            if best_over >= diff * 0.5:
                return 23
            if best_over >= diff * 0.4:
                return 8
            if best_over >= diff * 0.3:
                return 3
            return 0
        # local
        if best_over >= diff * 0.8:
            return 44
        if best_over >= diff * 0.7:
            return 42
        if best_over >= diff * 0.6:
            return 41
        if best_over >= diff * 0.5:
            return 36
        if best_over >= diff * 0.4:
            return 28
        if best_over >= diff * 0.3:
            return 24
        return 22
    bestdiff = abs(best - secbest)
    if monotone:  # 端到端
        if bestdiff >= diff * 0.9:
            return 39 if best_over == diff else 33
        if bestdiff >= diff * 0.8:
            return 38 if best_over == diff else 27
        if bestdiff >= diff * 0.7:
            return 37 if best_over == diff else 26
        if bestdiff >= diff * 0.6:
            return 36 if best_over == diff else 22
        if bestdiff >= diff * 0.5:
            if best_over == diff:
                return 35
            return 25 if best_over >= diff * 0.84 else 16 if best_over >= diff * 0.68 else 5
        if bestdiff >= diff * 0.4:
            if best_over == diff:
                return 34
            return 21 if best_over >= diff * 0.84 else 14 if best_over >= diff * 0.68 else 4
        if bestdiff >= diff * 0.3:
            if best_over == diff:
                return 32
            return 18 if best_over >= diff * 0.88 else 15 if best_over >= diff * 0.67 else 3
        if bestdiff >= diff * 0.2:
            if best_over == diff:
                return 31
            return 17 if best_over >= diff * 0.88 else 11 if best_over >= diff * 0.67 else 0
        if bestdiff >= diff * 0.1:
            if best_over == diff:
                return 30
            return 12 if best_over >= diff * 0.88 else 7 if best_over >= diff * 0.67 else 0
        if bestdiff > 0:
            return 6 if best_over >= diff * 0.67 else 2
        return 1 if best_over >= diff * 0.67 else 0
    # local
    if bestdiff >= diff * 0.9:
        return 40
    if bestdiff >= diff * 0.8:
        return 39
    if bestdiff >= diff * 0.7:
        return 38
    if bestdiff >= diff * 0.6:
        return 37
    if bestdiff >= diff * 0.5:
        return 35 if best_over == diff else (25 if best_over >= diff * 0.5 else 20)
    if bestdiff >= diff * 0.4:
        return 34 if best_over == diff else (21 if best_over >= diff * 0.5 else 19)
    if bestdiff >= diff * 0.3:
        return 33 if best_over == diff else (18 if best_over >= diff * 0.5 else 16)
    if bestdiff >= diff * 0.2:
        return 32 if best_over == diff else (17 if best_over >= diff * 0.5 else 12)
    if bestdiff >= diff * 0.1:
        return 31 if best_over == diff else (14 if best_over >= diff * 0.5 else 9)
    if bestdiff > 0:
        return 11 if best_over >= diff * 0.5 else 2
    return 1 if best_over >= diff * 0.5 else 0


# ---------------------------------------------------------------------------
# 合成基因组与读段
# ---------------------------------------------------------------------------

def repeat_layout(unit_len, read_len, copies):
    """重复单元内部布局（unit 内坐标）：
    - 保守区 [cons_lo, cons_hi)：任何拷贝都不放私有 SNP → conserved 读段存在；
    - 拷贝 c 的私有 SNP 位于 snp_pos[c]，间距 = read_len+20 > read_len，
      保证以它为中心的 read_len 窗口至多含一个私有 SNP。
    布局放不下时 SystemExit（提醒调大 --unit-len）。
    """
    margin = 50
    cons_lo = margin
    cons_hi = cons_lo + read_len + 40
    snp_pos = [cons_hi + 100 + c * (read_len + 20) for c in range(copies)]
    need = max(cons_hi, snp_pos[-1] + (read_len + 1) // 2) + margin
    if need > unit_len:
        raise SystemExit(
            f"unit_len={unit_len} 放不下该布局（read_len={read_len}, "
            f"copies={copies} 需要 ≥ {need}）；请调大 --unit-len")
    return cons_lo, cons_hi, snp_pos


def make_genome_with_repeats(rng, unique_len, copies, unit_len, read_len):
    """独特背景 + copies 个拷贝的重复单元（每拷贝 1 个私有 SNP，见 repeat_layout）。

    返回 (genome, copy_pos, unit_seqs)。拷贝位置间隔 ≥2 kb。
    """
    cons_lo, cons_hi, snp_pos = repeat_layout(unit_len, read_len, copies)
    bg = rng.choice(np.array(list("ACGT")), size=unique_len)
    genome = "".join(bg)
    unit = rng.choice(np.array(list("ACGT")), size=unit_len)
    pos, used = [], set()
    while len(pos) < copies:
        p = int(rng.integers(unique_len // 4, unique_len - unit_len - 1000))
        if any(abs(p - q) < 2000 for q in pos):
            continue
        pos.append(p)
    pos.sort()
    unit_seqs = []
    for c in range(copies):
        u = unit.copy()
        # 私有 SNP 必须真的改变碱基（否则该拷贝无 distinguishing 位点）
        others = [b for b in "ACGT" if b != unit[snp_pos[c]]]
        u[snp_pos[c]] = str(rng.choice(np.array(others)))
        unit_seqs.append("".join(u))
    # 从右到左插入，避免位移；copy_pos 返回的是插入后基因组坐标
    genome_pos, offset = [], 0
    for p, u in sorted(zip(pos, unit_seqs), reverse=True):
        genome = genome[:p] + u + genome[p:]
    for p in pos:
        genome_pos.append(p + offset)
        offset += unit_len
    return genome, genome_pos, unit_seqs


def make_reads(rng, genome, copy_pos, unit_seqs, read_len, n_per_class):
    """三类读段（各 n 条）：
    unique        独特背景、完美
    conserved     全拷贝保守区内的 150 bp 窗口、完美（→ 5 路平局）
    diverged      以某拷贝私有 SNP 为中心的窗口、完美（→ 只有来源拷贝满分，
                  对其余各拷贝恰 1 个错配）
    """
    cons_lo, cons_hi, snp_pos = repeat_layout(len(unit_seqs[0]), read_len,
                                              len(unit_seqs))
    reads = []
    class_of = []
    for _ in range(n_per_class):
        st = int(rng.integers(1000, len(genome) - read_len - 1000))
        if any(abs(st - (p - 50)) < 600 or p <= st < p + len(unit_seqs[0])
               for p in copy_pos):
            st = int(rng.integers(1000, copy_pos[0] - read_len - 100))
        reads.append(genome[st:st + read_len])
        class_of.append("unique")
    # conserved 窗口：保守区内所有起点（布局保证非空）
    starts = [s for s in range(cons_lo, cons_hi - read_len)
              if all(all(u[i] == unit_seqs[0][i] for u in unit_seqs)
                     for i in range(s, s + read_len))]
    if not starts:
        raise SystemExit("内部错误：保守区不存在（布局与 SNP 放置不一致）")
    for _ in range(n_per_class):
        s = int(rng.choice(starts))
        c = int(rng.integers(len(copy_pos)))
        reads.append(unit_seqs[c][s:s + read_len])
        class_of.append("conserved")
    # diverged 窗口：私有 SNP 居中（布局保证窗口内只有这一个私有 SNP）
    for _ in range(n_per_class):
        c = int(rng.integers(len(copy_pos)))
        s = snp_pos[c] - read_len // 2
        reads.append(unit_seqs[c][s:s + read_len])
        class_of.append("diverged")
    return reads, class_of


# ---------------------------------------------------------------------------
# 玩具全候选比对器：k-mer 索引找候选，±2 移码无空位扫描打分
# ---------------------------------------------------------------------------

class ToyAligner:
    def __init__(self, genome, k=19):
        self.genome = genome
        self.g = np.frombuffer(genome.encode(), dtype=np.uint8)
        self.k = k
        self.index = {}
        gb = genome.encode()
        for i in range(len(gb) - k + 1):
            self.index.setdefault(gb[i:i + k], []).append(i)

    def frac_rep(self, read):
        """读段被「出现次数 > max_occ(500)」的 k-mer 覆盖的比例（bwa frac_rep 口径）。"""
        rb = read.encode()
        cov = [False] * len(rb)
        for i in range(len(rb) - self.k + 1):
            occ = len(self.index.get(rb[i:self.k + i], ()))
            if occ > BWA_MAX_OCC:
                for j in range(i, i + self.k):
                    cov[j] = True
        return sum(cov) / len(rb)

    def score_read(self, read, read_len):
        """返回 (候选对角线数, 最佳 bwa 分, 次优 bwa 分, 次优已知, sub_n, frac_rep,
        最佳 bowtie2 分, 次优 bowtie2 分)。

        候选按「对角线 p−i（种子 k-mer 偏移 i，基因组位置 p）」归并——同一对角线上的
        命中是同一比对的种子，不是竞争比对；每个对角线只取 ±2 移码扫描的最高分。
        """
        rb = read.encode()
        cand_diag = {}
        step = 7
        for i in range(0, len(rb) - self.k + 1, step):
            for p in self.index.get(rb[i:i + self.k], ()):
                cand_diag.setdefault(p - i, []).append(p)
        bwa_scores, bt2_scores = [], []
        for ps in cand_diag.values():
            best_bwa = -10 ** 9
            best_bt2 = -10 ** 9
            for p in ps:
                for shift in range(-2, 3):
                    s = p + shift
                    if s < 0 or s + read_len > len(self.g):
                        continue
                    mm = int(np.count_nonzero(
                        self.g[s:s + read_len] != np.frombuffer(rb, dtype=np.uint8)))
                    m = read_len - mm
                    best_bwa = max(best_bwa, m * BWA_A - mm * BWA_B)
                    best_bt2 = max(best_bt2, m * BT2_MATCH - mm * BT2_MM)
            bwa_scores.append(best_bwa)
            bt2_scores.append(best_bt2)
        order = np.argsort(bwa_scores)[::-1]
        b1 = bwa_scores[order[0]]
        known = len(cand_diag) > 1 and bwa_scores[order[1]] > -10 ** 8
        b2 = bwa_scores[order[1]] if known else None
        sub_n = sum(1 for s in bwa_scores if b1 - s <= BWA_SUB_TMP) - 1
        t1 = bt2_scores[order[0]]
        t2 = bt2_scores[order[1]] if known else None
        return (len(cand_diag), b1, b2, known, sub_n, self.frac_rep(read),
                t1, t2)


def main():
    ap = argparse.ArgumentParser(
        description="重复区多重比对把 MAPQ 压到 0（合成算例；公式按 bwa 0.7.17 / bowtie2 2.5.1 源码复刻）")
    ap.add_argument("--seed", type=int, default=SEED, help="随机种子")
    ap.add_argument("--unique-len", type=int, default=40000, help="独特背景长度 bp")
    ap.add_argument("--copies", type=int, default=5, help="重复单元拷贝数")
    ap.add_argument("--unit-len", type=int, default=1200, help="重复单元长度 bp")
    ap.add_argument("--read-len", type=int, default=150, help="读段长度 bp")
    ap.add_argument("--reads-per-class", type=int, default=600, help="每类读段数")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    print("=" * 72)
    print("[Part 1] 公式锚点（手算值，逐条注明算术）")
    print("=" * 72)
    print("bwa 0.7.17 mem_approx_mapq_se 复刻：")
    a1 = bwa_mem_mapq_se(score=150, sub=0, sub_n=0, frac_rep=0.0, l=150)
    print(f"  完美唯一: score=150, sub 缺省→19 → 6.02×131×(ln50/ln150)⁴ ≈ 481 → 封顶 {a1}")
    a2 = bwa_mem_mapq_se(score=150, sub=150, l=150)
    print(f"  完美平局(5 拷贝不可分): sub=150 ≥ score → {a2}（u05 ⑩ 习题 5 的答案）")
    a3 = bwa_mem_mapq_se(score=30, sub=20, sub_n=3, frac_rep=0.0, l=80)
    print(f"  小分演示: score=30, sub=20, sub_n=3, l=80 → 28-6 = {a3}")
    a4 = bwa_mem_mapq_se(score=150, sub=100, sub_n=0, frac_rep=0.5, l=150)
    print(f"  frac_rep=0.5: 原 60 × 0.5 → {a4}（重复种子比例直接打折）")
    # 端到端：完美分 0，scMin = L(-0.6,-0.6) 截为整数；local：完美分 2L，scMin = G(20,8)=20+8·ln L
    sc_per, sc_min = 0, int(-0.6 * args.read_len - 0.6)
    lc_per, lc_min = 2 * args.read_len, int(20 + 8 * np.log(args.read_len))
    print(f"bowtie2 2.5.1 BowtieMapq2 复刻（L={args.read_len}；端到端 scPer={sc_per}, scMin={sc_min}, diff={sc_per - sc_min}；"
          f"local scPer={lc_per}, scMin={lc_min}, diff={lc_per - lc_min}）：")
    b1 = bowtie2_mapq2(sc_per, None, sc_per, sc_min, monotone=True)
    b2 = bowtie2_mapq2(sc_per, sc_per, sc_per, sc_min, monotone=True)
    b3 = bowtie2_mapq2(lc_per, None, lc_per, lc_min, monotone=False)
    b4 = bowtie2_mapq2(sc_per, sc_per - 4 * BT2_MM, sc_per, sc_min, monotone=True)
    b5 = bowtie2_mapq2(sc_per, None, sc_per, sc_min, monotone=True,
                       can_max=False, exhausted=False)
    print(f"  端到端完美唯一 → {b1}（讲义 u05 ④4.5 的「上限 42」）")
    print(f"  端到端完美平局 → {b2}（与 bwa 的 0 不同——口径差异本身）")
    print(f"  local 完美唯一 → {b3}（--local 时上限 44，源码 unique.h）")
    print(f"  次优差 24/{sc_per - sc_min}（4 个错配）且 bestOver=diff → {b4}")
    print(f"  未穷举且无次优 → {b5}（MAPQ 255 = 未知，SAM 规范口径）")

    print()
    print("=" * 72)
    print("[Part 2] 合成批比对：同一批读段，bwa 口径 vs bowtie2 口径")
    print("=" * 72)
    rng = np.random.default_rng(args.seed)
    genome, copy_pos, unit_seqs = make_genome_with_repeats(
        rng, args.unique_len, args.copies, args.unit_len, args.read_len)
    print(f"合成参考: {len(genome)} bp = {args.unique_len//1000} kb 背景 + "
          f"{args.copies}×{args.unit_len} bp 重复单元"
          f"（保守区 + 每拷贝 1 个私有 SNP，间距 {args.read_len + 20} bp；"
          f"seed={args.seed}）")
    reads, class_of = make_reads(rng, genome, copy_pos, unit_seqs,
                                 args.read_len, args.reads_per_class)
    aln = ToyAligner(genome)
    rows = {}
    mapq0_total = 0
    n_total = 0
    hist_bwa = [0, 0, 0, 0]  # =0 / 1-9 / 10-29 / ≥30
    for read, cls in zip(reads, class_of):
        (_, s1, s2, known, sub_n, f_rep, t1, t2) = aln.score_read(read, args.read_len)
        q_bwa = bwa_mem_mapq_se(score=s1, sub=s2 if known else 0, sub_n=sub_n,
                                frac_rep=f_rep, l=args.read_len)
        q_bt2 = bowtie2_mapq2(t1, t2 if known else None, sc_per, sc_min,
                              monotone=True)
        r = rows.setdefault(cls, {"n": 0, "bwa": [], "bt2": []})
        r["n"] += 1
        r["bwa"].append(q_bwa)
        r["bt2"].append(q_bt2)
        n_total += 1
        mapq0_total += (q_bwa == 0)
        hist_bwa[0 if q_bwa == 0 else 1 if q_bwa < 10 else 2 if q_bwa < 30 else 3] += 1
    print(f"{'类别':<12} {'n':>5} | {'bwa MAPQ 均值':>13} {'=0%':>7} {'≥30%':>7}"
          f" | {'bowtie2 均值':>12} {'=0%':>7} {'≥30%':>7}")
    print("-" * 80)
    for cls in ("unique", "conserved", "diverged"):
        r = rows[cls]
        mb = np.mean(r["bwa"])
        mt = np.mean(r["bt2"])
        zb = 100.0 * np.mean([q == 0 for q in r["bwa"]])
        zt = 100.0 * np.mean([q == 0 for q in r["bt2"]])
        hb = 100.0 * np.mean([q >= 30 for q in r["bwa"]])
        ht = 100.0 * np.mean([q >= 30 for q in r["bt2"]])
        print(f"{cls:<12} {r['n']:>5} | {mb:>13.2f} {zb:>6.1f}% {hb:>6.1f}%"
              f" | {mt:>12.2f} {zt:>6.1f}% {ht:>6.1f}%")
    print("-" * 80)
    print(f"MAPQ 直方图（bwa 口径）: =0: {hist_bwa[0]}  1-9: {hist_bwa[1]}"
          f"  10-29: {hist_bwa[2]}  ≥30: {hist_bwa[3]}（合计 {n_total}）")
    print(f"「高比对率陷阱」演示：全部 {n_total} 条都「比上了」(mapped 100%)，"
          f"但 MAPQ=0 占 {mapq0_total}/{n_total} = {mapq0_total / n_total * 100:.1f}%")
    keep = {cls: 100.0 * np.mean([q >= 30 for q in rows[cls]["bwa"]])
            for cls in rows}
    print(f"MAPQ≥30 过滤保留率（bwa 口径）: unique {keep['unique']:.1f}% / "
          f"conserved {keep['conserved']:.1f}% / diverged {keep['diverged']:.1f}%")
    print("→ 重复区读段几乎全被过滤：按位置计数时重复区要么「看着高覆盖」"
          "（不过滤、随机落位），要么「系统性归零」（过滤）——失效条件第 1 条"
          "的**扩展参考**方向。")

    print()
    print("=" * 72)
    print("[Part 3] 对偶演示：塌缩参考（5 个来源 → 同一坐标，深度聚合）")
    print("=" * 72)
    # bookkeeping：样本基因组有 5 个拷贝，参考只收 1 个代表拷贝。5 个来源的
    # 读段与代表拷贝至多差 1 个 SNP，在塌缩参考上全部唯一地贴到同一坐标
    # （家族读段按完美唯一建模，≤1 个 SNP 差异不改变定性结论）。
    d_bg = 10.0
    n_bg = int(d_bg * args.unique_len / args.read_len)
    n_per_source = int(d_bg * args.unit_len / args.read_len)
    starts_bg = rng.integers(0, args.unique_len - args.read_len, size=n_bg)
    fam_starts = rng.integers(0, args.unit_len - args.read_len,
                              size=args.copies * n_per_source)
    depth_bg = np.zeros(args.unique_len, dtype=np.int64)
    np.add.at(depth_bg,
              starts_bg[:, None] + np.arange(args.read_len)[None, :], 1)
    unit_depth = np.zeros(args.unit_len, dtype=np.int64)
    np.add.at(unit_depth,
              fam_starts[:, None] + np.arange(args.read_len)[None, :], 1)
    bg_med = float(np.median(depth_bg[1000:-1000]))
    unit_med = float(np.median(unit_depth))
    ratio = unit_med / bg_med
    q_fam = bwa_mem_mapq_se(score=args.read_len, sub=0, sub_n=0, frac_rep=0.0,
                            l=args.read_len)
    print(f"背景 {n_bg} 条（≈{d_bg:.0f}×）+ 家族 {args.copies} 来源×{n_per_source} 条"
          f"（在塌缩参考上全部唯一贴到 1 个代表拷贝）")
    print(f"深度中位：背景 {bg_med:.1f}×，代表拷贝区 {unit_med:.1f}×，比值 {ratio:.2f}")
    print(f"家族读段 MAPQ：全部 {q_fam}（唯一完美比对）→ MAPQ≥30 过滤保留 100%")
    print("→ 塌缩参考的异常信号是「高深度 + 高 MAPQ」，与 Part 2 扩展参考的"
          "「低 MAPQ 分散落位」对偶：只查 MAPQ 分布或只查深度都会漏掉另一半"
          "（失效条件第 1 条的两个方向必须分开排查）。")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        check("bwa 完美唯一 → 60", a1 == 60)
        check("bwa 完美平局 → 0", a2 == 0)
        check("bwa sub_n 手算 28-6=22", a3 == 22)
        check("bwa frac_rep=0.5 → 30", a4 == 30)
        check("bowtie2 端到端唯一 → 42", b1 == 42)
        check("bowtie2 端到端平局 → 1", b2 == 1)
        check("bowtie2 local 唯一 → 44", b3 == 44)
        check("bowtie2 次优差 24/90 → 31", b4 == 31)
        check("bowtie2 未穷举无次优 → 255", b5 == 255)
        # 2026-11-03 现跑记录
        z_unique = 100.0 * np.mean([q == 0 for q in rows["unique"]["bwa"]])
        z_cons = 100.0 * np.mean([q == 0 for q in rows["conserved"]["bwa"]])
        z_div = 100.0 * np.mean([q == 0 for q in rows["diverged"]["bwa"]])
        check(f"unique 类 MAPQ=0 比例 == 0（现跑 {z_unique:.1f}）", z_unique == 0.0)
        check(f"conserved 类 MAPQ=0 比例 == 100（现跑 {z_cons:.1f}）",
              z_cons == 100.0)
        check(f"diverged 类 MAPQ=0 比例 == 0（现跑 {z_div:.1f}）", z_div == 0.0)
        m_cons = float(np.mean(rows["conserved"]["bt2"]))
        check(f"conserved 类 bowtie2 MAPQ == 1（现跑 {m_cons:.2f}）", m_cons == 1.0)
        h_unique = 100.0 * np.mean([q >= 30 for q in rows["unique"]["bwa"]])
        check(f"unique 类 bwa MAPQ≥30 比例 == 100（现跑 {h_unique:.1f}）",
              h_unique == 100.0)
        h_div = 100.0 * np.mean([q >= 30 for q in rows["diverged"]["bwa"]])
        check(f"diverged 类 bwa MAPQ≥30 比例 == 0（现跑 {h_div:.1f}）",
              h_div == 0.0)
        check(f"MAPQ=0 总数 == {mapq0_total}（复现锚 {args.reads_per_class}）",
              mapq0_total == args.reads_per_class)
        check(f"塌缩参考深度比值 ≈ 5（现跑 {ratio:.2f}，区间 4–6）",
              4.0 < ratio < 6.0)
        check("塌缩参考家族读段 MAPQ == 60（唯一完美）", q_fam == 60)
        check(f"家族读段数 == {args.copies}×{n_per_source}",
              len(fam_starts) == args.copies * n_per_source)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

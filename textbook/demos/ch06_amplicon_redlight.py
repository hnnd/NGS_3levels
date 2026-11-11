#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch06_amplicon_redlight.py — 扩增子类文库的重复/过表达红灯「本来就是设计」对照（合成算例）

服务章节：第 6 章 §6.4「红灯辨析」与失效条件第 1 条
（FastQC 的阈值是针对随机全基因组文库的启发式：扩增子碱基组成等红灯属正常）。

数据性质：【合成算例】两个文库全部由固定种子 numpy 现场生成：
  - WGS-like：N 条相互独立的随机 150 bp 读段（均匀随机序列，模拟均一打断的基因组文库）；
  - amplicon-like：40 个合成单倍型（300 bp），20 万条读段按指数丰度抽样并加 0.5%/碱基
    替换错误（模拟同一对引物锚定保守区的扩增子文库 + PCR 重复 + 测序错误）。
  全部合成，不对应任何真实菌株或样本，输出不得写成真实样本的实测结果。

正文引用的输出（FastQC v0.12.1 源码语义，2026-11-03 逐行核对）：
  - Duplication 模块：序列 >50 bp 截前 50 bp；以 100,000 个【不同】序列为观察上限
    （OverRepresentedSeqs.OBSERVATION_CUTOFF：达到后不再记录新序列，但已见序列仍全程
    计数——讲义 l0_05 §1「仅抽取文件开头 100,000 条 reads」的口径不准确，见 CASE-CH06-04）；
    WARN = 去重后剩余序列占比 < 70%，ERROR = < 50%（limits.txt）。
  - Overrepresented 模块：单序列占比 > 0.1% 即列入（WARN），最高者 > 1% → ERROR。
  - 对照结论：WGS-like 去重后 ≈100%（PASS）；amplicon-like 去重后 ≈4%、最高单序列 ≈14%
    → 两模块 FAIL——这是扩增子设计的必然，不是数据缺陷。
  - 与 2026-11-03 实跑 FastQC v0.12.1 对照（同一生成器造出的两个合成文件）：
    实跑 dedup 100.0% vs 4.0855%，模块判定与本脚本一致（cases/ch06/case.md §③）。

参数含义：
  --n-reads    每个文库的合成读段数（默认 200000）
  --n-hap      扩增子文库的单倍型个数（默认 40）
  --read-len   读段长度（默认 150）
  --error-rate 扩增子读段逐碱基替换错误率（默认 0.005）
  --seed       随机种子（默认 20261103，与 case.md 实跑文件同一生成器）
  --selftest   断言正文引用的关键输出
"""
import argparse
import sys

import numpy as np

OBSERVATION_CUTOFF = 100000  # OverRepresentedSeqs：不同序列观察上限
DUP_THRESH = {"warn": 70.0, "error": 50.0}      # 去重后剩余百分比（limits.txt）
OVER_WARN = 0.1                                  # 单序列占比列入阈值（%）
OVER_ERROR = 1.0                                 # 最高单序列占比 ERROR 阈值（%）


def gen_wgs_like(rng, n, length):
    """WGS-like：n 条独立随机读段（与 case.md 实跑文件同一调用序列）。"""
    bases = np.array(list("ACGT"))
    return ["".join(rng.choice(bases, length)) for _ in range(n)]


def gen_amplicon_like(rng, n, n_hap, length, error_rate):
    """扩增子-like：n_hap 个单倍型，指数丰度抽样 + 逐碱基替换错误。"""
    bases = np.array(list("ACGT"))
    haps = ["".join(rng.choice(bases, 300)) for _ in range(n_hap)]
    w = rng.exponential(1.0, n_hap)
    w /= w.sum()
    idx = rng.choice(n_hap, n, p=w)
    reads = []
    for i in idx:
        s = np.array(list(haps[i][:length]))
        mask = rng.random(length) < error_rate
        if mask.any():
            s[mask] = rng.choice(bases, mask.sum())
        reads.append("".join(s))
    return reads


def fastqc_duplication(reads):
    """复刻 OverRepresentedSeqs 计数 + DuplicationLevel 纠偏与判定。
    返回 (去重后剩余%, 判定, 观察到的不同序列数, 是否触发观察上限)。"""
    seqs = {}
    count = 0
    unique = 0
    frozen = False
    count_at_limit = 0
    for r in reads:
        count += 1
        key = r[:50] if len(r) > 50 else r          # >50 bp 截前 50 bp
        if key in seqs:
            seqs[key] += 1
            if not frozen:
                count_at_limit = count
        elif not frozen:
            seqs[key] = 1
            unique += 1
            count_at_limit = count
            if unique == OBSERVATION_CUTOFF:
                frozen = True
    # DuplicationLevel.getCorrectedCount：按「计数相同」归并后外推
    collated = {}
    for c in seqs.values():
        collated[c] = collated.get(c, 0) + 1

    def corrected(dup_level, n_obs):
        if count_at_limit == count or count - n_obs < count_at_limit:
            return float(n_obs)
        p_not = 1.0
        limit_of_caring = 1.0 - n_obs / (n_obs + 0.01)
        for i in range(count_at_limit):
            p_not *= ((count - i) - dup_level) / float(count - i)
            if p_not < limit_of_caring:
                p_not = 0.0
                break
        p_seeing = 1.0 - p_not
        return n_obs / p_seeing

    dedup_total = sum(corrected(d, c) for d, c in collated.items())
    raw_total = sum(corrected(d, c) * d for d, c in collated.items())
    pct = dedup_total / raw_total * 100 if raw_total else 100.0
    status = "fail" if pct < DUP_THRESH["error"] else (
        "warn" if pct < DUP_THRESH["warn"] else "pass")
    return pct, status, len(seqs), frozen


def fastqc_overrepresented(reads):
    """复刻 OverRepresentedSeqs 列入/判定：单序列占比 >0.1% 列入，最高 >1% → error。"""
    total = len(reads)
    best = ("", 0)
    listed = 0
    seqs = {}
    for r in reads:
        key = r[:50] if len(r) > 50 else r
        seqs[key] = seqs.get(key, 0) + 1
    for k, c in seqs.items():
        if c / total * 100 > OVER_WARN:
            listed += 1
            if c > best[1]:
                best = (k, c)
    top_pct = best[1] / total * 100
    if best[1] == 0:
        status = "pass"
    elif top_pct > OVER_ERROR:
        status = "fail"
    else:
        status = "warn"
    return best[1], top_pct, listed, status


def main():
    ap = argparse.ArgumentParser(
        description="扩增子 vs 随机文库：FastQC 重复/过表达模块的红灯对照（合成算例）")
    ap.add_argument("--n-reads", type=int, default=200000)
    ap.add_argument("--n-hap", type=int, default=40)
    ap.add_argument("--read-len", type=int, default=150)
    ap.add_argument("--error-rate", type=float, default=0.005)
    ap.add_argument("--seed", type=int, default=20261103)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    ok = True
    n_pass = [0]
    total = [0]

    def check(name, cond):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok = ok and cond
        total[0] += 1
        if cond:
            n_pass[0] += 1

    print("=" * 66)
    print(f"生成两个合成文库（seed={args.seed}，各 {args.n_reads} 条 {args.read_len} bp）")
    print("=" * 66)
    rng = np.random.default_rng(args.seed)
    wgs = gen_wgs_like(rng, args.n_reads, args.read_len)
    amp = gen_amplicon_like(rng, args.n_reads, args.n_hap, args.read_len, args.error_rate)

    for name, reads in (("WGS-like（独立随机序列）", wgs),
                        ("amplicon-like（40 单倍型+PCR 重复+0.5% 错误）", amp)):
        pct, dstat, nuniq, frozen = fastqc_duplication(reads)
        top, top_pct, nlisted, ostat = fastqc_overrepresented(reads)
        print(f"\n[{name}]")
        print(f"  观察到的不同 50-mer 序列: {nuniq}（观察上限 100000 {'触发' if frozen else '未触发'}）")
        print(f"  Duplication: 去重后剩余 {pct:.4f}%  → {dstat.upper()}"
              f"（阈值 warn<70 / error<50）")
        print(f"  Overrepresented: 列入 {nlisted} 条，最高单序列 {top} 条 = {top_pct:.4f}%"
              f" → {ostat.upper()}（阈值 列入>0.1% / error>1%）")

    # ---- selftest 断言（与 2026-11-03 实跑 FastQC v0.12.1 记录对算）----
    print()
    pct_w, st_w, _, _ = fastqc_duplication(wgs)
    pct_a, st_a, _, _ = fastqc_duplication(amp)
    top_a, toppct_a, _, ost_a = fastqc_overrepresented(amp)
    print("[selftest]")
    check("WGS-like 去重后剩余 = 100.0%（实跑 FastQC 记录 100.0）",
          abs(pct_w - 100.0) < 1e-9)
    check("WGS-like duplication = PASS", st_w == "pass")
    check("amplicon-like 去重后剩余 = 4.0855%（实跑 FastQC 记录 4.085500000000001）",
          abs(pct_a - 4.085500000000001) < 1e-6)
    check("amplicon-like duplication = FAIL", st_a == "fail")
    check("amplicon-like 最高单序列 = 27788 条 13.894%（实跑 FastQC 记录一致）",
          top_a == 27788 and abs(toppct_a - 13.894) < 1e-9)
    check("amplicon-like overrepresented = FAIL", ost_a == "fail")

    # freeze 机制单元构造：5000 条读段只有 2 个不同序列（12-mer 不触发 50 bp 截断）
    # → 上限不触发、计数精确；去重后剩余 = 2/5000 = 0.04% → FAIL（< error 50）
    tiny = ["ACGT" * 3] * 3000 + ["TTGC" * 3] * 2000
    p, s, u, f = fastqc_duplication(tiny)
    check("单元构造：2 个不同序列时 dedup=0.04% fail、上限未触发",
          u == 2 and not f and abs(p - 0.04) < 1e-9 and s == "fail")

    if args.selftest:
        print()
        print(f"SELFTEST {'PASS' if ok else 'FAIL'} ({n_pass[0]}/{total[0]})")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

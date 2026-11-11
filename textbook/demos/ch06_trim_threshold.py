#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch06_trim_threshold.py — fastp cut_tail 滑窗修剪阈值对保留读段数与平均长度的影响（合成算例）

服务章节：第 6 章 §6.4「fastp 参数调优」；失效条件第 3 条
（过度修剪造成长度偏倚；清洗后保留率异常低几乎总是参数错）；
讲义 u04 ⑥ 6.2 病征 A（过滤保留率灾难性锐减）的定量复现入口。

数据性质：【合成算例】输入为讲义 l0_05 上机步骤 1 的生成器（random.seed(42)，
2000 条 100 bp 读段，30% 片段 70 bp + TruSeq 接头，质量剖面
Q(p)=max(2,int(38-20*(p/100)^2))）。全部合成，不对应真实样本，
输出不得写成真实样本的实测结果。

复刻口径（OpenGene/fastp v1.0.1 源码逐行核对，2026-11-03）：
  - filter.cpp Filter::trimAndCut 的 cut_tail（反向滚动窗口，w=4 时
    totalQual/w >= 33+阈值 即停，t 回退 t-w+1，末尾 N 再回退）；
  - adaptertrimmer.cpp trimBySequence（先质量修剪、后接头扫描：从 read 的 -4 位
    起逐位 Hamming 比对，容忍 cmplen/8 个错配，首位命中即截到 pos）；
  - 顺序：质量修剪 → 接头修剪 → 长度过滤（--length_required）→ 低质量过滤
    （Q<15 碱基 >40% 判低质量，本算例不触发）。
  - 一轮插入/删除比对（matchWithOneInsertion）在本算例不触发，
    --selftest 以与真实 fastp 1.0.1 四档阈值实跑记录的完全一致为验证。

正文引用的输出（cut_mean_quality ∈ {15,20,25,30}，窗口 4，length_required 50，
接头 AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC）：
  保留读段数 / 总碱基 / 平均长度 / Q20% / Q30% / 接头修剪读段·碱基，
  四档与 2026-11-03 实跑 fastp 1.0.1 完全一致：
    Q15: 2000 条 / 181973 bp / 90.99 bp / 96.16% / 70.34% / 604 条·18027 bp
    Q20: 2000 条 / 172152 bp / 86.08 bp / 100%   / 74.35% / 608 条·13848 bp
    Q25: 2000 条 / 151168 bp / 75.58 bp / 100%   / 84.67% / 605 条·4832 bp
    Q30: 2000 条 / 121980 bp / 60.99 bp / 100%   / 100%   / 4 条·20 bp
  教学点：阈值从 20 抬到 30，Q30 百分比上升但有效产出从 86% 崩到 61%——
  「让指标变好看」与「保住数据」是两件事；接头修剪计数随阈值单调下降是
  「先质量修剪、后接头扫描」的顺序效应，不是接头变少了。

参数含义：
  --cut-qualities  逗号分隔的 cut_mean_quality 扫描档（默认 15,20,25,30）
  --window         滑窗宽度（默认 4，fastp 黄金值）
  --length-required 过滤后最小读长（默认 50）
  --seed           生成器种子（默认 42，与讲义一致）
  --n-reads        合成读段数（默认 2000）
  --selftest       断言与实跑 fastp 1.0.1 记录一致
"""
import argparse
import random
import sys

ADAPTER = "AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC"


def gen_reads(seed=42, n=2000):
    """讲义 l0_05 上机步骤 1 生成器原文（random.seed(42)）。"""
    rng = random.Random(seed)
    reads = []
    for i in range(n):
        insert = 70 if i % 10 < 3 else 100
        seq = ("".join(rng.choice("ACGT") for _ in range(insert)) + ADAPTER)[:100]
        qual = "".join(chr(max(2, int(38 - 20 * (p / 100) ** 2)) + 33)
                       for p in range(100))
        reads.append([seq, qual])
    return reads


def cut_tail(seq, qual, w, qthr, front=0, tail=0):
    """fastp v1.0.1 filter.cpp 的 cut_tail（反向滚动窗口）复刻。"""
    l = len(seq)
    if l - front - tail - w <= 0:
        return None
    qa = [ord(c) for c in qual]
    total = sum(qa[l - tail - 1 - i] for i in range(w - 1))  # 预备滚动
    t = l - tail - 1
    while t - w >= front:
        total += qa[t - w + 1]
        if t < l - tail - 1:
            total -= qa[t + 1]
        if total / w >= 33 + qthr:
            break
        t -= 1
    if t < l - 1:
        t = t - w + 1
    while t >= 0 and seq[t] == "N":
        t -= 1
    rlen = t - front + 1
    if rlen <= 0 or front >= l - 1:
        return None
    return seq[front:front + rlen], qual[front:front + rlen]


def trim_by_sequence(seq, adapter, match_req=4):
    """fastp v1.0.1 adaptertrimmer.cpp trimBySequence 的 Hamming 段复刻。
    返回 (修剪后的序列, 计数的接头碱基数)；未命中返回 None。"""
    rlen, alen = len(seq), len(adapter)
    if alen < match_req:
        return None
    start = -4 if alen >= 16 else (-3 if alen >= 12 else (-2 if alen >= 8 else 0))
    pos = start
    found = False
    while pos < rlen - match_req:
        cmplen = min(rlen - pos, alen)
        allowed = cmplen // 8
        mismatch = 0
        i = max(0, -pos)
        while i < cmplen:
            if adapter[i] != seq[i + pos]:
                mismatch += 1
                if mismatch > allowed:
                    break
            i += 1
        if i == cmplen:          # 全程未超容错误配 → 命中
            found = True
            break
        pos += 1
    if not found:
        return None
    if pos < 0:
        return "", alen + pos
    return seq[:pos], rlen - pos


def run_fastp_model(reads, cut_q, window, length_required,
                    qualified=15, unqualified_pct=40):
    """顺序：cut_tail → trimBySequence → length/quality 过滤。"""
    passed = 0
    total_bases = q20 = q30 = 0
    adapter_reads = 0
    adapter_bases = 0
    for seq, qual in reads:
        out = cut_tail(seq, qual, window, cut_q)
        if out is None:
            continue
        seq2, qual2 = out
        hit = trim_by_sequence(seq2, ADAPTER)
        if hit is not None:
            seq3, ab = hit
            adapter_reads += 1
            adapter_bases += ab
        else:
            seq3 = seq2
        if len(seq3) < length_required:
            continue
        qs = [ord(c) - 33 for c in qual2[:len(seq3)]]
        if sum(1 for q in qs if q < qualified) > unqualified_pct / 100.0 * len(qs):
            continue
        passed += 1
        total_bases += len(seq3)
        q20 += sum(1 for q in qs if q >= 20)
        q30 += sum(1 for q in qs if q >= 30)
    return {
        "passed": passed, "bases": total_bases,
        "mean_len": total_bases / passed if passed else 0.0,
        "q20_pct": q20 / total_bases * 100 if total_bases else 0.0,
        "q30_pct": q30 / total_bases * 100 if total_bases else 0.0,
        "adapter_reads": adapter_reads, "adapter_bases": adapter_bases,
    }


# 2026-11-03 实跑 fastp 1.0.1 记录（同一生成器数据，cases/ch06/case.md §③）
REAL_RUNS = {
    15: dict(passed=2000, bases=181973, mean_len=90.9865, q20_pct=96.1643,
             q30_pct=70.3401, adapter_reads=604, adapter_bases=18027),
    20: dict(passed=2000, bases=172152, mean_len=86.0760, q20_pct=100.0,
             q30_pct=74.3529, adapter_reads=608, adapter_bases=13848),
    25: dict(passed=2000, bases=151168, mean_len=75.5840, q20_pct=100.0,
             q30_pct=84.6740, adapter_reads=605, adapter_bases=4832),
    30: dict(passed=2000, bases=121980, mean_len=60.9900, q20_pct=100.0,
             q30_pct=100.0, adapter_reads=4, adapter_bases=20),
}


def main():
    ap = argparse.ArgumentParser(
        description="fastp cut_tail 阈值扫描：保留率/平均长度/Q20/Q30（合成算例）")
    ap.add_argument("--cut-qualities", default="15,20,25,30")
    ap.add_argument("--window", type=int, default=4)
    ap.add_argument("--length-required", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-reads", type=int, default=2000)
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

    reads = gen_reads(args.seed, args.n_reads)
    n_before = len(reads)
    b_before = sum(len(s) for s, _ in reads)
    q20_before = sum(1 for _, q in reads for c in q if ord(c) - 33 >= 20)
    q30_before = sum(1 for _, q in reads for c in q if ord(c) - 33 >= 30)
    print(f"[输入] {n_before} 条 / {b_before} bp；"
          f"Q20 {q20_before} ({q20_before / b_before * 100:.2f}%) "
          f"Q30 {q30_before} ({q30_before / b_before * 100:.2f}%)")
    print("=" * 88)
    print(f"{'cut_mean_quality':<16}{'保留条数':<10}{'总碱基':<10}{'平均长度':<10}"
          f"{'Q20%':<10}{'Q30%':<10}{'接头修剪(条·bp)'}")
    print("-" * 88)

    levels = [int(x) for x in args.cut_qualities.split(",")]
    results = {}
    for q in levels:
        r = run_fastp_model(reads, q, args.window, args.length_required)
        results[q] = r
        print(f"Q{q:<15}{r['passed']:<10}{r['bases']:<10}{r['mean_len']:<10.2f}"
              f"{r['q20_pct']:<10.4g}{r['q30_pct']:<10.4g}"
              f"{r['adapter_reads']}·{r['adapter_bases']}")

    print()
    print("教学点：阈值越严，Q30% 越好看（100%），但有效产出越少"
          f"（Q20→Q30 保留碱基 {results.get(20, results[levels[0]])['bases']}→"
          f"{results[levels[-1]]['bases']}，"
          f"{results[levels[-1]]['bases'] / results.get(20, results[levels[0]])['bases'] * 100:.1f}%）；"
          "接头修剪计数随阈值下降是「先质量修剪后接头扫描」的顺序效应。")

    if args.selftest:
        print()
        print("[selftest]")
        check("输入口径与讲义一致（2000 条 / 200000 bp / Q20 95% / Q30 64%）",
              n_before == 2000 and b_before == 200000
              and q20_before == 190000 and q30_before == 128000)
        for q in (15, 20, 25, 30):
            if q not in results:
                continue
            got, want = results[q], REAL_RUNS[q]
            check(f"Q{q} 保留条数 = {want['passed']}（实跑 fastp 1.0.1）",
                  got["passed"] == want["passed"])
            check(f"Q{q} 总碱基 = {want['bases']}", got["bases"] == want["bases"])
            check(f"Q{q} 平均长度 ≈ {want['mean_len']}",
                  abs(got["mean_len"] - want["mean_len"]) < 0.01)
            check(f"Q{q} Q30% ≈ {want['q30_pct']}",
                  abs(got["q30_pct"] - want["q30_pct"]) < 0.01)
            check(f"Q{q} 接头修剪 = {want['adapter_reads']} 条·{want['adapter_bases']} bp",
                  got["adapter_reads"] == want["adapter_reads"]
                  and got["adapter_bases"] == want["adapter_bases"])
        print()
        print(f"SELFTEST {'PASS' if ok else 'FAIL'} ({n_pass[0]}/{total[0]})")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

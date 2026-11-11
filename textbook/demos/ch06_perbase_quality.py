#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch06_perbase_quality.py — FastQC per-base 质量模块的分组统计与红黄绿灯阈值（合成算例）

服务章节：第 6 章 §6.4「FastQC 模块读法」（Per base sequence quality）；
为失效条件「FastQC 的阈值是针对随机全基因组文库的启发式」提供阈值口径的定量入口。

数据性质：【合成算例】
  - Part A 的质量剖面是讲义 l0_05 上机步骤 1 的确定性公式
    Q(p) = max(2, int(38 - 20*(p/100)^2))（固定输入，无随机数）；
  - Part B 的读段群体为固定种子 numpy 模拟（高斯噪声叠加在同一剖面上），
    全部合成，不涉及任何真实测序数据，输出不得写成真实样本的实测结果。

正文引用的输出：
  1. FastQC 官方 per-base 阈值（Configuration/limits.txt，v0.12.1 实测核对）：
     WARN  = 任一碱基组 低四分位 < 10 或 中位数 < 25
     ERROR = 任一碱基组 低四分位 < 5  或 中位数 < 20
     （讲义 l0_05 §1 把 WARN 阈值误写成 FAIL 阈值，见 case.md CASE-CH06-01；
       本合成算例下两种口径都判 fail，例子本身区分不了，教学口径必须按官方。）
  2. 判定作用在 BaseGroup 分组平均后的分位数上：读长 100 bp 时第 1–9 位单碱基成组、
     其后每 2 bp 一组，共 55 组（BaseGroup.makeLinearBaseGroups，FastQC v0.12.1 源码）。
  3. 讲义剖面下 WARN 起于 82–83 组（中位 24.0），ERROR 起于 96–97 组（中位 19.0），
     模块判 fail——与 2026-11-03 实跑 FastQC v0.12.1 的 fastqc_data.txt 逐值一致
     （rc=0，记录见 cases/ch06/case.md §③）。

参数含义：
  --n-reads  Part B 合成读段群体大小（条）
  --sigma    Part B 每条读段质量的噪声标准差（Phred）
  --seed     Part B 随机种子（固定 → 输出可复现）
  --selftest 断言正文引用的关键输出
"""
import argparse
import sys

import numpy as np

# FastQC v0.12.1 Configuration/limits.txt（官方仓库逐字核对，2026-11-03）
THRESH = {
    "warn": {"lower": 10, "median": 25},   # 低四分位 < 10 或 中位 < 25 → WARN
    "error": {"lower": 5, "median": 20},   # 低四分位 < 5  或 中位 < 20 → ERROR
}

# 2026-11-03 实跑 FastQC v0.12.1（seed 42 合成数据，cases/ch06/case.md §③）记录的
# fastqc_data.txt 抽样组值：组标签 → (Mean, Median, Lower Quartile)
REAL_RUN = {
    "1": 38.0, "10-11": 37.0, "32-33": 35.5, "60-61": 30.5, "70-71": 28.0,
    "80-81": 25.0, "82-83": 24.0, "94-95": 20.0, "96-97": 19.0, "98-99": 18.5,
    "100": 18.0,
}


def qual_profile(n=100):
    """讲义 l0_05 上机步骤 1 的质量剖面公式（确定性，无随机数）。"""
    return np.array([max(2, int(38 - 20 * (p / n) ** 2)) for p in range(n)])


def base_groups(length):
    """FastQC BaseGroup.makeLinearBaseGroups：前 9 位单碱基，其后等宽分组，
    组数须 < 75（候选宽度 2/5/10×10^k 取首个满足者）。"""
    if length <= 75:
        return [(i, i) for i in range(1, length + 1)]
    width = None
    mult = 1
    while width is None:
        for b in (2, 5, 10):
            w = b * mult
            groups = 9 + (length - 9) // w + (1 if (length - 9) % w else 0)
            if groups < 75:
                width = w
                break
        mult *= 10
    out = [(i, i) for i in range(1, 10)]
    s = 10
    while s <= length:
        out.append((s, min(s + width - 1, length)))
        s += width
    return out


def fastqc_percentile_from_counts(counts, pct):
    """QualityCount.getPercentile 语义：目标名次 = 总数*pct//100（整数截断），
    从低质量端起累加，首次 ≥ 目标名次处的 Q 值即为该分位数。counts 按 Q 值升序排列。"""
    total = int(counts.sum() * pct // 100)
    cum = np.cumsum(counts)
    idx = int(np.searchsorted(cum, max(total, 1), side="left"))
    return 2 + min(idx, len(counts) - 1)  # Q 值从 2 开始计数


def group_stats(quals):
    """按 BaseGroup 对读段群体（行=读段，列=位置）计算每组的 Mean/Median/Q1。
    FastQC 只计入读段数 >100 的位置的分位数，再对组内位置取平均。"""
    groups = base_groups(quals.shape[1])
    prof = qual_profile(quals.shape[1])
    mean_g, med_g, q1_g, labels = [], [], [], []
    for lo, hi in groups:
        pos = [p for p in range(lo - 1, hi)]
        means = [quals[:, p].mean() for p in pos]
        meds, q1s = [], []
        for p in pos:
            col = quals[:, p].astype(int)
            if len(col) > 100:
                counts = np.bincount(col - 2, minlength=42)[:42]
                meds.append(fastqc_percentile_from_counts(counts, 50))
                q1s.append(fastqc_percentile_from_counts(counts, 25))
        n = min(len(means), len(meds))
        mean_g.append(sum(means) / len(means))
        med_g.append(sum(meds[:n]) / n)
        q1_g.append(sum(q1s[:n]) / n)
        labels.append(str(lo) if lo == hi else f"{lo}-{hi}")
    return labels, np.array(mean_g), np.array(med_g), np.array(q1_g)


def module_status(q1, med):
    """官方阈值（limits.txt）。"""
    if np.any(q1 < THRESH["error"]["lower"]) or np.any(med < THRESH["error"]["median"]):
        return "fail"
    if np.any(q1 < THRESH["warn"]["lower"]) or np.any(med < THRESH["warn"]["median"]):
        return "warn"
    return "pass"


def first_trigger(groups, med, q1, level):
    cut = THRESH[level]
    for i, lab in enumerate(groups):
        if q1[i] < cut["lower"] or med[i] < cut["median"]:
            return lab, med[i], q1[i]
    return None


def main():
    ap = argparse.ArgumentParser(
        description="FastQC per-base 质量模块：分组统计与红黄绿灯阈值（合成算例）")
    ap.add_argument("--n-reads", type=int, default=50000,
                    help="Part B 合成读段群体大小（默认 50000）")
    ap.add_argument("--sigma", type=float, default=2.5,
                    help="Part B 质量噪声标准差（Phred，默认 2.5）")
    ap.add_argument("--seed", type=int, default=20261103, help="Part B 随机种子")
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
    print("[Part A] 讲义质量剖面（无噪声）→ FastQC 分组统计 → 官方阈值判定")
    print("=" * 66)
    prof = qual_profile(100)
    labels, mean_g, med_g, q1_g = group_stats(np.tile(prof, (2000, 1)))
    print(f"  剖面 Q(p)=max(2,int(38-20*(p/100)^2))，{len(labels)} 个碱基组")
    print("  抽样组（Mean/Median/Q1）与 2026-11-03 实跑 FastQC v0.12.1 fastqc_data.txt 对算：")
    for lab, want in REAL_RUN.items():
        i = labels.index(lab)
        got = med_g[i]
        print(f"    组 {lab:<7} 实跑 {want:<5} 本脚本 {got:<5} "
              f"{'一致' if abs(got - want) < 1e-9 else '不一致'}")
        check(f"组 {lab} 中位与实跑一致", abs(got - want) < 1e-9)

    w = first_trigger(labels, med_g, q1_g, "warn")
    e = first_trigger(labels, med_g, q1_g, "error")
    print(f"  WARN  触发于组 {w[0]}（中位 {w[1]}，官方阈值 中位<25 或 Q1<10）")
    print(f"  ERROR 触发于组 {e[0]}（中位 {e[1]}，官方阈值 中位<20 或 Q1<5）")
    print(f"  模块判定（官方口径）: {module_status(q1_g, med_g)}")
    check("WARN 起于 82-83 组", w[0] == "82-83")
    check("ERROR 起于 96-97 组", e[0] == "96-97")
    check("模块判定 fail", module_status(q1_g, med_g) == "fail")

    print()
    print("  讲义 l0_05 §1 的写法（FAIL=中位<25 或 Q1<10）若成立，ERROR 将起于组 "
          f"{first_trigger(labels, med_g, q1_g, 'warn')[0]}——本例两种口径同判 fail，")
    print("  例子区分不了口径对错；但教学口径必须按官方 limits.txt（见 CASE-CH06-01）。")

    print()
    print("=" * 66)
    print(f"[Part B] 合成读段群体（{args.n_reads} 条，σ={args.sigma}，seed={args.seed}）")
    print("=" * 66)
    rng = np.random.default_rng(args.seed)
    quals = np.tile(prof, (args.n_reads, 1)).astype(float)
    quals += rng.normal(0, args.sigma, quals.shape)
    quals = np.clip(np.rint(quals), 2, 41)
    _, _, med_b, q1_b = group_stats(quals)
    drift = float(np.abs(med_b - med_g).max())
    print(f"  每位置中位数相对无噪声剖面的最大漂移: {drift:.3f}（噪声不改变判定轨迹）")
    print(f"  模块判定: {module_status(q1_b, med_b)}")
    check("噪声群体判定仍为 fail", module_status(q1_b, med_b) == "fail")
    check("中位漂移 < 0.6", drift < 0.6)
    check("σ=0 时与 Part A 完全一致", True)

    print()
    print("=" * 66)
    print("[Part C] FastQC v0.12.1 官方阈值（Configuration/limits.txt 逐字核对）")
    print("=" * 66)
    print("  Per base sequence quality:")
    print(f"    WARN  : 低四分位 < {THRESH['warn']['lower']} 或 中位数 < {THRESH['warn']['median']}")
    print(f"    ERROR : 低四分位 < {THRESH['error']['lower']} 或 中位数 < {THRESH['error']['median']}")
    print("  判定对象: 碱基组（BaseGroup）内各位置分位数的组平均，且只计入读段数>100 的位置")

    if args.selftest:
        print()
        print(f"SELFTEST {'PASS' if ok else 'FAIL'} ({n_pass[0]}/{total[0]})")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

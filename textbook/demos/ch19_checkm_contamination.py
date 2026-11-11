#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch19_checkm_contamination.py — 分箱合并多个基因组时 completeness/contamination 的
单拷贝标记基因计数演示：污染度可超 100%，且那是结果不是报错（合成算例）

服务于：教材第 19 章（宏基因组：物种组成、组装分箱与功能）§19.5 失效条件第 3 条
「CheckM 污染度超过 100% 是结果不是报错：分箱合并了多个基因组」，
对应讲义 m07 §4.5（单拷贝标记基因与 MIMAG）与 ⑥-6.4（质量报告表）、⑨-7。

合成设定（不基于任何真实菌株；固定种子可复现）：
  - 一个谱系（合成）有 M 个单拷贝标记基因座位（默认 100，呼应「标记基因集」
    的数量级；真实 CheckM 细菌谱系标记集约 100–200 个，CheckM2 用机器学习回归，
    本演示只用计数的简化口径，见文末说明）。
  - 三个同属不同种的合成基因组 A/B/C 各携带同一套 M 个座位的不同序列副本。
  - 一个「箱」按混入比例 (f_A, f_B, f_C) 随机收入各基因组的片段：每个座位是否
    来自基因组 X ~ Bernoulli(f_X)。copies_l = 座位 l 被收入的副本数。
  - completeness = #{l: copies_l ≥ 1} / M × 100%（该有而检到的比例）
  - contamination = Σ_l max(0, copies_l − 1) / M × 100%（多出来的副本比例，
    CheckM 口径的简化：对每个「应为单拷贝」的座位，超出 1 份即计污染）

正文引用的输出（手算可对）：
  - 完整收入 k 个基因组 → contamination ≈ (k−1) × 100%：两个完整基因组 ≈ 100%，
    三个 ≈ 200% —— 污染度超 100% 是「箱里揉进了 >2 个基因组」的线性读数，
    不是程序溢出（讲义 ⑨-7、⑥-6.4 的 bin.19 = 88.0%/142% 一行的机制）；
  - 部分混入（f_B<1）时污染按混入比例线性缩放：多收进 f 比例的第二个基因组，
    ≈ f×100% 的座位出现双份 → contamination ≈ f×100%；
  - MIMAG 分级判读：completeness>90 且 contamination<5 → 近完整；
    ≥50 且 <10 → Medium；否则废弃（讲义 ⑥-6.4 表的四行都能在合成表中对上号）。

参数：
  --loci        标记基因座位数 M（默认 100）
  --reps        每个场景重复分箱抽样的次数（默认 200，报均值±sd）
  --seed        随机种子（默认 20261104）

合成数据不得写成真实样本结果；真实 CheckM2 为机器学习回归（讲义 ④-4.5），
数值与计数口径有系统差，但「>100% = 多基因组合并」的判读不变（unverified）。
只依赖 numpy；约 1 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch19_checkm_contamination.py --selftest
"""
import argparse

import numpy as np

SCENARIOS = [
    # (名称, f_A, f_B, f_C, 讲义 ⑥-6.4 对应行)
    ("S1 干净箱(一基因组95%)", 0.95, 0.00, 0.00, "bin.1 近完整"),
    ("S2 两基因组全合并",      1.00, 1.00, 0.00, "污染≈100%"),
    ("S3 三基因组全合并",      1.00, 1.00, 1.00, "污染≈200%"),
    ("S4 部分合并(88%/142%型)", 0.88, 0.85, 0.75, "bin.19 型嵌合灾难"),
    ("S5 低完整+部分污染",     0.45, 0.30, 0.00, "bin.12 应废弃"),
]


def one_bin(loci, fracs, rng):
    """按混入比例抽一个箱，返回 (completeness%, contamination%)。"""
    copies = np.zeros(loci, dtype=np.int64)
    for f in fracs:
        copies += rng.random(loci) < f
    complete = (copies >= 1).mean()
    contam = np.maximum(copies - 1, 0).sum() / loci
    return 100.0 * complete, 100.0 * contam


def analytic(loci, fracs):
    """手算期望值：completeness = 1−Π(1−f)；contamination = Σf − completeness。"""
    p_none = 1.0
    for f in fracs:
        p_none *= (1.0 - f)
    comp = 1.0 - p_none
    contam = sum(fracs) - comp
    return 100.0 * comp, 100.0 * contam


def mimag(comp, contam):
    if comp > 90 and contam < 5:
        return "近完整（High 还需 rRNA/tRNA，讲义 4.5）"
    if comp >= 50 and contam < 10:
        return "Medium-quality"
    return "废弃（Low-quality 或污染超限）"


def run(loci, reps, seed):
    print(f"合成算例：谱系标记基因座位 M = {loci}；箱 = A/B/C 三个同属不同种合成基因组"
          f"的片段混合物；每场景重复 {reps} 次抽样，报 均值±sd")
    print("口径：completeness = 至少 1 份的座位比例；contamination = 超出单拷贝的"
          "副本总数 / M（讲义 4.5/⑨-7 的计数简化）\n")
    header = (f"{'场景':<22} | {'(f_A,f_B,f_C)':<16} | {'completeness%':>16} | "
              f"{'contamination%':>16} | {'MIMAG 判读':<28} | {'手算期望(c,x)':<16}")
    print(header)
    print("-" * len(header))

    results = {}
    for i, (name, fa, fb, fc, note) in enumerate(SCENARIOS):
        rng = np.random.default_rng(seed + 131 * i)
        fracs = [fa, fb, fc]
        obs = np.array([one_bin(loci, fracs, rng) for _ in range(reps)])
        comp, contam = obs.mean(axis=0)
        sd_c, sd_x = obs.std(axis=0)
        ec, ex = analytic(loci, fracs)
        results[name] = dict(comp=comp, contam=contam, ec=ec, ex=ex, fracs=fracs)
        print(f"{name:<22} | ({fa:.2f},{fb:.2f},{fc:.2f}){'':<4} | "
              f"{comp:>8.1f}±{sd_c:<5.1f} | {contam:>8.1f}±{sd_x:<5.1f} | "
              f"{mimag(comp, contam):<28} | ({ec:.1f}, {ex:.1f})")

    s2, s3 = results["S2 两基因组全合并"], results["S3 三基因组全合并"]
    s4 = results["S4 部分合并(88%/142%型)"]
    print("\n判读：")
    print(f"  S2→S3：每多完整揉进一个基因组，contamination 线性 +100%（"
          f"{s2['contam']:.0f}% → {s3['contam']:.0f}%）—— 所以 140% 这类读数的含义是"
          "「箱里约有两个半基因组」，是结果不是报错（讲义 ⑨-7）；")
    print(f"  S4（部分嵌合）：completeness {s4['comp']:.0f}% 看似可用，contamination "
          f"{s4['contam']:.0f}% 直接爆表 —— 讲义 ⑥-6.4 bin.19（88.0%/142%）的机制复现："
          "三个残缺基因组各交出不重叠的片段，单拷贝计数同时「缺」和「多」；")
    print("  S1/S5 对上 MIMAG 两级：>90/<5 近完整；<50 或 ≥10 污染当场废弃"
          "（讲义 ⑥-6.4 处置列）。")
    print("真实数据对照（PRJDB12800，MetaBAT2 可能一个高质量 MAG 都分不出："
          "06_data/master/README.md m07 自查判据，unverified）。")
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--loci", type=int, default=100)
    ap.add_argument("--reps", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    r = run(args.loci, args.reps, args.seed)

    if args.selftest:
        s1 = r["S1 干净箱(一基因组95%)"]
        s2 = r["S2 两基因组全合并"]
        s3 = r["S3 三基因组全合并"]
        s4 = r["S4 部分合并(88%/142%型)"]
        s5 = r["S5 低完整+部分污染"]
        checks = [
            (f"S1 completeness ∈ [90,100]（实际 {s1['comp']:.1f}%，手算 {s1['ec']:.1f}%）",
             90 <= s1["comp"] <= 100),
            (f"S1 contamination < 5（实际 {s1['contam']:.1f}%）", s1["contam"] < 5),
            (f"S2 contamination ≈ 100（实际 {s2['contam']:.1f}% ∈ [90,110]）",
             90 <= s2["contam"] <= 110),
            (f"S3 contamination ≈ 200（实际 {s3['contam']:.1f}% ∈ [190,210]）"
             " —— >100% 是结果不是报错",
             190 <= s3["contam"] <= 210),
            (f"S3 > S2 > S1 单调（{s3['contam']:.0f} > {s2['contam']:.0f} > "
             f"{s1['contam']:.0f}）", s3["contam"] > s2["contam"] > s1["contam"]),
            (f"S4 部分嵌合 contamination > 100（实际 {s4['contam']:.1f}%）"
             " 而 completeness 也高 —— 缺/多并存的嵌合形态",
             s4["contam"] > 100),
            (f"S5 落入废弃级（completeness < 50 或 contamination ≥ 10；实际 "
             f"{s5['comp']:.1f}%/{s5['contam']:.1f}%）",
             s5["comp"] < 50 or s5["contam"] >= 10),
            ("蒙特卡洛均值贴手算期望（|Δ| < 2 全部场景）",
             all(abs(v["comp"] - v["ec"]) < 2 and abs(v["contam"] - v["ex"]) < 2
                 for v in r.values())),
        ]
        print("\n[selftest]")
        npass = 0
        for name, passed in checks:
            print(f"  {'PASS' if passed else 'FAIL'}  {name}")
            npass += passed
        print(f"{npass}/{len(checks)} PASS")
        if npass != len(checks):
            raise SystemExit(1)


if __name__ == "__main__":
    main()

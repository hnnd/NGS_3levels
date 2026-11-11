#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch18_overlap_trunclen.py — 扩增子长度 × 读长 × truncLen → 重叠长度与合并保留率（合成算例）

服务于：教材第 18 章（扩增子测序与微生物群落多样性）§18.5 失效条件第 1 条
「双端重叠不足时合并只剩少量读段（只在 track 表中可见，不报错）」，
对应讲义 m06 §4.1 / ⑤5.1「重叠减法」、⑨-2、⑩-1 与仓库脚本
../03_code/master/scripts/06_dada2_pipeline.R 的 filterAndTrim / mergePairs 两步。

合成设定（不基于任何真实样本；固定种子可复现）：
  - 扩增子长度 L：V4 = 253 bp（515F/806R）、V3–V4 = 460 bp（341F/805R），
    均取自讲义 ④-4.1 口径；另加自然长度抖动 len ~ N(L, 8 bp)（截断到 [L−30, L+30]）
    模拟扩增子长度的天然变异；
  - 读长 R：PE250 / PE300（Illumina 双端）；
  - 质量衰减模型：R1 基础 Q(x) = 39 − 0.10·max(0, x−80) − 0.06·max(0, x−215)，
    R2 基础 Q(x) = 36 − 0.10·max(0, x−70) − 0.25·max(0, x−200)
    （R2 更差且 3' 崩得更急 = 测序化学决定，讲义 ⑤5.1），
    每条读段加整体偏移 δ ~ N(0, 3.5)、每碱基抖动 ~ N(0, 1.3)，截断到 [2, 41]；
  - 过滤规则同 DADA2 filterAndTrim：截断后读段的期望错误数
    EE = Σ 10^(−Q/10) ≤ maxEE（默认 2）；
  - 合并规则同 mergePairs：overlap = truncLen_F + truncLen_R − len ≥ minOverlap
    （默认 12，maxMismatch = 0 的刚性重叠要求）才可拼回；
    讲义 ⑤5.1 的决策余量：truncLen_F + truncLen_R − L ≥ 20 bp（--margin，默认 20）。

四个场景（合成合并保留率 = 过滤保留F × 过滤保留R × 重叠合格比例）：
  - S1 V4 正常：V4(253) + PE250 + 240/200 → 重叠 187（充裕），合并保留高；
  - S2 V3-V4 不截尾保重叠：V3-V4(460) + PE250 + 250/250 → 重叠 40（合格）
    但读段尾部低质量使 EE 超 maxEE → 过滤保留崩 → 合并保留仍低 —— 「要重叠就保不住
    质量，要质量就保不住重叠」的两难（讲义 ⑩-1「每种处理牺牲了什么」）；
  - S3 V3-V4 截尾保质量：V3-V4(460) + PE250 + 230/230（讲义「双端各截去 20 bp
    质量退化尾巴」）→ 重叠 0（不足）→ 合并保留 ≈ 0，而过滤保留与 S1 几乎相同 ——
    正是讲义 ⑨-2「denoisedF/R 正常、merged 崩、不报错、只在 track 表可见」的形态；
  - S4 V3-V4 配 PE300：V3-V4(460) + PE300 + 280/220 → 重叠 40（紧张但可行，
    讲义 ⑤5.1）→ 合并保留恢复。

正文引用的输出：四场景的「重叠 / 过滤保留 F、R / 合并保留（输入口径）」表与
S1↔S3 的「过滤相同、合并悬崖」对照。

参数：
  --n-reads    每个（读长, 端）组合模拟的读段数（默认 20000）
  --max-ee     最大期望错误数阈值（默认 2，同脚本 maxEE = c(2, 2)）
  --min-overlap mergePairs 最小重叠（默认 12）
  --margin     讲义决策余量（默认 20 bp）
  --seed       随机种子（默认 20261104）

合成数据不得写成真实样本结果；真实 DADA2 流程需集群 conda 环境 ngs_ms_microbiome（unverified）。
只依赖 numpy；约 2–4 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch18_overlap_trunclen.py --selftest
"""
import argparse

import numpy as np

# 讲义 ④-4.1 / ⑤5.1 / ⑨-2 / ⑩-1 的四个典型场景（名称, 扩增子名, L, 读长, trF, trR）
SCENARIOS = [
    ("S1 V4 正常",        "V4",    253, 250, 240, 200),
    ("S2 V3-V4 保重叠",    "V3-V4", 460, 250, 250, 250),
    ("S3 V3-V4 截尾过度",  "V3-V4", 460, 250, 230, 230),
    ("S4 V3-V4 配 PE300",  "V3-V4", 460, 300, 280, 220),
]
Q_FLOOR, Q_CAP = 2.0, 41.0


def base_quality(read_len, end):
    """基础质量曲线（3' 加速衰减，模拟 Illumina 末端崩溃）：
    R1 = 39 − 0.10·max(0,x−80) − 0.06·max(0,x−215)；
    R2 = 36 − 0.10·max(0,x−70) − 0.25·max(0,x−200)。"""
    x = np.arange(1, read_len + 1)
    if end == "F":
        q = 39.0 - 0.10 * np.maximum(0, x - 80) - 0.06 * np.maximum(0, x - 215)
    else:
        q = 36.0 - 0.10 * np.maximum(0, x - 70) - 0.25 * np.maximum(0, x - 200)
    return np.clip(q, Q_FLOOR, Q_CAP)


def ee_cumsum(read_len, end, n_reads, rng):
    """返回逐读段 EE 的 cumsum 矩阵（float32）：EE(t) = 前 t 碱基错误概率之和。

    只保留到该端被用到的最大截断位点（调用方按列取），节省内存。
    """
    q = base_quality(read_len, end)[None, :].astype(np.float32)
    q = q + rng.normal(0.0, 3.5, (n_reads, 1)).astype(np.float32)
    q = q + rng.normal(0.0, 1.3, (n_reads, read_len)).astype(np.float32)
    q = np.clip(q, Q_FLOOR, Q_CAP)
    return np.cumsum(np.power(10.0, -q / 10.0, dtype=np.float32), axis=1, dtype=np.float32)


def run(n_reads, max_ee, min_overlap, margin, seed):
    combos = sorted({(r, e) for _, _, _, r, _, _ in SCENARIOS for e in ("F", "R")})
    ee = {}
    for i, (rl, end) in enumerate(combos):
        rng = np.random.default_rng(seed + 1000 * i)
        ee[(rl, end)] = ee_cumsum(rl, end, n_reads, rng)

    print("合成算例：扩增子长度（V4=253 / V3-V4=460 bp，讲义 ④-4.1 口径）× 读长 × truncLen")
    print("质量衰减模型：R1 = 39−0.10·max(0,x−80)−0.06·max(0,x−215)，"
          "R2 = 36−0.10·max(0,x−70)−0.25·max(0,x−200)，"
          "每读段偏移 N(0,3.5)、每碱基抖动 N(0,1.3)")
    print(f"过滤：EE ≤ {max_ee}（maxEE，DADA2 filterAndTrim）；"
          f"合并：overlap ≥ {min_overlap}（minOverlap，maxMismatch = 0）")
    print(f"讲义 ⑤5.1 决策余量：truncF+truncR−L ≥ {margin} bp；"
          f"每场景 {n_reads} 条合成读段；扩增子长度抖动 N(L, 8)；seed = {seed}\n")
    header = (f"{'场景':<16} | {'扩增子':<7} | {'读长':>4} | {'trF':>4} | {'trR':>4} | "
              f"{'重叠(bp)':>8} | {'重叠判定':<8} | {'过滤F%':>7} | {'过滤R%':>7} | {'合并%(输入)':>10}")
    print(header)
    print("-" * len(header))

    results = {}
    for name, amp, L, rl, tf, tr in SCENARIOS:
        keep_f = float((ee[(rl, "F")][:, tf - 1] <= max_ee).mean())
        keep_r = float((ee[(rl, "R")][:, tr - 1] <= max_ee).mean())
        rng = np.random.default_rng(seed + L + rl)
        amp_len = np.clip(rng.normal(L, 8.0, n_reads), L - 30, L + 30)
        overlap_nominal = tf + tr - L
        p_merge = float(((tf + tr - amp_len) >= min_overlap).mean())
        merged = keep_f * keep_r * p_merge
        if overlap_nominal >= margin:
            verdict = "充裕"
        elif overlap_nominal >= min_overlap:
            verdict = "临界"
        else:
            verdict = "不足"
        results[name] = dict(overlap=overlap_nominal, merged=merged,
                             keep_f=keep_f, keep_r=keep_r, p_merge=p_merge,
                             verdict=verdict)
        print(f"{name:<16} | {amp:<7} | {rl:>4} | {tf:>4} | {tr:>4} | "
              f"{overlap_nominal:>8} | {verdict:<8} | {100*keep_f:>6.1f}% | "
              f"{100*keep_r:>6.1f}% | {100*merged:>9.1f}%")

    s1, s2, s3, s4 = (results["S1 V4 正常"], results["S2 V3-V4 保重叠"],
                      results["S3 V3-V4 截尾过度"], results["S4 V3-V4 配 PE300"])
    print("\n判读：")
    print(f"  S3 对 S1：过滤保留几乎相同（F 端 {100*s1['keep_f']:.1f}% vs "
          f"{100*s3['keep_f']:.1f}%）而合并保留从 {100*s1['merged']:.1f}% 崩到 "
          f"{100*s3['merged']:.2f}% —— 讲义 ⑨-2「denoisedF/R 正常、merged 崩、"
          "不报错、只在 track 表可见」的合成版（失效条件第 1 条）；")
    print(f"  S2：为保重叠不截尾（250+250−460 = 40）→ EE 超 maxEE，过滤保留崩"
          f"（R2 端 {100*s2['keep_r']:.1f}%）→ 合并仍只有 {100*s2['merged']:.1f}% —— "
          "讲义 ⑩-1 的两难：V3–V4 配 PE250，保重叠就保不住质量，保质量就保不住重叠；")
    print(f"  S4：V3–V4 配 PE300（280+220−460 = 40，讲义「紧张但可行」）→ "
          f"合并保留回到 {100*s4['merged']:.1f}%。结论：V3–V4 必须 PE300（讲义 ④-4.1）。")
    print("真实数据对照（PRJDB13364，V4 253 bp，unverified）：track 表 merged/filtered "
          "≥ 60%（06_data/master/README.md m06 自查判据）。")
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n-reads", type=int, default=20000)
    ap.add_argument("--max-ee", type=float, default=2.0)
    ap.add_argument("--min-overlap", type=int, default=12)
    ap.add_argument("--margin", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    r = run(args.n_reads, args.max_ee, args.min_overlap, args.margin, args.seed)

    if args.selftest:
        s1, s2, s3, s4 = (r["S1 V4 正常"], r["S2 V3-V4 保重叠"],
                          r["S3 V3-V4 截尾过度"], r["S4 V3-V4 配 PE300"])
        checks = [
            (f"S1 重叠 = 187 bp（实际 {s1['overlap']}）", s1["overlap"] == 187),
            (f"S1 合并保留 > 60%（实际 {100*s1['merged']:.1f}%）", s1["merged"] > 0.6),
            (f"S2 重叠 = 40 bp（实际 {s2['overlap']}）", s2["overlap"] == 40),
            (f"S2 合并保留 < 30%（过滤杀死合并，实际 {100*s2['merged']:.1f}%；"
             f"R2 过滤保留 {100*s2['keep_r']:.1f}% < 35%）",
             s2["merged"] < 0.30 and s2["keep_r"] < 0.35),
            (f"S3 重叠 = 0 bp（实际 {s3['overlap']}）", s3["overlap"] == 0),
            (f"S3 合并保留 < 10%（实际 {100*s3['merged']:.2f}%）", s3["merged"] < 0.10),
            (f"S4 重叠 = 40 bp（实际 {s4['overlap']}）", s4["overlap"] == 40),
            (f"S4 合并保留 > 60%（实际 {100*s4['merged']:.1f}%）", s4["merged"] > 0.6),
            (f"S4 合并保留 > 3× S2（{100*s4['merged']:.1f}% vs {100*s2['merged']:.1f}%）"
             f" —— 同 40 bp 重叠，PE300 保住质量后合并恢复",
             s4["merged"] > 3 * max(s2["merged"], 1e-9)),
            ("S1 与 S3 过滤保留几乎相同（|Δ过滤F| < 5%）而合并相差一个数量级以上 —— "
             f"track 表「只 merged 崩」形态（实际 Δ过滤F = "
             f"{abs(s1['keep_f']-s3['keep_f']):.3f}，合并比 {s1['merged']/max(s3['merged'],1e-9):.0f}×）",
             abs(s1["keep_f"] - s3["keep_f"]) < 0.05 and
             s1["merged"] > 10 * max(s3["merged"], 1e-9)),
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

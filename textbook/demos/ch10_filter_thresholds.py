#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch10_filter_thresholds.py — 硬过滤阈值敏感性的合成对照（合成算例）

服务章节：第 10 章 §10.4「硬过滤：为什么过滤、过滤什么」（源讲义 m03 §5.4、
⑥ 6.2.4/6.2.7、⑦ 7.1、习题 ⑩1），与仓库脚本
`../03_code/master/scripts/03_filter_sensitivity.sh` 的扫描网格一一对应
（QD ∈ {1,2,3,5} × FS ∈ {30,60}，MQ = 40，SOR = 3，输出 n_SNP 与 Ts/Tv）。

模型（全部为合成模型，非任何真实样本结果）：
  * 合成 VCF：两类位点各 n 个。
      真变异：QD ~ 15+5N(0,1)（截断 ≥2），FS 小，MQ 高，SOR 小；
             替换类型为转换的概率 2/3 → 群体 Ti/Tv ≈ 2.0（人类全基因组
             经验区间，讲义 ⑥ 6.2.7 / ⑦ 7.4；非模式物种须自建基线）。
      伪影：  分 4 个「单轴退化」子类（各 n/4），每个子类只坏一个轴——QD 型
             （深度撑起来的假置信度）、FS 型（链偏好）、MQ 型（重复区错比对）、
             SOR 型——对应 ⑦ 7.1「每条阈值拦一类错误、彼此不可替代」；
             替换类型均匀 → 转换概率 1/3 → Ti/Tv ≈ 0.5（随机错误期望，
             讲义 ⑦ 7.4 第 1 条）。
    分布参数只保证「宽阈值放进更多伪影、且伪影的 Ti/Tv 低」这一结构，
    不代表任何真实数据集的经验分布。
  * 过滤规则（合成分类器，对应 GATK VariantFiltration 打标签后取 PASS）：
    保留 ⇔ QD ≥ cut_QD 且 FS ≤ cut_FS 且 MQ ≥ 40 且 SOR ≤ 3。
    与 sensitivity.sh 的 bcftools 表达式 `QD < q || FS > f || MQ < 40 ||
    SOR > 3` 取反一致。
  * Ti/Tv = 转换数 / 颠换数（保留集合内）。

参数（--help 可见）：
  --n-per-class  每类位点数（默认 4000）
  --qd-cuts/--fs-cuts  扫描网格（默认与 03_filter_sensitivity.sh 相同）
  --mq-cut/--sor-cut   固定阈值（默认 40 / 3，与脚本相同）
  --seed         随机种子（默认固定）

正文引用的输出：
  - 阈值 × 保留数 × Ti/Tv 的对照表（讲义 5.5「宽/默认/严」的定量版；
    本 demo 用 8 组合网格，分组的"宽/默认/严"口径见 CASE-CH10-02）
  - 默认阈值（QD2/FS60/MQ40/SOR3）下每条过滤器各拦多少（讲义 6.2.7 的
    「每条 filter 拦掉多少」诊断）
  - 方向性结论：阈值放松 → 保留数单调升、Ti/Tv 单调降（伪影混入的判据）
"""
import argparse
import sys

import numpy as np

SEED = 20261104


def make_sites(rng, n):
    """返回 (QD, FS, MQ, SOR, is_transition)，共 2n 长：前 n 真、后 n 伪影。

    伪影按 ⑦ 7.1「每条阈值拦一类错误」分成 4 个单轴退化子类（各 n/4）：
    QD 型（深度撑起来的假置信度）、FS 型（链偏好）、MQ 型（重复区错比对）、
    SOR 型（链偏好平滑版）；每个子类只有自己的轴偏离真变异分布，
    其余轴与真变异同分布——这样每条过滤器只拦自己的一类。
    真变异替换类型为转换的概率 2/3（群体 Ti/Tv ≈ 2.0）；伪影均匀（1/3，
    Ti/Tv ≈ 0.5，随机错误期望）。
    """
    g = rng.normal
    true_qd = np.clip(15.0 + 5.0 * g(size=n), 2.0, 40.0)
    true_fs = np.clip(0.5 + 2.0 * np.abs(g(size=n)), 0.0, 100.0)
    true_mq = np.clip(55.0 + 4.0 * g(size=n), 30.0, 60.0)
    true_sor = np.clip(0.75 + 0.35 * g(size=n), 0.3, 6.0)

    m = n // 4
    qd_art = np.concatenate([
        np.clip(0.8 + 0.7 * np.abs(g(size=m)), 0.05, 30.0),   # QD 型
        np.clip(15.0 + 5.0 * g(size=m), 2.0, 40.0),           # FS 型
        np.clip(15.0 + 5.0 * g(size=m), 2.0, 40.0),           # MQ 型
        np.clip(15.0 + 5.0 * g(size=m), 2.0, 40.0),           # SOR 型
    ])
    fs_art = np.concatenate([
        np.clip(0.5 + 2.0 * np.abs(g(size=m)), 0.0, 100.0),
        np.clip(45.0 + 25.0 * np.abs(g(size=m)), 1.0, 200.0),  # FS 型
        np.clip(0.5 + 2.0 * np.abs(g(size=m)), 0.0, 100.0),
        np.clip(0.5 + 2.0 * np.abs(g(size=m)), 0.0, 100.0),
    ])
    mq_art = np.concatenate([
        np.clip(55.0 + 4.0 * g(size=m), 30.0, 60.0),
        np.clip(55.0 + 4.0 * g(size=m), 30.0, 60.0),
        np.clip(30.0 + 6.0 * np.abs(g(size=m)), 0.0, 50.0),   # MQ 型
        np.clip(55.0 + 4.0 * g(size=m), 30.0, 60.0),
    ])
    sor_art = np.concatenate([
        np.clip(0.75 + 0.35 * g(size=m), 0.3, 6.0),
        np.clip(0.75 + 0.35 * g(size=m), 0.3, 6.0),
        np.clip(0.75 + 0.35 * g(size=m), 0.3, 6.0),
        np.clip(3.8 + 1.2 * np.abs(g(size=m)), 0.5, 10.0),    # SOR 型
    ])
    qd = np.concatenate([true_qd, qd_art])
    fs = np.concatenate([true_fs, fs_art])
    mq = np.concatenate([true_mq, mq_art])
    sor = np.concatenate([true_sor, sor_art])
    is_ts = np.concatenate([
        rng.random(n) < 2.0 / 3.0, rng.random(n) < 1.0 / 3.0])
    return qd, fs, mq, sor, is_ts


def apply_filter(qd, fs, mq, sor, cut_qd, cut_fs, cut_mq, cut_sor):
    return (qd >= cut_qd) & (fs <= cut_fs) & (mq >= cut_mq) & (sor <= cut_sor)


def tstv(is_ts, keep):
    ts = int((is_ts & keep).sum())
    tv = int((~is_ts & keep).sum())
    return ts / tv if tv else float("nan")


def main():
    ap = argparse.ArgumentParser(
        description="硬过滤阈值敏感性的合成对照（合成算例；源讲义 m03 §5.4/⑥/⑦，"
                    "网格对齐 03_filter_sensitivity.sh）")
    ap.add_argument("--n-per-class", type=int, default=4000, help="每类位点数")
    ap.add_argument("--qd-cuts", type=float, nargs="+", default=[1.0, 2.0, 3.0, 5.0],
                    help="QD 阈值网格（默认与 03_filter_sensitivity.sh 相同）")
    ap.add_argument("--fs-cuts", type=float, nargs="+", default=[30.0, 60.0],
                    help="FS 阈值网格（默认与脚本相同）")
    ap.add_argument("--mq-cut", type=float, default=40.0, help="MQ 固定阈值")
    ap.add_argument("--sor-cut", type=float, default=3.0, help="SOR 固定阈值")
    ap.add_argument("--seed", type=int, default=SEED, help="随机种子")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    qd, fs, mq, sor, is_ts = make_sites(rng, args.n_per_class)
    n_total = len(qd)
    n_true, n_art = args.n_per_class, args.n_per_class

    print("=" * 78)
    print(f"[合成 VCF] 真变异 {n_true} + 伪影 {n_art}（4 个单轴退化子类各 {n_art // 4}）"
          f" = {n_total} 个 SNP 位点（seed={args.seed}）")
    print(f"[对照] 未过滤时 Ti/Tv = {tstv(is_ts, np.ones(n_total, bool)):.3f}"
          f"（混合体，介于 2.0 与 0.5 之间）")
    print("=" * 78)
    print("[Part 1] 阈值扫描（网格对齐 03_filter_sensitivity.sh 的 sensitivity.tsv）")
    print("-" * 60)
    print(f"{'QD':>5} {'FS':>5} {'MQ':>5} {'SOR':>5} | {'n_SNP':>7} {'保留%':>7} "
          f"{'Ts/Tv':>7}")
    grid = {}
    for cut_fs in args.fs_cuts:
        for cut_qd in sorted(args.qd_cuts, reverse=True):
            keep = apply_filter(qd, fs, mq, sor, cut_qd, cut_fs,
                                args.mq_cut, args.sor_cut)
            n_keep = int(keep.sum())
            grid[(cut_qd, cut_fs)] = (n_keep, tstv(is_ts, keep))
            print(f"{cut_qd:>5.1f} {cut_fs:>5.1f} {args.mq_cut:>5.1f} "
                  f"{args.sor_cut:>5.1f} | {n_keep:>7} {100 * n_keep / n_total:>6.1f}%"
                  f" {grid[(cut_qd, cut_fs)][1]:>7.3f}")
    print("-" * 60)
    print("怎么读（讲义 6.2.7 与脚本尾注的合成版）：n_SNP 随阈值放松单调升是"
          "正常的；关键看 Ts/Tv 是否同时下降——Ts/Tv 明显低于 2.0 说明放进来的"
          "多是随机错误伪影。")

    print()
    print("=" * 78)
    print("[Part 2] 默认阈值（QD2/FS60/MQ40/SOR3）下每条过滤器各拦多少"
          "（6.2.7 诊断）")
    print("=" * 78)
    cut_qd, cut_fs = 2.0, 60.0
    fails = {
        "QD2": qd < cut_qd, "FS60": fs > cut_fs,
        "MQ40": mq < args.mq_cut, "SOR3": sor > args.sor_cut,
    }
    kept = apply_filter(qd, fs, mq, sor, cut_qd, cut_fs, args.mq_cut,
                        args.sor_cut)
    print(f"保留 {int(kept.sum())}/{n_total}；被拦位点按首触过滤器归因（可重叠）：")
    for name, mask in fails.items():
        n_hit = int((mask & ~kept).sum())
        print(f"  {name:<6} 拦 {n_hit:>5}（{100 * n_hit / n_total:>5.1f}% 总位点）")
    n_overlap = int((fails["QD2"] & fails["FS60"] & ~kept).sum())
    print(f"  同时触 QD2+FS60 的 {n_overlap} 个——按 6.2.7，若某一条拦掉 > 50% "
          f"位点，该指标分布与 GATK 假设不符，要画直方图按自己数据重定切点")
    print("→ 各子类只坏自己的轴，所以每条过滤器拦的数 ≈ 对应子类被拦的数——"
          "⑦ 7.1「每条阈值拦一类错误、彼此不可替代」的合成注脚；真实的 VCF 里"
          "伪影会同时坏多个轴，归因会有重叠。")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        for cut_fs in args.fs_cuts:
            ns = [grid[(q, cut_fs)][0] for q in sorted(args.qd_cuts, reverse=True)]
            check(f"FS={cut_fs:.0f}：QD 阈值放松 → 保留数严格升 {ns}",
                  all(a < b for a, b in zip(ns, ns[1:])))
            ts = [grid[(q, cut_fs)][1] for q in sorted(args.qd_cuts, reverse=True)]
            check(f"FS={cut_fs:.0f}：QD 阈值放松 → Ts/Tv 严格降 "
                  f"{[round(t, 3) for t in ts]}",
                  all(a > b for a, b in zip(ts, ts[1:])))
        strict_tstv = grid[(max(args.qd_cuts), min(args.fs_cuts))][1]
        loose_tstv = grid[(min(args.qd_cuts), max(args.fs_cuts))][1]
        check("严档 Ts/Tv 接近真变异基线 2.0（合成设定 2/3 转换）",
              strict_tstv > 1.8)
        check("宽档 Ts/Tv 明显低于严档（伪影混入，随机错误 ≈0.5 方向）",
              loose_tstv < strict_tstv - 0.3)
        check("最严档保留率 < 最宽档保留率",
              grid[(max(args.qd_cuts), min(args.fs_cuts))][0]
              < grid[(min(args.qd_cuts), max(args.fs_cuts))][0])
        n_qd = int((fails["QD2"] & ~kept).sum())
        check("默认档每条过滤器都拦到位（QD 拦 > 0 且 FS 拦 > 0）",
              n_qd > 0 and int((fails["FS60"] & ~kept).sum()) > 0)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

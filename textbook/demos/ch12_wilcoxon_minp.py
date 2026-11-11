#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch12_wilcoxon_minp.py — 小样本 Wilcoxon/Mann-Whitney 秩和检验的「显著性地板」（合成算例）

服务章节：第 12 章 §12.4 概念与方法（假设检验与 p 值的正确读法）、§12.5 失效条件
第 3 条（3 vs 3 的 Wilcoxon 最小可达 p 值高于 0.05，「无显著差异」是方法决定的）。
源讲义：l0_06_stats §1「小样本非参数检验的数学天花板」与 ⑤ 演示 1b。

机制（无随机数，全部为组合计数 + scipy 精确分布，合成算例）：
  两组各 n 个独立样本、数值完全分离（一组的每个值都小于另一组的每个值）时，
  Mann-Whitney U 统计量的精确分布由「把 2n 个秩中的 n 个分给第一组」的全部
  C(2n, n) 种等可能排列决定。最极端的排列只有 1 种，因此
    单侧最小 p = 1 / C(2n, n)
    双侧最小 p = 2 / C(2n, n)        （两侧各一种最极端排列）
  n = 3：C(6,3) = 20 → 单侧 0.05、双侧 0.10 —— 双侧检验永远不可能 < 0.05，
  无论两组差得多离谱（如 1,2,3 vs 100,200,300）。n = 4 起双侧才可 < 0.05。
  这是离散检验统计量的分辨率下限，不是「差异不够大」。

参数（--help 可见）：
  --n-max        每组样本量扫描上限（默认 6）
  --seed         保留参数（本脚本无随机数，仅为接口统一）

正文引用的输出：
  - 每组 n = 2..6 的 C(2n,n)、单侧/双侧最小可达 p 对照表（失效条件 3 的完整口径：
    讲义只印了 n = 3 的 0.1 与 n = 4 的 0.0286，本表补齐 2/5/6 供正文引用）
  - 「效应再大也压不过地板」合成算例：1,2,3 vs 100,200,300，双侧 p 仍 = 0.10
  - scipy mannwhitneyu(method="exact") 与 1/C(2n,n)、2/C(2n,n) 的逐格一致性
    （scipy 精确法与 R wilcox.test(exact=TRUE) 在无结数据上同分布）

依赖：Python 标准库 + numpy（组合数）+ scipy（精确 Mann-Whitney）。
合成算例：不含任何真实样本数据。
"""
import argparse
import math
import sys

import numpy as np
from scipy import stats
from scipy.special import comb


def min_p_table(n_max):
    """每组 n = 2..n_max：理论地板（1/C、2/C）与 scipy 精确法逐格对照。"""
    rows = []
    for n in range(2, n_max + 1):
        x = np.arange(1, n + 1, dtype=float)
        y = np.arange(n + 1, 2 * n + 1, dtype=float)   # 完全分离：max(x) < min(y)
        n_perm = comb(2 * n, n)
        p_one_theory = 1.0 / n_perm
        p_two_theory = 2.0 / n_perm
        p_two_scipy = stats.mannwhitneyu(
            x, y, alternative="two-sided", method="exact").pvalue
        p_one_scipy = stats.mannwhitneyu(
            x, y, alternative="less", method="exact").pvalue
        rows.append(dict(n=n, perm=n_perm, p1=p_one_theory, p2=p_two_theory,
                         p2s=p_two_scipy, p1s=p_one_scipy))
    return rows


def main():
    ap = argparse.ArgumentParser(
        description="小样本 Wilcoxon/Mann-Whitney 的显著性地板（合成算例，组合计数；"
                    "服务第 12 章失效条件 3 与讲义 l0_06 §1/演示 1b）")
    ap.add_argument("--n-max", type=int, default=6,
                    help="每组样本量扫描上限（默认 6）")
    ap.add_argument("--seed", type=int, default=20261104,
                    help="保留参数（本脚本无随机数）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    print("=" * 78)
    print("[合成算例] 两组完全分离（max(组1) < min(组2)）时 Wilcoxon/Mann-Whitney")
    print("           精确检验的最小可达 p 值 = f(C(2n,n))，与效应大小无关")
    print("=" * 78)
    rows = min_p_table(args.n_max)
    print(f"{'每组 n':>7} {'C(2n,n)':>10} {'单侧=1/C':>12} {'双侧=2/C':>12} "
          f"{'scipy 双侧':>12} {'双侧<0.05?':>11}")
    for r in rows:
        print(f"{r['n']:>7} {int(r['perm']):>10} {r['p1']:>12.6f} {r['p2']:>12.6f} "
              f"{r['p2s']:>12.6f} {'可行' if r['p2'] < 0.05 else '不可能':>11}")

    print()
    print("[口径说明] 双侧 = 2 × 单侧（两侧各一种最极端排列，无结数据下与 R")
    print("           wilcox.test / scipy exact 一致）。讲义失效条件 3 的「最小 p = 0.1」")
    print("           指双侧；若事先声明单侧假设，n=3 的地板是 0.05，仍无法 < 0.05。")

    print()
    print("[算例] 效应大到离谱也压不过地板：组1 = [1, 2, 3]，组2 = [100, 200, 300]")
    x = np.array([1.0, 2.0, 3.0]); y = np.array([100.0, 200.0, 300.0])
    p_big = stats.mannwhitneyu(x, y, alternative="two-sided", method="exact").pvalue
    mean_gap = y.mean() - x.mean()
    print(f"  组间均值差 = {mean_gap:.0f}（两组取值完全不重叠），"
          f"双侧 p 仍 = {p_big:.1f} —— 统计量的离散度由 C(6,3)=20 种排列锁死")
    print("  → 报「p = 0.1 无显著差异」是在报告实验设计缺陷，不是生物学结论")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        r3 = next(r for r in rows if r["n"] == 3)
        r4 = next(r for r in rows if r["n"] == 4)
        check("n=3：C(6,3) = 20，双侧最小 p 恰 = 0.10（讲义失效条件 3 口径）",
              r3["perm"] == 20 and abs(r3["p2"] - 0.10) < 1e-12)
        check("n=3：单侧最小 p = 0.05，双侧 2× 单侧",
              abs(r3["p1"] - 0.05) < 1e-12 and abs(r3["p2"] - 2 * r3["p1"]) < 1e-12)
        check("n=4：双侧最小 p = 2/C(8,4) = 0.02857 < 0.05（讲义演示 1b 口径）",
              abs(r4["p2"] - 0.02857142857142857) < 1e-9 and r4["p2"] < 0.05)
        check("scipy 精确法与理论地板逐格一致（|Δ| < 1e-9）",
              all(abs(r["p2s"] - r["p2"]) < 1e-9 and abs(r["p1s"] - r["p1"]) < 1e-9
                  for r in rows))
        check("n=5 起双侧才可能 < 0.01；n=2、3 永远不可能 < 0.05",
              rows[0]["p2"] > 0.05 and rows[1]["p2"] > 0.05
              and rows[3]["p2"] < 0.01)
        check("效应算例：组间均值差 198 时双侧 p 仍 = 0.10",
              abs(p_big - 0.10) < 1e-12)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

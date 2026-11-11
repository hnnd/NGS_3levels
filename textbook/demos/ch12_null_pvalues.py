#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch12_null_pvalues.py — 多重假设检验的假阳性累积与 BH/Bonferroni 校正（合成算例）

服务章节：第 12 章 §12.4 概念与方法（多重检验与 FDR）、§12.5 失效条件第 2 条
（2 万次检验按原始 p<0.05 筛选必然产生大批假阳性）。源讲义：l0_06_stats §3 与
⑤ 演示 3（全部无差异时有多少个 p < 0.05）、演示 4（有真信号时 none/Bonferroni/BH
的取舍）。DESeq2/edgeR 的具体模型属第 14 章，本脚本只做教科书层面的 t 检验模拟。

Part 1（零假设全成立，对齐讲义演示 3）：
  m = 20000 个「基因」，两组各 3 个样本，全部从同一 N(0,1) 抽取 —— 真差异严格为 0。
  手算规则：E(假阳性) = m × α = 20000 × 0.05 = 1000（期望，非整数承诺）；
  且 H0 为真时 p 值服从均匀分布 U(0,1)，KS 检验验证之。
  numpy 同结构实现（种子 42）与讲义 R 实现（set.seed(42)）的实现值不同属正常
  （不同 RNG），但都应落在 1000 附近；讲义印刷值 985 是 R 实现值，
  已在 ta 用 Rscript 实跑复核（见 cases/ch12/case.md §③）。

Part 2（200 个基因有真差异，对齐讲义演示 4）：
  前 200 个基因处理组均值提升 δ ~ U(1.0, 3.5)，其余 18000 个无差异；
  每组 n = 10。BH 阈值准则：p 值升序排秩 p_(k) ≤ (k/m)·q 的最大切点 k。
  本脚本按 R p.adjust 语义实现 BH（cummin 单调化）与 Bonferroni（p×m 截断 1），
  讲义印刷值（1169/186/983/0.841；53/53/0；144/135/9/0.062）同为 R 实现值，
  结构断言（假阳性占比量级、Bonferroni 零假阳性、BH 找回更多真阳性）不锚定 RNG。

参数（--help 可见）：
  --m / --n-null    Part 1 基因数与每组样本量（默认 20000 / 3，对齐演示 3）
  --n-true / --n-each  Part 2 真差异基因数与每组样本量（默认 200 / 10，对齐演示 4）
  --alpha / --q     显著性水准与 BH 的 q（默认 0.05）
  --seed-null / --seed-signal  两部分各自的固定种子（默认 42 / 7，对齐讲义）

正文引用的输出：
  - Part 1：原始 p<0.05 计数（≈1000 期望；985 为讲义 R 实现值）、BH/Bonferroni 后
    均 0 个、p 值直方图的均匀性（KS p）、min(p) 量级；E = m×α 手算规则
  - Part 2：none/Bonferroni/BH 三列「报告数 / 真阳性 / 假阳性 / 假阳性占比」，
    BH 阈值切点示例；BH 假阳性占比 ≈ q 量级（讲义 0.062 vs 承诺 0.05）

依赖：Python 标准库 + numpy + scipy（仅 t 分布 CDF 与 KS 检验）。
合成算例：所有「基因表达」均为正态随机数，与任何真实样本无关。
"""
import argparse
import sys

import numpy as np
from scipy import stats

SEED_NULL = 42      # 对齐讲义演示 3 的 set.seed(42)
SEED_SIGNAL = 7     # 对齐讲义演示 4 的 set.seed(7)


def ttest_p(X, Y):
    """等方差两样本 t 检验（双侧）p 值，向量化；与 scipy.stats.ttest_ind
    (equal_var=True) 逐位一致（selftest 断言），与 R t.test(var.equal=TRUE) 同公式。"""
    n1, n2 = X.shape[1], Y.shape[1]
    df = n1 + n2 - 2
    sp2 = ((n1 - 1) * X.var(axis=1, ddof=1) + (n2 - 1) * Y.var(axis=1, ddof=1)) / df
    t = (X.mean(axis=1) - Y.mean(axis=1)) / np.sqrt(sp2 * (1.0 / n1 + 1.0 / n2))
    return 2.0 * stats.t.cdf(-np.abs(t), df)


def p_adjust_bh(p):
    """R p.adjust(method='BH') 语义：q_(i) = min_{j>=i} p_(j)·m/j（升序侧 cummin）。"""
    m = len(p)
    o = np.argsort(p)
    ps = p[o]
    q = ps * m / np.arange(1, m + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(m)
    out[o] = np.minimum(q, 1.0)
    return out


def p_adjust_bonferroni(p):
    return np.minimum(p * len(p), 1.0)


def count_sig(p, thresh):
    return int((p < thresh).sum())


def main():
    ap = argparse.ArgumentParser(
        description="多重检验假阳性累积与 BH/Bonferroni（合成算例；服务第 12 章"
                    "失效条件 2，对齐讲义 l0_06 演示 3/4）")
    ap.add_argument("--m", type=int, default=20000, help="检验总数（演示 3 基因数）")
    ap.add_argument("--n-null", type=int, default=3, help="Part 1 每组样本量")
    ap.add_argument("--n-true", type=int, default=200, help="Part 2 真差异基因数")
    ap.add_argument("--n-each", type=int, default=10, help="Part 2 每组样本量")
    ap.add_argument("--alpha", type=float, default=0.05, help="显著性水准")
    ap.add_argument("--q", type=float, default=0.05, help="BH 的 FDR 水准 q")
    ap.add_argument("--seed-null", type=int, default=SEED_NULL)
    ap.add_argument("--seed-signal", type=int, default=SEED_SIGNAL)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    # ---------------- Part 1：零假设全成立 ----------------
    print("=" * 78)
    print(f"[Part 1 · 合成算例 · 对齐讲义演示 3] {args.m} 个「基因」、两组各 "
          f"{args.n_null} 个样本，全部同分布 N(0,1) —— 真差异严格为 0"
          f"（seed={args.seed_null}）")
    print("=" * 78)
    rng = np.random.default_rng(args.seed_null)
    ctrl = rng.standard_normal((args.m, args.n_null))
    trt = rng.standard_normal((args.m, args.n_null))
    pv = ttest_p(ctrl, trt)

    n_raw = count_sig(pv, args.alpha)
    n_bh = count_sig(p_adjust_bh(pv), args.alpha)
    n_bonf = count_sig(p_adjust_bonferroni(pv), args.alpha)
    ks = stats.kstest(pv, "uniform")
    print(f"手算规则：E(假阳性) = m × α = {args.m} × {args.alpha} = "
          f"{args.m * args.alpha:.0f}（期望，非整数承诺）")
    print(f"原始 p < {args.alpha}            ：{n_raw} 个「显著基因」—— 全部是假阳性")
    print(f"BH 校正后 < {args.alpha}         ：{n_bh} 个")
    print(f"Bonferroni 校正后 < {args.alpha} ：{n_bonf} 个"
          f"（阈值 p < {args.alpha}/{args.m} = {args.alpha / args.m:.2e}）")
    print(f"p 值均匀性 KS 检验：stat = {ks.statistic:.4f}, p = {ks.pvalue:.3g}"
          f"（H0 为真时 p ~ U(0,1)，直方图应平坦；不拒绝均匀性 = 与理论一致）")
    print(f"min(p) = {pv.min():.3g} —— 最「显著」的那个也是纯噪声"
          f"（{args.m} 次检验里最极端者的理论量级 1/m ≈ {1 / args.m:.3g}）")
    print("讲义 R 实现值（set.seed(42)，ta 2026-11-04 Rscript 实跑复核）："
          "原始 985、BH 0、Bonferroni 0、min 8.5e-06 —— 与本 numpy 实现"
          "（同分布不同 RNG）结构一致")

    # ---------------- Part 2：200 个基因有真差异 ----------------
    print()
    print("=" * 78)
    print(f"[Part 2 · 合成算例 · 对齐讲义演示 4] {args.n_true} 个基因有真差异"
          f"（δ ~ U(1.0, 3.5)），其余 {args.m - args.n_true} 个无差异；"
          f"每组 {args.n_each} 个样本（seed={args.seed_signal}）")
    print("=" * 78)
    rng2 = np.random.default_rng(args.seed_signal)
    delta = np.concatenate([rng2.uniform(1.0, 3.5, args.n_true),
                            np.zeros(args.m - args.n_true)])
    c2 = rng2.standard_normal((args.m, args.n_each))
    t2 = rng2.standard_normal((args.m, args.n_each)) + delta[:, None]
    p2 = ttest_p(c2, t2)
    is_true = np.zeros(args.m, dtype=bool)
    is_true[:args.n_true] = True

    print(f"{'校正方法':<12} {'报告数':>7} {'真阳性':>7} {'假阳性':>7} {'假阳性占比':>9}")
    results = {}
    for name, padj in [("none（原始）", p2),
                       ("bonferroni", p_adjust_bonferroni(p2)),
                       ("BH", p_adjust_bh(p2))]:
        hit = padj < args.alpha
        n_hit = int(hit.sum())
        tp = int((hit & is_true).sum())
        fp = int((hit & ~is_true).sum())
        fpr = fp / n_hit if n_hit else 0.0
        results[name.split("（")[0]] = (n_hit, tp, fp, fpr)
        print(f"{name:<12} {n_hit:>7} {tp:>7} {fp:>7} {fpr:>9.3f}")
    print("讲义 R 实现值（set.seed(7)，ta 实跑复核）：none 1169/186/983/0.841；"
          "bonferroni 53/53/0/0.000；BH 144/135/9/0.062")
    print(f"读法：none 的列表约八成是垃圾；Bonferroni 零假阳性但漏掉大半真基因；"
          f"BH 本次名单的假阳性占比（FDP）{results['BH'][3]:.3f}（讲义 R 实现值 0.062）"
          f"——单次 FDP 可以高于或低于 q={args.q}，BH 控制的是它的期望（FDR），"
          "不是每一份名单的保证")

    # BH 阈值切点演示（讲义 BH 准则：p_(k) ≤ (k/m)·q 的最大 k）
    o = np.argsort(p2)
    ks_rank = np.arange(1, args.m + 1)
    cut = p2[o] <= ks_rank / args.m * args.q
    kmax = int(ks_rank[cut].max()) if cut.any() else 0
    print(f"BH 阈值切点：满足 p_(k) ≤ (k/m)·q 的最大 k = {kmax}"
          f"（p_({kmax}) = {p2[o][kmax - 1]:.4g} ≤ "
          f"{kmax}/{args.m}×{args.q} = {kmax / args.m * args.q:.4g}）")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        exp_fp = args.m * args.alpha
        check(f"Part 1：原始 p<{args.alpha} 计数 {n_raw} 落在期望 {exp_fp:.0f} "
              f"的蒙特卡洛区间内（±15%）",
              abs(n_raw - exp_fp) <= 0.15 * exp_fp)
        check(f"Part 1：BH 与 Bonferroni 后均为 0 个显著（{n_bh}, {n_bonf}）",
              n_bh == 0 and n_bonf == 0)
        check("Part 1：p 值通过均匀性 KS 检验（p > 0.01，与 U(0,1) 一致）",
              ks.pvalue > 0.01)
        check("Part 1：min(p) 处于 1/m 量级（1e-7 与 1e-3 之间）",
              1e-7 < pv.min() < 1e-3)
        check("Part 2：不校正列表假阳性占比 > 50%",
              results["none"][3] > 0.5)
        check("Part 2：Bonferroni 假阳性 = 0",
              results["bonferroni"][2] == 0)
        check("Part 2：Bonferroni 找回的真阳性显著少于 none（保守代价）",
              results["bonferroni"][1] < results["none"][1])
        check("Part 2：BH 找回的真阳性多于 Bonferroni、假阳性占比在 q 的 "
              "2 倍以内（讲义 0.062 vs q=0.05）",
              results["BH"][1] > results["bonferroni"][1]
              and results["BH"][3] <= 2 * args.q)
        check("Part 2：BH 阈值切点 k 的报告数 = k（升序 cummin 单调化后 "
              "恰为切点数）",
              kmax == results["BH"][0])
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

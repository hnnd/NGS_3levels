#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch14_ora_background.py — ORA 背景基因集用错：全基因组 vs 本次被检验基因（合成算例）

服务章节：第 14 章 §14.4 概念与方法（功能富集）、§14.5 失效条件第 3 条
「富集分析背景基因集用错使结论全错」。源讲义：m04 ⑨-E7、§4.5、⑥6.4。
机制（讲义 ⑨-E7）：enrichGO 不传 universe 时以 OrgDb 全部注释基因为背景
（clusterProfiler 默认行为，CH14_EXPERT_001 文⑤实查 enrichGO.R 源码确认），
但实验实际只检验了其中一部分（低表达/组织特异基因未进入检验）。背景分母虚高、
且未检验基因 disproportionately 落在通路外 → BgRatio 被低估 → p 值系统性偏小
→ 假阳性通路。讲义设例口径：注释 3 万余 vs 实际检验 1.5 万（设例数，正文引用须标设例）。

模型（合成，非 PRJDB36269 或任何真实样本）：
  * 注释基因 N_annot = 30000；通路内基因被「检验」（表达且通过预过滤）的概率为 1.0、
    通路外为 0.5——模拟「未检验基因 disproportionately 在通路外」这一真实数据的
    结构性事实（通路成员只占基因组的少数：200 通路 × 40 成员，覆盖率 ≈ 23%）；
  * 200 个合成通路，各 40 个成员；差异基因列表 1500 个，全部随机抽自**被检验基因**
    （纯零假设：没有任何通路真正富集）；
  * ORA：对每个通路做超几何检验 P(X ≥ k)，背景分别取
      正确 = 有资格入选名单的基因（padj 非 NA 且映射到注释；本合成即被检验基因）
      错误 = 全部注释基因（enrichGO 不传 universe 的默认行为）
    各自做 BH 校正，数显著 term。

参数（--help 可见）：
  --n-annot / --n-pathway / --pathway-size / --n-de   合成规模（默认 30000/200/40/3000）
  --p-test-in / --p-test-out   通路内/外基因被检验的概率（默认 1.0 / 0.5）
  --seed               随机种子（默认 20260829，对齐 m04 脚本 set.seed(20260829) 的结构）

正文引用的输出：
  - Part 0 手算规则：超几何检验 P(X≥k) = 1 − Σ_{i<k} C(K,i)C(N−K,n−i)/C(N,n)，
    手算例 N=10、K=4、n=3、k=2 → [C(4,2)C(6,1)+C(4,3)]/C(10,3) = 40/120 = 1/3
  - Part 1：纯零假设下（差异列表随机、无真富集），正确背景 vs 错误背景的
    显著 term 数（BH 0.05）、p 值中位数比与「边缘推进」计数（raw p 从 >0.05
    被压到 <0.05 的 term 数）——错误背景使每个 term 的 p 系统性偏小，
    把边缘 term 推进显著区（排序本身不变：p 是命中数 k 的单调函数）

依赖：Python 标准库 + numpy + scipy。
合成算例：所有「基因/通路 membership」均为随机数生成器产物，与任何真实样本无关。
"""
import argparse
import sys
from math import comb

import numpy as np
from scipy import stats

SEED = 20260829  # 对齐 m04 脚本 set.seed(20260829)（结构对齐；RNG 不同）


def hypergeom_sf(k, N, K, n):
    """P(X ≥ k)，X ~ Hypergeometric(总体 N、成功态 K、抽 n 个)。手算实现，与 scipy 对照。"""
    denom = comb(N, n)
    return sum(comb(K, i) * comb(N - K, n - i) for i in range(k, min(K, n) + 1)) / denom


def bh_adjust(pvals):
    """Benjamini-Hochberg 校正（讲义公式在第 12 章；此处为复现入口）。"""
    p = np.asarray(pvals, dtype=float)
    m = p.size
    order = np.argsort(p)
    ranked = p[order] * m / (np.arange(m) + 1)
    # 单调化：从后往前 cummin
    adj_sorted = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(m)
    out[order] = np.clip(adj_sorted, 0, 1)
    return out


def main():
    ap = argparse.ArgumentParser(
        description="ORA 背景基因集用错的全基因组 vs 被检验基因对照（合成算例；服务"
                    "第 14 章失效条件 3，对齐讲义 m04 ⑨-E7）")
    ap.add_argument("--n-annot", type=int, default=30000)
    ap.add_argument("--n-pathway", type=int, default=200)
    ap.add_argument("--pathway-size", type=int, default=40)
    ap.add_argument("--n-de", type=int, default=3000)
    ap.add_argument("--p-test-in", type=float, default=1.0,
                    help="通路内基因被检验（进入表达矩阵）的概率")
    ap.add_argument("--p-test-out", type=float, default=0.5,
                    help="通路外基因被检验的概率")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    # ---------------- Part 0：手算规则 ----------------
    print("=" * 78)
    print("[Part 0 · 手算规则] 超几何检验与背景集的位置")
    print("=" * 78)
    p_hand = (comb(4, 2) * comb(6, 1) + comb(4, 3) * comb(6, 0)) / comb(10, 3)
    p_scipy = float(stats.hypergeom.sf(1, 10, 4, 3))
    print("  手算例：N=10 个基因、通路 K=4 个、差异列表 n=3 个、其中命中 k=2 个")
    print(f"    P(X≥2) = [C(4,2)·C(6,1) + C(4,3)·C(6,0)] / C(10,3) = {p_hand:.4f}")
    print(f"    scipy 对照 = {p_scipy:.4f}（一致：{abs(p_hand - p_scipy) < 1e-12}）")
    print("  背景集 N 与 K 同时在分子里换：把 N 换大、K 按真实 membership 不动，")
    print("  零假设下的期望命中 E[X] = n·K/N 被改变——同一个 k 在新的零假设下")
    print("  「看起来更极端」，p 值因此整体漂移。")

    # ---------------- 合成数据 ----------------
    rng = np.random.default_rng(args.seed)
    N = args.n_annot
    # 通路 membership：random 抽取，通路间允许重叠（真实 GO 即如此）
    pathways = [rng.choice(N, size=args.pathway_size, replace=False)
                for _ in range(args.n_pathway)]
    in_any = np.zeros(N, dtype=bool)
    for pw in pathways:
        in_any[pw] = True
    # 检验事件：通路内基因更可能被检验（结构性事实的模拟）
    p_test = np.where(in_any, args.p_test_in, args.p_test_out)
    tested = rng.random(N) < p_test
    n_tested = int(tested.sum())
    k_annot = int(in_any.sum())
    k_tested = int((in_any & tested).sum())
    print()
    print(f"[合成世界] 注释基因 {N}（通路相关 {k_annot}）；被检验 {n_tested}"
          f"（通路相关 {k_tested}）")
    print(f"  BgRatio 正确口径 = {k_tested}/{n_tested} = {k_tested/n_tested:.4f}；"
          f"错误口径 = {k_annot}/{N} = {k_annot/N:.4f}")
    # 差异列表：纯零假设——从被检验基因里均匀抽 n_de 个（无真富集）
    de = rng.choice(np.where(tested)[0], size=args.n_de, replace=False)

    # ---------------- Part 1：同一列表、两种背景 ----------------
    print()
    print("=" * 78)
    print(f"[Part 1 · 合成算例] {args.n_pathway} 个通路 × {args.pathway_size} 成员；"
          f"差异列表 {args.n_de} 个（纯零假设）；seed={args.seed}")
    print("=" * 78)
    p_correct = np.empty(args.n_pathway)
    p_wrong = np.empty(args.n_pathway)
    for j, pw in enumerate(pathways):
        k_hit = int(np.isin(de, pw).sum())
        # 正确背景：universe = 被检验基因；通路在被检验集内的成员数
        K_c = int(tested[pw].sum())
        p_correct[j] = stats.hypergeom.sf(k_hit - 1, n_tested, K_c, args.n_de)
        # 错误背景：universe = 全部注释基因；通路全部成员
        p_wrong[j] = stats.hypergeom.sf(k_hit - 1, N, args.pathway_size, args.n_de)
    adj_correct = bh_adjust(p_correct)
    adj_wrong = bh_adjust(p_wrong)
    sig_c = int((adj_correct < 0.05).sum())
    sig_w = int((adj_wrong < 0.05).sum())
    ratio = p_wrong / p_correct
    pushed = int(((p_correct >= 0.05) & (p_wrong < 0.05)).sum())
    only_wrong_sig = int(((adj_correct >= 0.05) & (adj_wrong < 0.05)).sum())
    print(f"{'':>22}{'正确背景（被检验基因）':>24}{'错误背景（全基因组）':>22}")
    print(f"{'显著 term 数 (BH<0.05)':>22}{sig_c:>24d}{sig_w:>22d}"
          f"   （真实富集数 = 0）")
    print(f"{'p 值中位数':>22}{np.median(p_correct):>24.3f}{np.median(p_wrong):>22.3f}")
    print(f"{'median(p错误/p正确)':>22}{np.median(ratio):>24.3f}")
    print(f"  p错误 < p正确的 term：{(ratio < 1).sum()} 个；"
          f"反向：{(ratio > 1).sum()} 个")
    print(f"  「边缘推进」（raw p 从 ≥0.05 被压到 <0.05 的 term）：{pushed} 个；"
          f"仅错误背景过 BH 线的 term：{only_wrong_sig} 个")
    print("读法：差异列表是随机的，正确背景下显著数 ≈ 0（校准）；错误背景让每个")
    print("      term 的 p 系统性偏小、把边缘 term 推进显著区——排序本身不变")
    print("      （p 是命中数 k 的单调函数），变的是「谁过线」。真实数据里注释集远")
    print("      大于检验集（讲义设例：3 万余 vs 1.5 万），同一偏移放大成讲义 ⑥6.4")
    print("      说的「富集出一堆 term」；正确背景 = 与名单同一选择规则下有资格入选的基因")
    print("      （按 padj 筛名单时：padj 非 NA 且映射到注释），而非 rownames(res)；写进方法学。")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        check(f"手算规则与 scipy 一致（|{p_hand:.4f} − {p_scipy:.4f}| < 1e-12）",
              abs(p_hand - p_scipy) < 1e-12)
        check("手算 hypergeom_sf 与 scipy 在合成数据上逐点一致（最大差 < 1e-10）",
              max(abs(hypergeom_sf(int(np.isin(de, pw).sum()), n_tested,
                                   int(tested[pw].sum()), args.n_de) - pc)
                  for pw, pc in zip(pathways[:20], p_correct[:20])) < 1e-10)
        check(f"正确背景校准：显著 term 数 {sig_c} ≤ 15（200 个检验、零假设）",
              sig_c <= 15)
        check(f"错误背景制造假阳性：显著 term 数 {sig_w} ≥ 2 且 > 正确背景（{sig_c}）",
              sig_w >= 2 and sig_w > sig_c)
        check(f"边缘推进：raw p 从 ≥0.05 被压到 <0.05 的 term 有 {pushed} 个 ≥ 10",
              pushed >= 10)
        check(f"方向系统性：median(p错误/p正确) = {np.median(ratio):.3f} < 0.9，"
              f"且 p错误<p正确 的 term 占 {(ratio < 1).mean():.0%} ≥ 80%",
              np.median(ratio) < 0.9 and (ratio < 1).mean() >= 0.8)
        check("差异列表 ⊆ 被检验基因（正确背景口径自洽）", bool(tested[de].all()))
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

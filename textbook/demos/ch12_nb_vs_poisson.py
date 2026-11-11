#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch12_nb_vs_poisson.py — 测序计数的均值-方差关系：泊松（技术重复）vs 负二项（生物学重复）（合成算例）

服务章节：第 12 章 §12.4 概念与方法（测序计数数据与负二项分布）、§12.5 失效条件
第 1 条的正向机制（计数为什么不能直接当正态数据做 t 检验）。源讲义：l0_06_stats §2
与 ⑤ 演示 2。DESeq2/edgeR 的离散度收缩工程细节属第 14 章，本脚本只演示
「方差随均值增长、泊松装不下」的一般道理。

模型（全部为合成模型，非任何真实样本结果）：
  * n_gene = 2000 个「基因」的期望表达 μ ~ 2^U(1, 12)（2 到 4096，对齐演示 2）；
    每个基因 n_rep = 6 个生物学重复。
  * 泊松世界（技术重复的抽样散斑噪声）：Y ~ Pois(μ) ⇒ Var = μ（等离散）。
  * 负二项世界（生物学重复 = 真实浓度 Gamma 变异 ⊗ 泊松抽样）：
    Y ~ NB(size = 1/α, μ)，α = 0.1（对齐演示 2 的 size = 10）⇒ Var = μ + α·μ²。
    低表达区间方差 ≈ 均值（泊松项主导）；高表达区间 α·μ² 项主导 —— 过离散。
  * 分箱中位数表（cut: 0/10/100/1000/1e5，对齐演示 2 的 tapply(cut(...))）。

参数（--help 可见）：
  --n-gene / --n-rep   基因数与每基因重复数（默认 2000 / 6，对齐演示 2）
  --alpha              NB 离散度（默认 0.1，即 R rnbinom 的 size = 10）
  --seed               随机种子（默认 20260829，对齐演示 2 的 set.seed 结构；
                       注意 numpy 与 R 的 RNG 不同，分箱中位数的实现值不同属正常，
                       讲义印刷值 1.3/3.5/26.4/166.3 是 R RNG 的实现值，
                       本脚本锚定结构：泊松 ≈ 1、NB 随表达量单调放大）

正文引用的输出：
  - 闭式表：μ × α 下的 Var_Pois = μ 与 Var_NB = μ + αμ²（手算规则入口，
    如 μ=100、α=0.1：100 vs 1100，差 11 倍）
  - 分箱中位数 var/mean 表：泊松四箱 ≈ 1；NB 1.3 → 3.5 → 26–29 → 166–173（numpy 现跑 172.2；讲义 R 166.3）
    （讲义演示 2 的量化结论：低表达抽样噪声主导、高表达生物学变异主导）
  - 「一个假定方差恒定的 t 检验无法同时处理这两端」的定量注脚

依赖：Python 标准库 + numpy（scipy 不使用）。
合成算例：所有「基因表达计数」均为随机数生成器产物，与任何真实样本无关。
"""
import argparse
import sys

import numpy as np

SEED = 20260829   # 对齐讲义演示 2 的 set.seed(20260829)（结构对齐；RNG 不同）


def binned_median_ratio(mat):
    """按表达量分箱（cut 0/10/100/1000/1e5，对齐演示 2）返回 var/mean 中位数。"""
    m = mat.mean(axis=1)
    v = mat.var(axis=1, ddof=1)
    b = np.digitize(m, [10.0, 100.0, 1000.0])
    out, med_mu = [], []
    for k in range(4):
        sel = b == k
        out.append(float(np.median(v[sel] / m[sel])))
        med_mu.append(float(np.median(m[sel])))
    return out, med_mu


def main():
    ap = argparse.ArgumentParser(
        description="泊松 vs 负二项的均值-方差关系（合成算例；服务第 12 章计数数据"
                    "统计基础，对齐讲义 l0_06 演示 2）")
    ap.add_argument("--n-gene", type=int, default=2000)
    ap.add_argument("--n-rep", type=int, default=6)
    ap.add_argument("--alpha", type=float, default=0.1,
                    help="NB 离散度 α（= 1/size；演示 2 的 size=10 即 α=0.1）")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    # ---------------- Part 0：闭式（手算规则） ----------------
    print("=" * 78)
    print("[Part 0 · 手算规则] Var_Poisson = μ；Var_NB = μ + α·μ²")
    print("=" * 78)
    print(f"{'μ':>8} {'Var_Pois':>10} | {'α=0.05 的 Var_NB':>15} "
          f"{'α=0.1 的 Var_NB':>15} {'α=0.5 的 Var_NB':>15}")
    for mu in (10.0, 100.0, 1000.0):
        cells = "  ".join(
            f"α={a:<5}{mu + a * mu * mu:>9.0f}" for a in (0.05, 0.1, 0.5))
        print(f"{mu:>8.0f} {mu:>10.0f} |  {cells}"
              f"   （NB/Poisson 比 = {1 + 0.1 * mu:.0f} @ α=0.1）")
    print("μ=100、α=0.1：泊松说方差 100，负二项说 1100 —— 差 11 倍；"
          "μ 越大 α·μ² 项占比越大：跨基因的均值—方差关系是 NB 模型可借用的结构"
          "（不是说逐基因 t 检验假定了全基因方差恒定）。")

    # ---------------- Part 1：模拟分箱表 ----------------
    print()
    print("=" * 78)
    print(f"[Part 1 · 合成算例] {args.n_gene} 个「基因」× {args.n_rep} 个生物学重复，"
          f"μ ~ 2^U(1,12)；泊松世界 vs 负二项世界（α={args.alpha}，"
          f"size={1 / args.alpha:g}）（seed={args.seed}）")
    print("=" * 78)
    rng = np.random.default_rng(args.seed)
    mu = 2.0 ** rng.uniform(1.0, 12.0, args.n_gene)
    pois = rng.poisson(mu[:, None], (args.n_gene, args.n_rep))
    nb = rng.negative_binomial(1.0 / args.alpha,
                               (1.0 / args.alpha) / (1.0 / args.alpha + mu[:, None]),
                               (args.n_gene, args.n_rep))

    labels = ["(0,10]", "(10,100]", "(100,1e3]", "(1e3,1e5]"]
    for name, mat in [("泊松（= 技术重复的抽样噪声）", pois),
                      ("负二项（= 生物学重复，α=0.1）", nb)]:
        ratios, med_mu = binned_median_ratio(mat)
        row = "  ".join(f"{labels[i]}: {ratios[i]:>6.1f}" for i in range(4))
        print(f"{name}\n    var/mean 中位数 = {row}")
    print("分箱内 μ 中位数：" +
          "  ".join(f"{labels[i]}: {med_mu[i]:>7.1f}" for i in range(4)) +
          "（负二项理论中线 1+α·μ："
          + "  ".join(f"{1 + args.alpha * med_mu[i]:>6.1f}" for i in range(4))
          + "）")
    print("讲义演示 2 的 R 实现值（set.seed(20260829)）：泊松 ≈1；负二项 "
          "1.3 / 3.5 / 26.4 / 166.3 —— 本 numpy 实现同分布不同 RNG，"
          "结构（泊松贴 1、负二项随表达量放大）一致。")
    print("→ 低表达箱 var/mean 约 1.3（接近泊松），高表达箱随表达量放大到上表最后一列的量级"
          "（本次现跑值见上；R 实现为 166.3）：跨基因的均值—方差关系是 NB 模型可借用的结构，"
          "不是说逐基因 t 检验假定了全基因方差恒定。")

    # ---------------- Part 2：单个基因的重复间波动 ----------------
    print()
    print("[Part 2 · 同一基因在 6 个生物学重复里的样子（合成算例）]")
    rng2 = np.random.default_rng(args.seed + 1)
    for mu0 in (20.0, 500.0):
        y = rng2.negative_binomial(1.0 / args.alpha,
                                   (1.0 / args.alpha) / (1.0 / args.alpha + mu0),
                                   args.n_rep)
        print(f"  μ={mu0:>5.0f}：重复计数 = {np.array2string(y, separator=', ')}"
              f"；样本方差/均值 = {y.var(ddof=1) / y.mean():.2f}"
              f"（泊松期望 ≈1，NB 理论 = {1 + args.alpha * mu0:.1f}）")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        check("手算规则：μ=100、α=0.1 时 Var_NB = 100 + 0.1×100² = 1100",
              abs(100.0 + 0.1 * 100.0 ** 2 - 1100.0) < 1e-9)
        pr, _ = binned_median_ratio(pois)
        nr, med_mu2 = binned_median_ratio(nb)
        check(f"泊松世界四箱 var/mean 都贴 1（最大 {max(pr):.2f} < 1.2）",
              max(pr) < 1.2)
        check("负二项世界四箱 var/mean 随表达量严格递增"
              f"（{[round(r, 1) for r in nr]}）",
              all(a < b for a, b in zip(nr, nr[1:])))
        check("负二项高表达箱 var/mean > 100（生物学变异 α·μ² 主导）",
              nr[3] > 100)
        check("负二项低表达箱 var/mean < 2（泊松抽样噪声主导）",
              nr[0] < 2)
        check("负二项各箱与理论中线 1+α·μ 同量级（比值 0.3–3）",
              all(0.3 <= nr[i] / (1 + args.alpha * med_mu2[i]) <= 3.0
                  for i in range(4)))
        check("NB 高表达箱方差放大倍数 > 泊松高表达箱 50 倍以上",
              nr[3] / max(pr[3], 1e-9) > 50)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

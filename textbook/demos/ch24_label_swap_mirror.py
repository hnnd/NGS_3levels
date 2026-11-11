#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch24_label_swap_mirror.py — 「换标签镜像」检验与方向反转指纹（合成算例）

服务于：教材第 24 章（AI 辅助生信分析的验证）§24.4 概念与方法
（三步验证法第 ② 步：已知答案的回归测试；contrast/factor 参考水平
写反是五类高频错误之 2）、§24.5 失效条件第 4 条（没有已知答案就无法
判断对错），对应讲义 p01 ④-4.3 表第 ② 行（cor(lfc_原, lfc_换) 理论值
应 ≈ -1）、④-4.7 第二条设计规则（扰动与错误模式成数学对偶）、⑥-6.1②
（换标签重跑后相关系数 = -1.000）、⑥-6.2 指纹表第 2 行（spike-in 全部
落在下调侧 0/20、与参考流程相关性 ≈ −0.99）、⑩-3 习题答案（那个数字
应该等于 −1），以及 03_code/phd/scripts/01_verify_de.R 第 ② 段的两个
数字（换标签相关 -1.000、上调侧命中 0/20）。

合成设定（不基于任何真实样本；复刻 01_make_spikein_counts.R 的生成器
设计，但用 numpy 种子独立抽样）：
  2 000 基因 × 6 样本（ctrl/treat 各 3），基线 2^N(5.5, 2.2)，
  文库因子 {1.00, 0.62, 1.45, 0.81, 1.30, 0.95}（max/min = 2.34），
  20 个 spike-in 基因在处理组上调 2^3 = 8 倍，负二项噪声 size = 1/0.15。
  效应量估计用「两组 log2-CPM 均值之差」的对称估计量——换标签后每个
  基因的估计值严格取负，相关性恒等于 -1（与估计量的噪声无关）。

正文引用的输出（手算可对）：
  - 换标签后 log2FC 向量与原始的皮尔逊相关 = -1.000（合成口径下严格
    -1；课程数据 README p01 节实测 verify 脚本报 -1.000，AI 版 vs
    参考流程 -0.990——后者含双重归一化与模型差异，仍指向方向反转）；
  - 方向写反时 20/20 个 spike-in 全部落在下调侧（上调侧命中 0/20，
    与 README p01 节实测一致）；
  - 朴素比值估计量的收缩形态：低表达基因的原始 log2FC 可以被噪声
    推到 |log2FC| ≫ 3，一个正态先验 τ=0.5 的后验均值把高表达
    spike-in 收缩到 ≈ +3 以下一点、把低表达基因压向 0——「真值 +3，
    收缩后略小」（verify_de.R 实测中位数 2.79）的机制演示。

参数：
  --n-gene    基因数（默认 2000）
  --n-spike   spike-in 基因数（默认 20）
  --true-lfc  spike-in 真实 log2 倍数（默认 3，即 8 倍）
  --seed      随机种子（默认 20261105）

合成数据不得写成真实样本结果。只用 Python 标准库 + numpy；< 1 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch24_label_swap_mirror.py --selftest
"""
import argparse

import numpy as np

LIB_FACTOR = np.array([1.00, 0.62, 1.45, 0.81, 1.30, 0.95])  # 与生成器 R 脚本同款
N_EACH = 3                                                    # 每组生物学重复
DISP = 0.15                                                   # 负二项离散度（合成参数）


def make_counts(n_gene: int, n_spike: int, true_lfc: float, seed: int):
    """合成已知答案计数矩阵：返回 (counts, spike_idx)。生成器设计复刻
    01_make_spikein_counts.R（基线对数正态、文库因子、NB 噪声），抽样独立。"""
    rng = np.random.default_rng(seed)
    base_mu = 2.0 ** rng.normal(5.5, 2.2, n_gene)
    candidates = np.flatnonzero(base_mu > 30)          # 只在中高表达基因里做 spike-in
    spike_idx = np.sort(candidates[:n_spike])          # 确定性选取（种子固定）
    mu = np.repeat(base_mu[:, None], 6, axis=1) * LIB_FACTOR[None, :]
    mu[spike_idx, 3:6] *= 2.0 ** true_lfc              # 处理组 T1–T3 上调
    n = 1.0 / DISP
    p = n / (n + mu)
    counts = rng.negative_binomial(n, p)               # 与 R rnbinom(size=1/disp) 同族
    return counts, spike_idx


def lfc_estimate(counts: np.ndarray) -> np.ndarray:
    """每基因 log2FC 的对称估计量：treat 组均值(CPM 对数) − ctrl 组均值。
    对称 ⇒ 交换组标签后每个值严格取负（镜像检验的数学基础）。"""
    lib = counts.sum(axis=0)
    log_cpm = np.log2(counts / lib[None, :] * 1e6 + 0.5)
    return log_cpm[:, 3:6].mean(axis=1) - log_cpm[:, 0:3].mean(axis=1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n-gene", type=int, default=2000)
    ap.add_argument("--n-spike", type=int, default=20)
    ap.add_argument("--true-lfc", type=float, default=3.0)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    counts, spike_idx = make_counts(args.n_gene, args.n_spike, args.true_lfc, args.seed)

    print("合成算例（不基于任何真实样本）：2 000 基因 × 6 样本，20 个 spike-in"
          " 上调 8 倍（log2FC=3），生成器设计复刻 01_make_spikein_counts.R")
    print()

    lfc = lfc_estimate(counts)
    lfc_swapped = -lfc                                   # 换标签 = 严格取负
    r_swap = float(np.corrcoef(lfc, lfc_swapped)[0, 1])

    print("部分 A 换标签镜像（讲义 ④-4.3② / ⑥-6.1② / ⑩-3 习题答案）：")
    print(f"  cor(log2FC_原, log2FC_换标签) = {r_swap:.3f}  （期望 ≈ -1；")
    print("   对称估计量下恒为 -1，与噪声大小、基因数无关）")
    print(f"  spike-in 原始 log2FC 中位数 = {np.median(lfc[spike_idx]):.2f}"
          f"（真值 +{args.true_lfc:.1f}，朴素估计量无偏但逐基因有噪声）")
    print()

    up_hits = int((lfc[spike_idx] > 0).sum())
    up_hits_flipped = int(((-lfc)[spike_idx] > 0).sum())   # 方向写反 = 符号翻转
    r_vs_ref = float(np.corrcoef(lfc, lfc_swapped)[0, 1])
    print("部分 B 方向反转指纹（讲义 ⑥-6.2 第 2 行 / verify_de.R ② 段）：")
    print(f"  正确方向：spike-in 上调侧命中 {up_hits}/{args.n_spike}")
    print(f"  方向写反：spike-in 上调侧命中 {up_hits_flipped}/{args.n_spike}"
          " ← 若为 0，比较方向反了（0/20）")
    print(f"  错误方向结果 vs 正确方向相关 = {r_vs_ref:.3f}（≈ −0.99 的合成对应；")
    print("   README p01 节实测 AI 版 vs 参考流程 -0.990，机制：contrast 两元素对调）")
    print()

    print("部分 C 「真值 +3，收缩后略小」的机制（讲义 ⑥-6.1②；verify 实测 2.79）：")
    mean_norm = counts.mean(axis=1)
    se = np.sqrt(2.0 / np.maximum(mean_norm, 1.0))       # 低表达 ⇒ 大标准误
    tau = 0.5                                            # log2FC 先验 N(0, τ²)（合成取值）
    lfc_shrunk = lfc * tau ** 2 / (tau ** 2 + se ** 2)
    low = mean_norm < np.median(mean_norm)
    raw_spread = np.median(np.abs(lfc[low]))
    shr_spread = np.median(np.abs(lfc_shrunk[low]))
    print(f"  低表达半区：原始 |log2FC| 中位数 {raw_spread:.2f}"
          f" → 收缩后 {shr_spread:.2f}（噪声项被压向 0）")
    print(f"  spike-in（高表达）：原始中位数 {np.median(lfc[spike_idx]):.2f}"
          f" → 收缩后 {np.median(lfc_shrunk[spike_idx]):.2f}"
          f"（仍 ≈ +{args.true_lfc:.0f}，只是「略小」）")
    print("  注：本部分为 toy 收缩（正态先验、已知方差）的机制演示；")
    print("        DESeq2 的收缩走离散度先验，数值以 verify_de.R 实测 2.79 为准。")

    if args.selftest:
        checks = [
            ("换标签相关 = -1.000（⑩-3 习题答案）", abs(r_swap + 1.0) < 1e-10),
            ("正确方向 spike-in 全部在上调侧（20/20）", up_hits == args.n_spike),
            ("方向写反后上调侧命中 0/20（指纹，README 实测一致）",
             up_hits_flipped == 0),
            ("错误方向与正确方向相关 ≈ -1（-0.99 指纹的合成对应）",
             r_vs_ref < -0.999),
            ("收缩把低表达基因压向 0", shr_spread < raw_spread),
            ("高表达 spike-in 收缩后仍 ≈ +3 且略小于原始值",
             2.0 < np.median(lfc_shrunk[spike_idx]) <= np.median(lfc[spike_idx])),
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

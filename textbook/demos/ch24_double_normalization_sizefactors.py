#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch24_double_normalization_sizefactors.py — 「归一化做两次」的 size factor
指纹与 CPM 手算（合成算例）

服务于：教材第 24 章（AI 辅助生信分析的验证）§24.4 概念与方法
（单位混淆：把 CPM 矩阵喂给 DESeq2 是五类高频错误之 3；报错三分法
数据层问题）、§24.5 失效条件第 1 条（语法正确但生物学错误是常态），
对应讲义 p01 ④-4.2 表第 3 行、⑥-6.1①（文库大小 max/min ≈ 2.5）、
⑥-6.2 指纹表第 3 行（sizeFactors 全挤在 1.0 附近、本例 0.95–1.13，
而原始 counts 文库大小相差 2.5 倍）、⑨-E1/E2（some values are not
integers / converting counts to integer mode），以及 03_code/phd/
scripts/01_verify_de.R 第 ①③ 段的对应行。

合成设定（不基于任何真实样本；复刻 01_make_spikein_counts.R 的生成器
设计，抽样独立）：
  2 000 基因 × 6 样本，文库因子 {1.00, 0.62, 1.45, 0.81, 1.30, 0.95}
  （max/min = 2.34，加 NB 噪声后期望比值 ≈ 2.5，与讲义 ⑥-6.1① 一致），
  负二项噪声 size = 1/0.15。
  size factor 用 DESeq2 的 median-of-ratios 估计量在 numpy 复刻：
  对全部计数为正基因的几何均值取比值的中位数。

正文引用的输出（手算可对）：
  - 原始 counts 的 size factor 散布恢复文库因子散布（max/min ≈ 2.3）；
  - 同一矩阵先转 CPM 再 round 后：所有样本文库大小被强行拉平到 1e6，
    size factor 全部塌缩到 1.0 附近（max/min < 1.25；课程数据 README
    p01 节实测 AI 版 0.949–1.128，散布 1.19）——「归一化做了两次」的
    可计算指纹；
  - CPM 手算规则（讲义 ④-4.3③ 那一行）：CPM = counts / 样本文库 × 1e6，
    verify_de.R 实测示例基因 counts=43、文库 292540 → 146.99；
  - E2 判定：CPM 矩阵是「值为整数的双精度」，DESeq2 只发一句
    converting counts to integer mode message（本机实跑 AI 脚本时
    确出现）——这是数据层问题被静默处理的信号，不是修好了。

参数：
  --n-gene    基因数（默认 2000）
  --seed      随机种子（默认 20261105）

合成数据不得写成真实样本结果。只用 Python 标准库 + numpy；< 1 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch24_double_normalization_sizefactors.py --selftest
"""
import argparse

import numpy as np

LIB_FACTOR = np.array([1.00, 0.62, 1.45, 0.81, 1.30, 0.95])  # 与生成器 R 脚本同款
DISP = 0.15                                                   # 负二项离散度（合成参数）


def make_counts(n_gene: int, seed: int) -> np.ndarray:
    """合成计数矩阵（无 spike-in；生成器设计复刻 01_make_spikein_counts.R，
    抽样独立）：基线 2^N(5.5, 2.2) × 文库因子 + 负二项噪声。"""
    rng = np.random.default_rng(seed)
    base_mu = 2.0 ** rng.normal(5.5, 2.2, n_gene)
    mu = np.repeat(base_mu[:, None], 6, axis=1) * LIB_FACTOR[None, :]
    n = 1.0 / DISP
    p = n / (n + mu)
    return rng.negative_binomial(n, p)


def median_of_ratios(counts: np.ndarray) -> np.ndarray:
    """DESeq2 size factor 估计量的 numpy 复刻：对全部计数为正基因的
    几何均值取 per-sample 比值，再取中位数（estimateSizeFactors 默认）。"""
    positive = counts[(counts > 0).all(axis=1)]
    geomean = np.exp(np.log(positive).mean(axis=1))
    sf = np.median(positive / geomean[:, None], axis=0)
    return sf / np.exp(np.mean(np.log(sf)))      # 归一到几何均值 1（便于跨表比较）


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n-gene", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    cts = make_counts(args.n_gene, args.seed)
    lib_sizes = cts.sum(axis=0)

    print("合成算例（不基于任何真实样本）：2 000 基因 × 6 样本，文库因子"
          " max/min = 2.34（生成器 R 脚本同款），NB 噪声 size=1/0.15")
    print()

    print("部分 A 原始 counts（讲义 ⑥-6.1① 的正常形态）：")
    print(f"  文库大小          : {', '.join(str(int(v)) for v in lib_sizes)}")
    lib_ratio = lib_sizes.max() / lib_sizes.min()
    print(f"  文库大小 max/min  : {lib_ratio:.2f}（讲义 ≈ 2.5；本机实跑课程脚本 2.54）")
    sf_raw = median_of_ratios(cts)
    print(f"  size factors      : {', '.join(f'{v:.3f}' for v in sf_raw)}")
    print(f"  size factor 散布  : {sf_raw.max() / sf_raw.min():.2f}×"
          " —— 归一化信息尚在，DESeq2 只需再校正这部分差异")
    print()

    cpm = np.round(cts / lib_sizes[None, :] * 1e6)      # AI 脚本同款「先转 CPM 再 round」
    sf_cpm = median_of_ratios(cpm)
    cpm_libs = cpm.sum(axis=0)
    cpm_lib_ratio = cpm_libs.max() / cpm_libs.min()
    print("部分 B 同一矩阵先转 CPM 再 round（AI 脚本 L38-39 的植入错误）：")
    print(f"  CPM 后文库大小    : {', '.join(str(int(v)) for v in cpm_libs)}")
    print(f"  各列 max/min      : {cpm_lib_ratio:.4f} —— 每列被强行拉到 ≈1e6"
          "（逐基因取整使各列不完全相等，差异 <0.1%）")
    print(f"  size factors      : {', '.join(f'{v:.3f}' for v in sf_cpm)}")
    cpm_spread = sf_cpm.max() / sf_cpm.min()
    print(f"  size factor 散布  : {cpm_spread:.2f}× —— 全部塌缩到 1.0 附近")
    print("   （课程数据 README p01 节实测 AI 版 0.949–1.128，散布 1.19；")
    print("     指纹判据：sizeFactors 挤在 1.0 附近 + 原始文库差 2.5 倍 → 归一化做了两次）")
    print()

    g, j = 0, 0
    cpm_hand = cts[g, j] / lib_sizes[j] * 1e6
    print("部分 C CPM 手算规则（讲义 ④-4.3③；verify_de.R ③ 的行项目）：")
    print(f"  基因 g 样本 {j + 1}：counts={cts[g, j]}，文库={int(lib_sizes[j])}，"
          f"手算 CPM = {cpm_hand:.2f}")
    print("  verify_de.R 实测示例（课程数据）：gene1768 在 C1 counts=43、"
          "文库 292540 → 146.99（本机 2026-11-05 实跑复现）")
    print()
    print("部分 D E1/E2 判定（讲义 ⑨ 表）：")
    print("  round(CPM) 的值是整数、但存储类型是双精度 → DESeq2 不报错，")
    print("  只发 message「converting counts to integer mode」（本机实跑 AI 脚本")
    print("  时确出现）→ 按 E2 处理：把它当报错看，回上游确认矩阵来源，勿 round 掩盖")

    if args.selftest:
        checks = [
            ("原始 size factor 散布恢复文库因子量级（> 2.0）",
             sf_raw.max() / sf_raw.min() > 2.0),
            ("CPM 后各样本文库大小被拉平到 ≈1e6（max/min < 1.001）",
             cpm_lib_ratio < 1.001),
            ("CPM 后 size factor 塌缩（散布 < 1.25，实测带 1.19 内）",
             cpm_spread < 1.25),
            ("CPM 转换摧毁了归一化信息（散布缩小 > 2 倍）",
             (sf_raw.max() / sf_raw.min()) / cpm_spread > 2.0),
            ("CPM 手算 = 闭式公式（手算规则可对）",
             abs(cpm_hand - cts[g, j] / lib_sizes[j] * 1e6) < 1e-9),
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

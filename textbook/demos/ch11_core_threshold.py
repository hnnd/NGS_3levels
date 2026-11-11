#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch11_core_threshold.py — 「≥95% 核心」在小样本上等于什么 + 注释漏检把真核心
基因判为附属的概率（合成算例，纯标准库）

服务章节：第 11 章 §11.5 失效条件第 2 条（小样本上「95% 核心」与 100% 等价，
应改写为「允许缺失 k 株（≈ x%）」）与 §11.4 核心/附属划分小节。

数据性质：【合成算例】只含算术与伯努利概率，不涉及任何真实菌株；
输出不得写成真实样本（如 Xoo 12 株完成图）的实测结果。

正文引用的输出：
  - k = n − ⌈p·n⌉ 换算表（p=0.95 与 0.99 两档；n=12 时 k=0，n=20 时 k=1）
    → 「允许缺失 k 株（≈ x%）」写法（TERMINOLOGY.md §2 口径 2）
  - 真核心基因在单株注释漏检率 q 下被判为非 100% 核心的概率 1−(1−q)^n
    → 支持「软核心/允许缺失」阈值抗注释噪声的机制说明（m02 讲义 §4.6）
  - 放宽到「允许缺失 k 株」后的误判概率 P[X>k], X~Binomial(n,q)
    → n=12、q=1%：k=0 时 11.4%，放宽到 k=1（≈91.7%）降到 0.62%

参数含义：
  --thresholds  要演示的核心存在比例档（默认 0.95 与 Roary 的 0.99）
  --strains     要演示的基因组数 n 列表（默认含本课贯穿面板的 4、12、57 等）
  --miss-rates  单株注释漏检率 q 列表（合成扫描用，非本课实测值）
  --selftest    断言上述正文引用数字
"""
import argparse
import math
import sys


def k_allowed(n, p):
    """「≥p 比例核心」等价于「允许缺失 k 株」：k = n − ⌈p·n⌉。"""
    return n - math.ceil(p * n)


def p_misjudge(n, q, k):
    """真核心基因（物理上 n 株全有）被判为「缺失 > k 株」的概率。

    每株独立漏检概率 q，漏检株数 X ~ Binomial(n, q)，误判 = X > k。
    k=0 时退化为 1−(1−q)^n。
    """
    # 直接累加二项概率，避免 scipy 依赖（n 很小）
    return sum(math.comb(n, i) * q ** i * (1.0 - q) ** (n - i)
               for i in range(k + 1, n + 1))


def print_threshold_table(strains, thresholds):
    print("=== 表 1：「≥p 核心」↔「允许缺失 k 株（≈ x%）」换算（合成算术）===")
    for p in thresholds:
        pct = int(round(p * 100))
        print(f"-- 阈值 ≥{pct}%（即 Roary Soft-core/Core 档位的常见写法）--")
        print("    n   需存在⌈p·n⌉株   允许缺失 k 株   存在比例下限")
        for n in strains:
            need = math.ceil(p * n)
            k = k_allowed(n, p)
            print(f"  {n:4d}      {need:4d}            {k:4d}          "
                  f"{(n - k) / n * 100:6.1f}%")
        first_k1 = next((n for n in range(1, 201) if k_allowed(n, p) >= 1), None)
        print(f"  >> n<{first_k1} 时 k=0：「≥{pct}% 核心」≡「100% 核心」，"
              f"n={first_k1} 起才允许缺 1 株\n")
    return


def print_miss_table(strains, miss_rates, p_thr):
    print("=== 表 2：注释漏检率 q 下，真核心基因被判出「允许缺失 k 株」之外的概率"
          "（合成伯努利算例）===")
    print("  物理事实：基因在 n 株基因组里全部存在；某株注释时以概率 q 漏检它"
          "（组装 gap、起始密码子错位、最小长度截断等，m02 讲义 §4.6/§⑨-2）")
    for n in strains:
        k = k_allowed(n, p_thr)
        print(f"-- n={n}（「≥{int(round(p_thr * 100))}% 核心」= 允许缺失 {k} 株）--")
        print("    q/株      判非 100%核心  判「缺失>k」   放宽到 k+1 后")
        for q in miss_rates:
            p0 = p_misjudge(n, q, 0)
            pk = p_misjudge(n, q, k)
            pk1 = p_misjudge(n, q, k + 1)
            print(f"  {q * 100:6.2f}%      {p0 * 100:8.2f}%      {pk * 100:8.2f}%"
                  f"      {pk1 * 100:8.2f}%")
        print()
    return


def selftest():
    """固定参数复算正文引用的关键数字。"""
    print("=== SELFTEST（合成算例，固定参数）===")
    # 换算表锚点
    assert k_allowed(12, 0.95) == 0, "n=12 时 95% 核心 = 100% 核心（失效条件 2）"
    assert k_allowed(20, 0.95) == 1, "n=20 时 95% 核心才允许缺 1 株"
    assert k_allowed(100, 0.95) == 5, "n=100 时 95% 核心允许缺 5 株"
    assert k_allowed(4, 0.95) == 0 and k_allowed(5, 0.95) == 0
    assert k_allowed(12, 0.99) == 0 and k_allowed(57, 0.99) == 0
    assert k_allowed(100, 0.99) == 1, "99% 档要到 n=100 才允许缺 1 株"
    # 二项式锚点：q=1%, n=12
    p0 = p_misjudge(12, 0.01, 0)
    assert abs(p0 - (1 - 0.99 ** 12)) < 1e-12, "k=0 时公式应退化为 1-(1-q)^n"
    assert abs(p0 - 0.113615) < 1e-5, f"11.36% 锚点，得 {p0:.6f}"
    pk1 = p_misjudge(12, 0.01, 1)
    assert abs(pk1 - 0.00617) < 5e-4, f"放宽到缺 1 株应降到 ≈0.62%，得 {pk1:.5f}"
    # 单调性：q 越大、n 越大，误判越多
    assert p_misjudge(20, 0.02, 1) > p_misjudge(20, 0.01, 1)
    assert p_misjudge(24, 0.01, 0) > p_misjudge(12, 0.01, 0)
    # 换算口径：「允许缺失 k 株（≈ x%）」的 x = (n-k)/n
    n, k = 20, k_allowed(20, 0.95)
    assert abs((n - k) / n - 0.95) < 1e-12
    print("SELFTEST PASS：n=12 时 95%≡100%（k=0）、n=20 起 k=1、"
          "q=1% 时 11.36%→0.62%（放宽 1 株）均复现")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="「≥95% 核心」↔「允许缺失 k 株」换算 + 注释漏检误判概率"
                    "（合成算例，非真实样本结果）")
    ap.add_argument("--thresholds", type=float, nargs="+",
                    default=[0.95, 0.99], help="核心存在比例档位")
    ap.add_argument("--strains", type=int, nargs="+",
                    default=[4, 5, 8, 10, 12, 15, 20, 24, 50, 54, 57, 100],
                    help="基因组数 n 列表")
    ap.add_argument("--miss-rates", type=float, nargs="+",
                    default=[0.005, 0.01, 0.02, 0.05],
                    help="单株注释漏检率 q（合成扫描值，非实测）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    print_threshold_table(args.strains, args.thresholds)
    print_miss_table(args.strains, args.miss_rates, args.thresholds[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())

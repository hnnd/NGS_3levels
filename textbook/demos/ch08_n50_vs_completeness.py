#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch08_n50_vs_completeness.py — N50 与完整度背离的反例（合成算例）

服务章节：第 8 章 §8.4「组装质量评估」概念小节、§8.5 失效条件第 2 条
（N50 与完整度可以背离；只报连续性不报正确性）。

数据性质：【合成算例】全部为固定种子的合成 contig 长度与算术复现，
与任何真实菌株无关；不得写成真实样本的实测结果。复现入口即本脚本（手算规则可复核）。

正文引用的输出：
  1. u06 §6.3 手算例：5 条 contig（100/80/50/40/30 kb）→ N50=80 kb，L50=2
  2. u06 习题 1：6 条 contig（500/300/200/150/100/50 kb）→ N50=300 kb，L50=2；
     前两条错接成 800 kb 后 → N50=800 kb，L50=1（错接使 N50 升高，被奖励而非惩罚）
  3. 两条染色体反例：正确 A=[2.0, 2.0] Mb vs 嵌合 B=[4.0] Mb —— 总长相同、
     基因都在（BUSCO 不变），N50 由 2.0 虚增至 4.0 Mb
  4. BUSCO 粒度：n=124 时 1 个基因 = 100/124 ≈ 0.81 个百分点（u06 §⑦）；
     C 相差 <1% 不足以下优劣结论；二项噪声量级 sqrt(p(1−p)/n)

参数含义：--example 只跑某一个算例（1-4）；--seed 随机种子（算例 4 的模拟用）。
"""
import argparse
import math
import sys


def n50_l50(lengths):
    """contig 长度降序累加达总长 50% 时那条的长度与已用条数。"""
    order = sorted(lengths, reverse=True)
    total = sum(order)
    half = total / 2
    acc = 0
    for i, ln in enumerate(order, 1):
        acc += ln
        if acc >= half:
            return ln, i, total
    return 0, 0, total


def kb(x):
    return f"{x:g} kb"


def example1():
    print("算例 1（讲义 u06 §6.3 手算例）：contigs = 100/80/50/40/30 kb")
    n50, l50, total = n50_l50([100, 80, 50, 40, 30])
    print(f"  总长 {total} kb，50% 阈值 {total/2:g} kb；累加 100→180 kb 越阈")
    print(f"  N50 = {n50} kb，L50 = {l50}\n")
    return n50 == 80 and l50 == 2


def example2():
    print("算例 2（讲义 u06 习题 1）：contigs = 500/300/200/150/100/50 kb")
    n50, l50, total = n50_l50([500, 300, 200, 150, 100, 50])
    print(f"  正确组装：总长 {total} kb，N50 = {n50} kb，L50 = {l50}")
    n50b, l50b, totalb = n50_l50([800, 200, 150, 100, 50])
    print(f"  错接版（最长两条连成 800 kb 嵌合序列）：总长 {totalb} kb，N50 = {n50b} kb，L50 = {l50b}")
    print("  → 总长一模一样，N50 由 300 升到 800 kb：错接被 N50 奖励\n")
    return (n50, l50, total, n50b, l50b) == (300, 2, 1300, 800, 1)


def example3():
    print("算例 3（§8.5 失效条件第 2 条的两染色体反例，合成）：")
    a = n50_l50([2.0, 2.0])     # 正确：两条独立环状染色体
    b = n50_l50([4.0])          # 错误：两染色体被短转座子嵌合缝成一条
    print(f"  正确组装 A：[2.0, 2.0] Mb → 总长 {a[2]} Mb，N50 = {a[0]} Mb，L50 = {a[1]}")
    print(f"  嵌合组装 B：[4.0] Mb    → 总长 {b[2]} Mb，N50 = {b[0]} Mb，L50 = {b[1]}")
    print(f"  B 的 N50 是 A 的 {b[0]/a[0]:g} 倍，但 B 是严重 misassembly；")
    print("  两套的 BUSCO 基因全部命中（C 不变）——只有正交证据能揭穿 B\n")
    return a[0] == 2.0 and b[0] == 4.0 and a[2] == b[2]


def example4():
    print("算例 4（BUSCO 粒度，合成/算术）：bacteria_odb10，n=124")
    n = 124
    one_gene_pct = 100.0 / n
    print(f"  1 个基因的得失 = {one_gene_pct:.2f} 个百分点（u06 §⑦「近 0.8 个百分点」）")
    print(f"  例：C:98.4%[S:97.6%,D:0.8%] 与 C:97.6% 只差 1 个基因 = {one_gene_pct:.1f} pp")
    for p in (0.95, 0.97):
        sd = math.sqrt(p * (1 - p) / n) * 100
        print(f"  若基因命中独立（上限假设），p={p:.2f} 时二项标准差 ≈ {sd:.2f} pp"
              f" —— C 差 <1% 远在此噪声内，不足以判优劣")
    c, s, d = 98.4, 97.6, 0.8
    print(f"  C=S+D 自检：{s}+{d}={s+d:.1f} = C ✓（只报 C 不报 S/D 的表无法解读）\n")
    return round(one_gene_pct, 2) == 0.81 and abs(s + d - c) < 1e-9


def selftest():
    print("=== SELFTEST（合成算例）===")
    ok = all([example1(), example2(), example3(), example4()])
    if not ok:
        print("SELFTEST FAIL")
        return 1
    print("SELFTEST PASS：N50/L50 算例、错接反例、BUSCO 粒度均与讲义口径一致")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="N50 与完整度背离反例演示（合成算例，非真实样本结果）")
    ap.add_argument("--example", type=int, choices=[1, 2, 3, 4],
                    help="只跑某一个算例（默认全部）")
    ap.add_argument("--seed", type=int, default=20261102,
                    help="保留参数：本脚本为确定性算术复现，种子仅作记录")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    fns = {1: example1, 2: example2, 3: example3, 4: example4}
    if args.example:
        return 0 if fns[args.example]() else 1
    ok = all(f() for f in fns.values())
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

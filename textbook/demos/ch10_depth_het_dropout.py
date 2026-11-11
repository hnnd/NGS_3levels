#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch10_depth_het_dropout.py — 测序深度对杂合位点检出的二项模型（合成算例）

服务章节：第 10 章 §10.4「深度—检出功效模型」（源讲义 m03 §7.2–7.3、习题 ⑩2）。
为失效条件「参考株自身比对应约为 0」之外的功效侧断言、以及
「低深度时杂合被系统性误判为纯合参考（allelic dropout）」提供复现入口。

模型（全部为理想化合成模型，非任何真实样本结果）：
  * 杂合位点上每条 read 独立地以概率 p 支持 ALT：X ~ Binomial(D, p)。
    理想等位抽样 p = 0.5；参考偏倚取 p = 0.45（讲义 §7.2「注意这是理想模型」
    第 ① 条：携带 ALT 的 read 更易丢，等位抽样不是严格的 0.5）。
  * 基因型后验（讲义 §7.3 链条的玩具版）：三个基因型 0/0、0/1、1/1 的
    单 read 支持 ALT 概率分别为 e（测序错误率，默认 Q30 ≈ 0.001）、0.5、1-e；
    先验 P(0/1) = h = 0.001（HaplotypeCaller 默认 --heterozygosity 0.001，
    「模型本来就认为杂合是罕见事件」）；P(0/0) = 1-h，P(1/1) = h（简化分配，
    对杂合→纯合参考误判方向无实质影响）。组合数 C(D,x) 在后验中约去。
  * GQ = -10·log10(1 - 最优后验)（Phred 口径，与 VCF GQ 同定义）。
  * 另给「纯证据规则」：caller 与过滤要求最少 2 条 ALT read（合成判据），
    则误判 = P(X ≤ 1) —— 即讲义 §7.2 表的第二列。

参数（--help 可见）：
  --depths        扫描深度列表（默认 5 8 10 15 20 30，与讲义表一致）
  --seq-error     单 read 测序错误率 e（默认 0.001 = Q30）
  --heterozygosity 杂合先验 h（默认 0.001，GATK --heterozygosity 默认）
  --ref-bias-p    参考偏倚下的 ALT 抽样概率（默认 0.45）
  --sim-n/--seed  蒙特卡洛对照（解析式 vs 模拟）的位点数与种子

正文引用的输出：
  - 讲义 §7.2 表的逐格复算值（P(X=0) / P(X≤1) / P(X≤2)，%）
  - 各深度下：纯证据误判率、含先验的后验误判率、误判杂合中 GQ≥20 的占比、
    误判事件的中位 GQ —— 自定义玩具先验下的示意（非 GATK 模型，教材不引用）
  - p = 0.45 参考偏倚列：同深度误判率抬升幅度（§7.2 理想模型注 ① 的量化）
  - 解析值与固定种子蒙特卡洛模拟的一致性核对（selftest 内含）
"""
import argparse
import math
import sys

import numpy as np

SEED = 20261104


def binom_pmf(d, p):
    """返回 x=0..d 的二项概率数组（p 为支持 ALT 的概率）。"""
    pmf = np.array([math.comb(d, x) for x in range(d + 1)], dtype=float)
    pmf *= p ** np.arange(d + 1) * (1.0 - p) ** (d - np.arange(d + 1))
    return pmf


def gt_posterior(x, d, eps, h):
    """三个基因型的未归一化后验分量（组合数已约去）。返回 (post, gq, call)。"""
    like = np.array([
        (1.0 - eps) ** (d - x) * eps ** x,          # 0/0：ALT read 都是测序错误
        0.5 ** d,                                    # 0/1：等位平衡
        eps ** (d - x) * (1.0 - eps) ** x,          # 1/1：REF read 都是测序错误
    ])
    prior = np.array([1.0 - h, h, h])
    post = like * prior
    post /= post.sum()
    call = int(np.argmax(post))
    gq = -10.0 * math.log10(max(1.0 - post[call], 1e-30))  # 高深度下 1-p 可为 0（浮点）
    return post, gq, call


def miscall_stats(d, p, eps, h, min_alt=2):
    """真杂合位点（X~Binom(d,p)）被误判为 0/0 的解析统计。

    返回 (纯证据误判率, 后验误判率, 误判中 GQ>=20 占比, 误判中位 GQ)。
    """
    pmf = binom_pmf(d, p)
    ev_only = float(pmf[:min_alt].sum())            # X <= min_alt-1
    mis_p, mis_gq_ge20, gq_list, w_list = 0.0, 0.0, [], []
    for x in range(d + 1):
        _, gq, call = gt_posterior(x, d, eps, h)
        if call == 0:                               # 后验最大 = 0/0 → 杂合被吞
            w = float(pmf[x])
            mis_p += w
            mis_gq_ge20 += w * (gq >= 20.0)
            gq_list.append(gq)
            w_list.append(w)
    gq_arr = np.array(gq_list)
    w_arr = np.array(w_list)
    w_arr /= w_arr.sum()
    order = np.argsort(gq_arr)
    cdf = np.cumsum(w_arr[order])
    median_gq = float(gq_arr[order][np.searchsorted(cdf, 0.5)])
    return ev_only, mis_p, mis_gq_ge20 / mis_p, median_gq


def main():
    ap = argparse.ArgumentParser(
        description="测序深度对杂合位点检出的二项模型（合成算例；源讲义 m03 §7.2–7.3）")
    ap.add_argument("--depths", type=int, nargs="+",
                    default=[5, 8, 10, 15, 20, 30], help="扫描深度（默认与讲义表一致）")
    ap.add_argument("--seq-error", type=float, default=0.001,
                    help="单 read 测序错误率 e（默认 0.001 = Q30）")
    ap.add_argument("--heterozygosity", type=float, default=0.001,
                    help="杂合先验 h（默认 0.001 = GATK --heterozygosity 默认）")
    ap.add_argument("--ref-bias-p", type=float, default=0.45,
                    help="参考偏倚下 ALT 抽样概率（默认 0.45）")
    ap.add_argument("--min-alt", type=int, default=2,
                    help="caller 要求的最少 ALT 证据条数（默认 2）")
    ap.add_argument("--sim-n", type=int, default=200000,
                    help="蒙特卡洛对照位点数（默认 200000）")
    ap.add_argument("--seed", type=int, default=SEED, help="随机种子")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    e, h = args.seq_error, args.heterozygosity
    assert 0 < e < 0.5 and 0 < h < 0.5 and 0 < args.ref_bias_p < 1.0

    print("=" * 78)
    print("[Part 1] 讲义 §7.2 表逐格复算：X ~ Binomial(D, 0.5)，杂合位点支持 ALT 的 read 数")
    print("=" * 78)
    print(f"{'D':>4} | {'P(X=0) %':>10} {'P(X<=1) %':>10} {'P(X<=2) %':>11}")
    print("-" * 44)
    table = {}
    for d in args.depths:
        pmf = binom_pmf(d, 0.5)
        row = (100.0 * pmf[0], 100.0 * pmf[:2].sum(), 100.0 * pmf[:3].sum())
        table[d] = row
        print(f"{d:>4} | {row[0]:>10.4g} {row[1]:>10.4g} {row[2]:>11.4g}")
    print("对照讲义印刷值：5×: 3.1 / 18.8 / 50.0 ｜ 8×: 0.39 / 3.5 / 14.5 ｜ "
          "10×: 0.098 / 1.07 / 5.5")
    print("                15×: 0.003 / 0.049 / 0.37 ｜ 20×: 0.0001 / 0.002 / 0.020 "
          "｜ 30×: ≈0 / ≈0 / 0.00004")

    print()
    print("=" * 78)
    print(f"[Part 2]（玩具模型，不入正文）杂合被误判为 0/0：纯证据规则 vs 自定义先验后验（e=Q30, h=0.001, "
          f"min_alt={args.min_alt}）")
    print("=" * 78)
    print(f"{'D':>4} | {'P(X<=%d) %%' % (args.min_alt - 1):>12} {'后验误判率 %':>12} "
          f"{'误判且GQ>=20 占比':>16} {'误判中位 GQ':>12} | {'p=0.45 后验误判率 %':>18}")
    print("-" * 92)
    stats = {}
    for d in args.depths:
        s_ideal = miscall_stats(d, 0.5, e, h, args.min_alt)
        s_bias = miscall_stats(d, args.ref_bias_p, e, h, args.min_alt)
        stats[d] = (s_ideal, s_bias)
        print(f"{d:>4} | {100 * s_ideal[0]:>12.3f} {100 * s_ideal[1]:>12.3f} "
              f"{100 * s_ideal[2]:>15.1f}% {s_ideal[3]:>12.1f} | "
              f"{100 * s_bias[1]:>18.3f}")
    print("注意：Part 2 是自定义玩具后验（个体先验 P(0/0)=1-h、P(0/1)=P(1/1)=h），"
          "不是 GATK 的模型——GATK 的 heterozygosity 是位点先验，不改变个体 GL；")
    print("      表中百分数不是任何 caller 的真实漏检率，p=0.45 列也只是参考偏倚的方向示意；"
          "教材第 10 章只引用 Part 1（D 即正文的局部有效深度 d），不要把本表抄进报告。")

    print()
    print("=" * 78)
    print("[Part 3] 解析 vs 模拟对照（固定种子蒙特卡洛，selftest 的一致性依据）")
    print("=" * 78)
    rng = np.random.default_rng(args.seed)
    n = args.sim_n
    d_check = 10
    x_sim = rng.binomial(d_check, 0.5, size=n)
    mis_sim = np.mean([gt_posterior(int(x), d_check, e, h)[2] == 0 for x in x_sim])
    mis_ana = stats[d_check][0][1]
    print(f"D={d_check}，n={n}，seed={args.seed}：模拟误判率 {100 * mis_sim:.3f}% "
          f"vs 解析 {100 * mis_ana:.3f}%（应一致到蒙特卡洛噪声）")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        # 讲义 §7.2 表逐格锚定（讲义按有效数字取舍，容差 = max(2% 印刷值, 5e-5%)）
        anchors = {5: (3.1, 18.8, 50.0), 8: (0.39, 3.5, 14.5),
                   10: (0.098, 1.07, 5.5), 15: (0.003, 0.049, 0.37),
                   20: (0.0001, 0.002, 0.020)}
        for d, exp in anchors.items():
            ok_d = all(abs(v - b) <= max(0.02 * abs(b), 5e-5)
                       for v, b in zip(table[d], exp))
            check(f"D={d}  讲义表三格复算一致（{exp}）", ok_d)
        check("D=30 P(X=0)、P(X<=1) ≈ 0（<1e-4%）",
              table[30][0] < 1e-4 and table[30][1] < 1e-4)
        check("D=30 P(X<=2)=0.00004%",
              abs(table[30][2] - 0.00004) <= 5e-5)
        # §7.3 链条的方向性断言
        ev_rates = [stats[d][0][0] for d in args.depths]
        post_rates = [stats[d][0][1] for d in args.depths]
        check("P(X<=1) 证据规则误判率随深度严格下降",
              all(a > b for a, b in zip(ev_rates, ev_rates[1:])))
        # 后验误判区边界 x*（判成 0/0 的最大 ALT 条数）：先验 999:1 把边界推到
        # x* ≈ 0.1d+1（eps=Q30 时的似然比零点），故 5×/8× 误判区 == X<=1，
        # d>=10 起误判区比证据规则更宽——这是 §7.3「先验偏向纯合参考」的定量版，
        # 也是讲义选 P(X<=2) 作第三列的原因（10× 边界恰好落在 X=2 格）。
        boundary = {}
        for d in args.depths:
            xs = [x for x in range(d + 1)
                  if gt_posterior(x, d, e, h)[2] == 0]
            boundary[d] = max(xs)
        check("后验误判区边界 x* 随深度不降",
              all(a <= b for a, b in zip([boundary[d] for d in args.depths],
                                         [boundary[d] for d in args.depths][1:])))
        check("5×/8× 后验误判区 == X<=1（与证据规则一致）",
              boundary[5] == args.min_alt - 1 and boundary[8] == args.min_alt - 1)
        check("d>=10 后验误判率 > P(X<=1)（先验把边界格拉入误判区）",
              all(stats[d][0][1] > stats[d][0][0]
                  for d in args.depths if d >= 10))
        check("10× 后验误判区恰好 == X<=2（讲义表第三列的定量解释）",
              boundary[10] == 2
              and abs(100 * stats[10][0][1] - table[10][2]) < 1e-9)
        check("10× 误判且 GQ>=20 占比 > 0（§7.3「GQ 还可能不低」）",
              stats[10][0][2] > 0.0)
        check("5× 误判且 GQ>=20 占比 > 10%（深缺失格 GQ 高）",
              stats[5][0][2] > 0.10)
        # 参考偏倚方向
        check("每个深度 p=0.45 误判率 > p=0.5 误判率",
              all(stats[d][1][1] > stats[d][0][1] for d in args.depths))
        # 解析 vs 模拟（蒙特卡洛噪声 ~ sqrt(p(1-p)/n) ≈ 0.03%）
        check(f"解析 vs 模拟一致（|Δ|={100 * abs(mis_sim - mis_ana):.4f}% < 0.1%）",
              abs(mis_sim - mis_ana) < 1e-3)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

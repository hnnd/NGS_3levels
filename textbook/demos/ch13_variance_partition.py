#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch13_variance_partition.py — 方差分解：加重复 vs 加深度的功效权衡（合成算例）

服务章节：第 13 章 §13.4「方差分解与重复-深度权衡」（源讲义 m01 §4.4–4.5、§4.7，
l0_06_stats §5；功效与 p 值的定义只引用第 12 章，不重讲）。
为失效条件 3「深度换不来重复：超过饱和点后加深度几乎不提升功效」与
正文断言「固定预算下增加生物学重复优于增加测序深度」提供复现入口。

模型（全部为理想化合成模型，非任何真实样本结果）：
  * 讲义 m01 §4.4 的方差分解：单样本测量方差 v(d) = σ²_b + σ²_t/d
    —— σ²_b 为生物学个体间方差（内在属性，与测序仪无关），
       σ²_t 为技术方差（合成取值为「每 1 M reads 的技术方差」），d 为深度（M reads）。
  * 两组各 n 个生物学重复、组间真差 δ 时，组间均值差的
    标准误 SE = sqrt(2·v(d)/n)；检验统计量服从非中心 t
    （df = 2n−2，ncp = δ/SE），功效按双侧 α = 0.05 由非中心 t 分布解析计算。
  * 固定预算约束（总 reads B = 2·n·d）下：SE² = (σ²_b·d + σ²_t)·2/B，
    即 SE² 随 d 线性上升 —— 预算固定时「加深」在解析上严格劣于「加重复」；
    深度的下限由检出需求决定（稀有转录本、杂合位点、覆盖度），不由本模型决定。

参数（--help 可见）：
  --sigma-b       生物学方差 σ²_b（默认 1.0，合成取值）
  --sigma-t       每 1 M reads 的技术方差 σ²_t（默认 2.0，合成取值；
                  仅用于演示方向与饱和形态，不对应任何真实实验标定）
  --delta         组间真差 δ（默认 1.0，即 δ/σ_b = 1，与 l0_06 演示 6 同设定）
  --alpha         显著性水准（默认 0.05）
  --budget        每组预算 B_group（M reads，默认 90；两组合计 180，对齐 l0_06 §5 的
                  「180 M 预算」表述与 m01 ⑩3 的自洽算例）
  --sim-n/--seed  蒙特卡洛对照（解析功效 vs 模拟）的重复次数与种子

正文引用的输出：
  - Part 0 手算规则：覆盖度账 e^(−C)（C=10/30）、共识账 P(Binom(d,ε) ≥ d/2)
    （讲义 §4.7 两本账的逐格复算）；m01 §4.5 杂合 10× 的逐格复算
    —— 含 CASE-CH13-01 的复算证据（P(X≤1)=1.07%，讲义「超过 5%」对应的是 P(X≤2)=5.47%）
  - Part 1 方差分解表：v(d) 随深度收敛到 σ²_b（饱和的形态证据）
  - Part 2 功效表：固定预算 B=180 M（两组）下 (n, d) 组合的功效排序
    —— 「加重复优于加深度」的方向性演示；含 6×20 M vs 3×40 M 对照
    （讲义 §4.4 引 Schurch 2016 的方向性结论；原研究结论按原研究引用，见 case.md）
  - Part 3 饱和曲线：固定 n=6，深度 5→120 M 的功效平台（失效条件 3 的定量入口）
  - Part 4 解析 vs 蒙特卡洛对照（selftest 的一致性依据），含与 R power.t.test
    口径差异的注记（strict=FALSE，见 CASE-CH12-02 / demos/ch12_paired_power.R 算例 D）
"""
import argparse
import math
import sys

import numpy as np
from scipy import stats

SEED = 20261104


def power_twosample(n, v, delta, alpha):
    """两组各 n 重复、单样本方差 v、真差 delta 时的双侧 t 检验解析功效。"""
    df = 2 * n - 2
    ncp = delta / math.sqrt(2.0 * v / n)
    tcrit = stats.t.ppf(1.0 - alpha / 2.0, df)
    return float(stats.nct.sf(tcrit, df, ncp) + stats.nct.cdf(-tcrit, df, ncp))


def main():
    ap = argparse.ArgumentParser(
        description="方差分解：加重复 vs 加深度的功效权衡（合成算例；源讲义 m01 §4.4–4.7、l0_06 §5）")
    ap.add_argument("--sigma-b", type=float, default=1.0, help="生物学方差 σ²_b（默认 1.0）")
    ap.add_argument("--sigma-t", type=float, default=2.0, help="每 1 M reads 的技术方差 σ²_t（默认 2.0，合成取值）")
    ap.add_argument("--delta", type=float, default=1.0, help="组间真差 δ（默认 1.0，δ/σ_b = 1）")
    ap.add_argument("--alpha", type=float, default=0.05, help="显著性水准（默认 0.05）")
    ap.add_argument("--budget", type=float, default=90.0, help="每组预算（M reads，默认 90；两组合计 180）")
    ap.add_argument("--sim-n", type=int, default=20000, help="蒙特卡洛重复次数（默认 20000）")
    ap.add_argument("--seed", type=int, default=SEED, help="随机种子")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    sb, st, delta, alpha = args.sigma_b, args.sigma_t, args.delta, args.alpha
    assert sb > 0 and st > 0 and delta > 0 and 0 < alpha < 1

    print("=" * 78)
    print("[Part 0] 手算规则：深度规划的两本账 + m01 §4.5 杂合位点复算（逐格可复核）")
    print("=" * 78)
    print("覆盖度账（讲义 §4.7 第一本）：P(某碱基 0 覆盖) = e^(−C)")
    for c in (10, 30):
        print(f"  C={c:>2}×：e^(−{c}) = {math.exp(-c):.3e}"
              + ("  （讲义：约 4.5×10⁻⁵）" if c == 10 else "  （讲义：已可忽略）"))
    print("共识账（讲义 §4.7 第二本）：半数以上 read 同点犯同一错，X ~ Binomial(d, ε=1%)")
    d_cons = 20
    p_cons = stats.binom.sf(math.ceil(d_cons / 2.0) - 1, d_cons, 0.01)
    print(f"  d={d_cons}：P(X ≥ {math.ceil(d_cons / 2.0)}) = {p_cons:.2e}  （讲义：低于 10⁻¹⁰，"
          f"{'一致' if p_cons < 1e-10 else '不符'}）")
    print("杂合位点（讲义 §4.5）：10× 深度、等位抽样 p=0.5，X ~ Binomial(10, 0.5)")
    for k in (1, 2):
        p_le = stats.binom.cdf(k, 10, 0.5)
        print(f"  P(突变 read ≤ {k}) = {p_le:.4f} = {100 * p_le:.2f}%"
              + ("  ← 讲义写「超过 5%」对应的是这一格（CASE-CH13-01）" if k == 2 else
                 "  ← 讲义写「≤ 1」时的实际值（与「超过 5%」不符，CASE-CH13-01）"))
    print("  25–30× 压制丢失率 < 0.1%：P(X≤1|Binom(25,0.5)) = "
          f"{stats.binom.cdf(1, 25, 0.5):.2e}，P(X≤2) = {stats.binom.cdf(2, 25, 0.5):.2e}"
          "  → 讲义口径成立")
    print("  深度换算账（m01 ⑩5 手算）：380 Mb × 30× ÷ (0.90 × (1−0.08)) = "
          f"{380 * 30 / (0.90 * 0.92):.0f} Mb ≈ {380 * 30 / (0.90 * 0.92) / 1000:.2f} Gb")

    print()
    print("=" * 78)
    print(f"[Part 1] 方差分解：v(d) = σ²_b + σ²_t/d（σ²_b={sb}, σ²_t={st}，合成取值）")
    print("=" * 78)
    print(f"{'d (M reads)':>11} | {'σ²_t/d':>8} {'v(d)':>8} {'技术占比':>9}")
    depths = [5, 10, 20, 30, 40, 60, 80, 120]
    vtab = {}
    for d in depths:
        v = sb + st / d
        vtab[d] = v
        print(f"{d:>11} | {st / d:>8.4f} {v:>8.4f} {100 * (st / d) / v:>8.1f}%")
    print("→ v(d) 随深度收敛到 σ²_b：d 从 20 翻倍到 40，v 只降 "
          f"{100 * (1 - vtab[40] / vtab[20]):.1f}%（饱和的形态证据）")

    print()
    print("=" * 78)
    print(f"[Part 2] 固定预算：两组合计 {2 * args.budget:.0f} M reads，δ/σ_b = {delta / math.sqrt(sb):.1f}")
    print("=" * 78)
    combos = [(3, 30), (6, 15), (9, 10), (18, 5)]
    print(f"{'设计 (n × d M)':>16} | {'v(d)':>7} {'SE(均值差)':>10} {'功效(双侧α=%.2f)' % alpha:>16}")
    ptab = {}
    for n, d in combos:
        assert 2 * n * d <= 2 * args.budget + 1e-9
        v = sb + st / d
        se = math.sqrt(2 * v / n)
        pw = power_twosample(n, v, delta, alpha)
        ptab[(n, d)] = pw
        print(f"{n:>6} × {d:<3}      | {v:>7.4f} {se:>10.4f} {pw:>16.3f}")
    print("→ 同一预算下，n 翻倍（深度相应减半）功效单调上升：解析上 SE² = "
          "(σ²_b·d + σ²_t)·2/B，预算固定时 SE² 随 d 线性上升")
    print()
    print("讲义 §4.4 方向性对照（Schurch 2016 结论的方向演示，非原研究数值）：")
    for n, d in [(6, 20), (3, 40)]:
        v = sb + st / d
        pw = power_twosample(n, v, delta, alpha)
        ptab[(n, d)] = pw
        print(f"  {n} × {d} M：v = {v:.4f}，功效 = {pw:.3f}")
    print("  → 「6 × 20 M 优于 3 × 40 M」的方向在合成模型下成立；"
          "教材正文引用 Schurch 2016 时按原研究结论写（见 case.md §④ 口径）")

    print()
    print("=" * 78)
    print("[Part 3] 饱和曲线：固定 n = 6，深度 5 → 120 M（失效条件 3 的定量入口）")
    print("=" * 78)
    print(f"{'d (M reads)':>11} | {'v(d)':>8} {'功效':>7} {'相对 d=20':>10}")
    sat_depths = [5, 10, 20, 30, 40, 60, 120]
    sat = {d: power_twosample(6, sb + st / d, delta, alpha) for d in sat_depths}
    for d in sat_depths:
        v = sb + st / d
        print(f"{d:>11} | {v:>8.4f} {sat[d]:>7.3f} {sat[d] / sat[20]:>10.3f}")
    print("→ 深度从 20 M 加到 120 M（6 倍），功效变化 "
          f"{100 * (sat[120] / sat[20] - 1):+.1f}%；同预算把 reads 换成重复（Part 2）提升大得多")

    print()
    print("=" * 78)
    print("[Part 4] 解析 vs 蒙特卡洛（固定种子；selftest 的一致性依据）")
    print("=" * 78)
    rng = np.random.default_rng(args.seed)
    n_mc, d_mc = 6, 15
    v_mc = sb + st / d_mc
    # 层次模型：每个体先抽生物学偏移 b_i ~ N(0, σ²_b)，
    # 再以 d 次独立技术抽样的均值作测量（合成「深度」的机制）
    bio = rng.normal(0.0, math.sqrt(sb), size=(args.sim_n, 2, n_mc))
    tech = rng.normal(0.0, math.sqrt(st), size=(args.sim_n, 2, n_mc, d_mc)).mean(axis=3)
    y = bio + tech
    y[:, 1, :] += delta
    xbar = y.mean(axis=2)
    s2 = y.var(axis=2, ddof=1)
    tstat = (xbar[:, 1] - xbar[:, 0]) / np.sqrt(s2.sum(axis=1) / n_mc)
    p_sim = float(np.mean(np.abs(tstat) > stats.t.ppf(1 - alpha / 2, 2 * n_mc - 2)))
    p_ana = ptab[(6, 15)]
    print(f"n={n_mc}，d={d_mc} M：模拟功效 {p_sim:.3f} vs 解析 {p_ana:.3f}"
          f"（蒙特卡洛标准误 ≈ {math.sqrt(p_ana * (1 - p_ana) / args.sim_n):.3f}）")
    print("口径注记：R power.t.test 默认 strict=FALSE（只计一侧拒绝域），"
          "本脚本用双侧精确（两侧拒绝域之和）；n=3、σ_t=0 时 R = 0.157 vs "
          "本脚本 nct 双侧见下，差异 < 0.01（CASE-CH12-02 / demos/ch12_paired_power.R 算例 D）")
    p_n3 = power_twosample(3, sb, delta, alpha)
    print(f"  n=3、v=σ²_b=1（纯生物学，无技术项）：nct 双侧 = {p_n3:.4f}（R strict=FALSE = 0.157）")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        # Part 0 手算规则锚定
        check("e^(−10) = 4.54e-05 ≈ 讲义 4.5×10⁻⁵",
              abs(math.exp(-10) - 4.539993e-05) < 1e-9)
        check("共识账 d=20、ε=1%：P(X≥10) < 1e-10（讲义口径）",
              stats.binom.sf(9, 20, 0.01) < 1e-10)
        check("CASE-CH13-01：P(X≤1|Binom(10,.5)) = 1.07% ≠ 「超过 5%」",
              abs(stats.binom.cdf(1, 10, 0.5) - 0.0107421875) < 1e-9)
        check("CASE-CH13-01：讲义「超过 5%」对应 P(X≤2) = 5.47%",
              abs(stats.binom.cdf(2, 10, 0.5) - 0.0546875) < 1e-9)
        check("25× 时 P(X≤2) < 1e-4（讲义「丢失率 < 0.1%」成立）",
              stats.binom.cdf(2, 25, 0.5) < 1e-4)
        check("换算账 380 Mb × 30× ÷ 0.828 ≈ 13.77 Gb",
              abs(380 * 30 / (0.90 * 0.92) / 1000 - 13.77) < 0.05)
        # Part 1：v(d) 单调下降且收敛
        check("v(d) 随深度严格下降", all(vtab[a] > vtab[b] for a, b in zip(depths, depths[1:])))
        check("v(120) 与 σ²_b 相对差 < 2%（技术项收敛）",
              abs(vtab[120] - sb) / sb < 0.02)
        # Part 2：预算线上 n 越大功效越高
        pw_line = [ptab[c] for c in combos]
        check("固定预算线上功效随 n 严格上升", all(a < b for a, b in zip(pw_line, pw_line[1:])))
        check("6×20 M 功效 > 3×40 M（讲义 §4.4 方向）",
              ptab[(6, 20)] > ptab[(3, 40)])
        # Part 3：饱和
        check("n=6 时功效随深度增幅递减（饱和）",
              all(sat[b] - sat[a] < sat[a] - sat[prev]
                  for prev, a, b in zip([5, 10, 20], [10, 20, 30], [20, 30, 40])))
        check("深度 20→120 M 功效相对增幅 < 10%（失效条件 3）",
              sat[120] / sat[20] - 1 < 0.10)
        # Part 4：解析 vs 模拟
        check(f"解析 vs 模拟一致（|Δ|={abs(p_sim - p_ana):.3f} < 3×蒙特卡洛标准误）",
              abs(p_sim - p_ana) < 3 * math.sqrt(p_ana * (1 - p_ana) / args.sim_n))
        check("n=3 纯生物学口径与 R power.t.test 差异 < 0.01（CASE-CH12-02）",
              abs(p_n3 - 0.157) < 0.01)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

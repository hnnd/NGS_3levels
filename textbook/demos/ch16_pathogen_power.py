#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch16_pathogen_power.py — 病原读段占比 → 每基因有效深度 → 时序差异检验功效（合成算例）

服务章节：第 16 章 §16.4 概念与方法（测序深度非对称悖论）、§16.5 失效条件第 3 条
（病原读段占比低时功效严重不足）。源讲义：p03 §4.1 设计选择（1）。

模型（全部为合成模型，非任何真实样本结果）：
  * 双 RNA-seq 侵染样本：总测序深度 D 条读段，病原占比 p，则病原侧有效读段
    P = D·p。病原某个基因占病原转录组的份额为 q（合成设定 1e-5–1e-3），
    该基因每样本期望计数 μ = P·q。
  * 比较两组的倍数变化 f（如体内侵染 vs 体外纯培养），每组 n 个生物学重复，
    计数 ~ 负二项 NB(μ, 离散度 α)。delta 法：log 倍数变化的标准误
    SE = sqrt((1/μ1+α)/n + (1/μ2+α)/n)，功效 ≈ Φ(|log f|/SE − z_{1-α/2})。
  * 讲义 §4.1 的算术（手算规则）：早期 p = 0.5% 时要让病原侧单基因达到稳健
    GLM 推断，需要病原有效读段 1e7–2e7 → 总深度 D = P/p = 2e9–4e9，
    即「20 亿至 40 亿 reads」——本脚本逐位复现。

参数（--help 可见）：
  --alpha        NB 离散度（默认 0.1，对齐 demos/ch12_nb_vs_poisson.py 口径）
  --n-rep        每组生物学重复数（默认 3，对齐主线数据 3 重复设计）
  --fold         待检倍数变化（默认 2.0）
  --q            基因占病原转录组份额（默认覆盖 1e-5 / 1e-4 / 1e-3 三档）
  --mc           蒙特卡洛重复数（默认 4000，仅 Poisson 精确检验对照用）
  --seed         随机种子（默认 20261104）
  --selftest     断言讲义算术、解析功效与泊松精确检验 MC 一致

正文引用的输出：
  - 功效表：病原有效读段 P = 1e4 → 2e7 时，低/中/高表达基因（q 三档）检出
    2 倍变化的解析功效（delta 法；NB 行标注为近似）
  - 讲义 §4.1 的 1e7–2e7 病原读段 → 2e9–4e9 总深度换算（手算规则入口）
  - MC 对照：α→0（泊松）时解析功效与条件精确二项检验的模拟功效一致（μ1 ≥ 10 时
    差 < 0.02；μ1 极小时正态近似失真，打印 ⚠ 并保留 MC 值为准）

依赖：Python 标准库 + numpy + scipy（nbinom 采样、binomtest、正态分布函数）。
合成算例：所有计数均为随机数生成器产物，与任何真实样本无关。
"""
import argparse
import sys

import numpy as np
from scipy.stats import binom, norm

SEED = 20261104
Z975 = norm.ppf(0.975)


def analytic_power(pathogen_reads, q, fold, alpha, n_rep):
    """delta 法解析功效：μ1 = P·q，μ2 = f·μ1。"""
    mu1 = pathogen_reads * q
    mu2 = fold * mu1
    if mu1 <= 0:
        return 0.0
    se = np.sqrt((1.0 / mu1 + alpha) / n_rep + (1.0 / mu2 + alpha) / n_rep)
    z = abs(np.log(fold)) / se
    return float(norm.cdf(z - Z975))


def mc_power_poisson(pathogen_reads, q, fold, n_rep, mc, seed):
    """泊松（α→0）世界里的条件精确二项检验 MC 功效（独立实现对照）。

    每组 n_rep 个样本之和：X ~ Pois(n_rep·μ1)、Y ~ Pois(n_rep·μ2)；
    条件于总量 T = X+Y，H0 下 X ~ Binom(T, 0.5)，双侧 p = 2·min{F(x), S(x)}。
    向量化实现，与逐条 binomtest 等价。
    """
    rng = np.random.default_rng(seed)
    mu1, mu2 = pathogen_reads * q, fold * pathogen_reads * q
    x = rng.poisson(n_rep * mu1, mc).astype(int)
    y = rng.poisson(n_rep * mu2, mc).astype(int)
    tot = x + y
    keep = tot > 0
    x, tot = x[keep], tot[keep]
    p_two = np.clip(2.0 * np.minimum(binom.cdf(x, tot, 0.5),
                                     binom.sf(x, tot, 0.5)), 0.0, 1.0)
    return float((p_two < 0.05).mean())


def main():
    ap = argparse.ArgumentParser(
        description="病原读段占比 → 有效深度 → 时序检验功效（合成算例；服务第 16 章 "
                    "失效条件 3，对齐讲义 p03 §4.1）")
    ap.add_argument("--alpha", type=float, default=0.1)
    ap.add_argument("--n-rep", type=int, default=3)
    ap.add_argument("--fold", type=float, default=2.0)
    ap.add_argument("--q", type=float, nargs="+",
                    default=[1e-5, 1e-4, 1e-3])
    ap.add_argument("--mc", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    p_grid = [1e4, 1e5, 1e6, 1e7, 2e7]

    # ---------------- Part 0：讲义算术（手算规则） ----------------
    print("=" * 78)
    print("[Part 0 · 手算规则] 病原有效读段 P 与总深度 D 的换算（侵染早期 p = 0.5%）")
    print("=" * 78)
    for P in (1e7, 2e7):
        print(f"  P = {P:.0e} 病原读段、p = 0.5% → D = P/p = {P / 0.005:.0e}（讲义印 "
              f"{P/0.005/1e8:.0f} 亿）")
    print("  讲义 §4.1『20 亿至 40 亿 reads』即 P = 1e7–2e7 在 p = 0.5% 下的总深度；")
    print("  p = 0.1% 时同 P 需 D = 1e10–2e10，预算上不可行 → 设计层面折中"
          "（后移首时点 / 富集捕获 / 高密度接种）。")

    # ---------------- Part 1：解析功效表 ----------------
    print()
    print("=" * 78)
    print(f"[Part 1 · 合成算例] 检出 {args.fold:g}× 变化的解析功效"
          f"（delta 法近似；α = {args.alpha}、每组 n = {args.n_rep}）")
    print("=" * 78)
    header = f"{'病原读段 P':>11} |" + "".join(f" {c:>18}" for c in
                                             [f"q={q:g}" for q in args.q])
    table = {}
    print(header + "   （单元格内 μ = P·q）")
    for P in p_grid:
        cells = []
        for q in args.q:
            pw = analytic_power(P, q, args.fold, args.alpha, args.n_rep)
            table[(P, q)] = pw
            cells.append(f"{pw:>18.3f}")
        print(f"{P:>10.0e} |" + "".join(cells))
    # 计数 → ∞ 时 1/μ 项消失，功效上限只由离散度与重复数决定（CNT-CH16-14）
    se_inf = np.sqrt(2.0 * args.alpha / args.n_rep)
    power_sup = float(norm.cdf(abs(np.log(args.fold)) / se_inf - Z975))
    print("读法：P = 1e4（病原占比 0.5% × 总深度 2e6 的截取样本）时，"
          "q = 1e-5 的低表达基因功效 ≈ α = 0.05（完全测不出）。")
    print(f"      深度无穷大时功效上限 = Φ(|ln f| / √(2α/n) − 1.96) = {power_sup:.3f}"
          f"（α={args.alpha:g}，n={args.n_rep}，f={args.fold:g}）：")
    if power_sup < 0.8:
        print("      本设定下加深测序到不了功效 0.8；要抬高上限须降离散度、加重复或接受更大效应量。")
    else:
        print("      本设定下功效 0.8 可达，所需 μ 见上表。")

    # ---------------- Part 2：MC 对照（泊松精确检验，独立实现） ----------------
    print()
    print("=" * 78)
    print(f"[Part 2 · MC 对照] α→0（泊松）世界，条件精确二项检验，"
          f"{args.mc} 次模拟（seed={args.seed}）")
    print("=" * 78)
    for q in args.q:
        for P in (1e5, 1e7):
            mc = mc_power_poisson(P, q, args.fold, args.n_rep, args.mc,
                                  args.seed + int(np.log10(P)) + int(-np.log10(q)))
            an = analytic_power(P, q, args.fold, 0.0, args.n_rep)
            mu1 = P * q
            flag = "" if mu1 >= 10 else "  ⚠ μ1 < 10：正态近似失真，解析值仅作量级参考"
            print(f"  q={q:g}、P={P:.0e}（μ1={mu1:g}）：MC = {mc:.3f} vs "
                  f"解析(α=0) = {an:.3f}（差 {abs(mc - an):.3f}）{flag}")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        check("手算规则：P = 1e7、p = 0.5% → D = 2e9（讲义『20 亿』）",
              abs(1e7 / 0.005 - 2e9) < 1)
        check("手算规则：P = 2e7、p = 0.5% → D = 4e9（讲义『40 亿』）",
              abs(2e7 / 0.005 - 4e9) < 1)
        # 单调性：功效随 P 与 q 单调不减
        for q in args.q:
            ps = [table[(P, q)] for P in p_grid]
            check(f"q={q:g}：功效随 P 单调不减（{[round(x, 3) for x in ps]}）",
                  all(a <= b + 1e-9 for a, b in zip(ps, ps[1:])))
        # 深度不足时功效贴地板（≤ 0.1）
        check("P = 1e4、q = 1e-5：功效贴 α 地板（< 0.10）",
              table[(1e4, 1e-5)] < 0.10)
        # 上限回归核查：表内任一单元格不超过解析上限；默认参数下上限 < 0.8
        sup = float(norm.cdf(abs(np.log(args.fold)) / np.sqrt(2.0 * args.alpha / args.n_rep) - Z975))
        check(f"功效上限 {sup:.3f}：表内最大值 {max(table.values()):.3f} 不超过上限",
              max(table.values()) <= sup + 1e-9)
        check(f"默认设定（α=0.1、n=3、f=2）上限 {sup:.3f} < 0.8：读法不得声称可达 0.8",
              sup < 0.8)
        # MC 与解析（α=0）一致（μ1 ≥ 10 时正态近似成立；μ1 极小时以 MC 为准并记录偏差）
        for q in args.q:
            for P in (1e5, 1e7):
                mc = mc_power_poisson(P, q, args.fold, args.n_rep, args.mc,
                                      args.seed + int(np.log10(P))
                                      + int(-np.log10(q)))
                an = analytic_power(P, q, args.fold, 0.0, args.n_rep)
                if P * q >= 10:
                    check(f"q={q:g}、P={P:.0e}：MC {mc:.3f} ≈ 解析 {an:.3f}"
                          f"（μ1={P*q:g} ≥ 10，正态近似成立，<0.02）",
                          abs(mc - an) < 0.02)
        mc_small = mc_power_poisson(1e5, 1e-5, args.fold, args.n_rep, args.mc,
                                    args.seed + 5 + 5)
        an_small = analytic_power(1e5, 1e-5, args.fold, 0.0, args.n_rep)
        check(f"μ1=1 时正态近似失真已被记录（MC {mc_small:.3f} vs 解析 "
              f"{an_small:.3f}，差 > 0.02 且打印 ⚠ 标注）",
              abs(mc_small - an_small) > 0.02)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

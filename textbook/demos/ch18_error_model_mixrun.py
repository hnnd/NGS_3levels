#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch18_error_model_mixrun.py — 跨 run 混合学习错误率的失真（合成错误谱，简化版）

服务于：教材第 18 章（扩增子测序与微生物群落多样性）§18.5 失效条件第 2 条
「混合不同测序 run 学错误率，错误模型失真」，
对应讲义 m06 §4.3-2（learnErrors 必须按独立测序批次分别执行）/ ⑥-6.2
（错误率图诊断）/ ⑨-4；本层贯穿数据 PRJDB13364 的 20 个样本跨 2017/2018/2019
三年测序，正是此失效的落点。

合成设定（不基于任何真实样本；固定种子可复现；为让机制可见，两 run 的错误谱
差异比真实数据大 —— 讲义只说「不同批次错误结构不同」，本 demo 用 4 倍差距演示）：
  - run A：名义错误谱 p_A(q) = 10^(−q/10)（Phred 定义，Q30 ≈ 1e-3/碱基）；
  - run B：整体差 6 个 Phred 档 p_B(q) = 10^(−(q−6)/10)（≈ 4× 错误率）；
  - 每个 Q 档模拟 n 次观测，错误计数 ~ Binomial(n, p)，
    分别学 per-run 错误率与「混在一起学」的合并错误率；
  - DADA2 的 ASV/错误判定（讲义 ④-4.2 简化）：丰度 n 的亲本序列若经错误产生
    某变异序列的期望拷贝 λ = n·p，观测到 k 条时，
    p_val = P(Poisson(λ) ≥ k)，p_val < OMEGA_A（1e-40）才判为真实 ASV；
    由此得判定边界 k*(n, p) = 使尾部概率 < OMEGA_A 的最小 k。

正文引用的输出：
  - per-run 学习能还原各自真实谱（蒙特卡洛噪声内）；合并学习的谱对 run B
    **低估**（本参数下 ≈ 0.63×）、对 run A **高估**（≈ 2.5×）——
    「混学的模型对哪个批次都不准」（讲义 ⑥-6.2）；
  - 判定边界移动：对 run B 的亲本，合并模型把边界从 k*_true 移到 k*_pool
    （低估错误 → 变异「看起来太丰富、不像错误」→ 被误判为 ASV），
    边界宽度倍数 ≈ 1.5×（合成参数）；居于此带的错误变异即假 ASV ——
    「后果是 ASV 数虚高」（讲义 ⑨-4）的机制；
  - 反向失真：对 run A，合并模型高估错误 → 真实变异被漏判（边界同样移动），
    合并学错误率双向失真。

参数：
  --q-bins      Q 值档位（默认 10 15 20 25 30 35 40）
  --n-per-bin   每个 Q 档的模拟观测数（默认 2000000；每个 run 一半）
  --frac-b      run B 的读段占比（默认 0.5）
  --offset-b    run B 的 Phred 偏移（默认 6，即 4× 错误率）
  --omega       DADA2 的 OMEGA_A（默认 1e-40）
  --scenario-q  判定情景的错配碱基 Q 值（默认 30）
  --parents     合成亲本队列数（默认 2000，对数均匀 1e3–1e7）
  --variants    每个亲本模拟的单碱基错误变异数（默认 30）
  --seed        随机种子（默认 20261104）

合成数据不得写成真实样本结果；真实 learnErrors 需集群 conda 环境 ngs_ms_microbiome
与真实 fastq（unverified）。只依赖 numpy + scipy；约 2–4 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch18_error_model_mixrun.py --selftest
"""
import argparse

import numpy as np
from scipy import stats


def true_rate(q, offset):
    return np.minimum(0.49, np.power(10.0, -(q - offset) / 10.0))


def learn_rates(q_bins, n_per_bin, frac_b, offset_b, seed):
    """模拟两个 run 的错误计数学习；返回 (learned_A, learned_B, learned_pool)。"""
    n_a = int(n_per_bin * (1.0 - frac_b))
    n_b = n_per_bin - n_a
    rng = np.random.default_rng(seed + 11)
    p_a, p_b = true_rate(q_bins, 0.0), true_rate(q_bins, offset_b)
    e_a = rng.binomial(n_a, p_a)
    e_b = rng.binomial(n_b, p_b)
    return e_a / n_a, e_b / n_b, (e_a + e_b) / (n_a + n_b), n_a, n_b


def k_boundary(n, p, omega):
    """k*(n, p)：使 P(Poisson(n·p) ≥ k) < omega 的最小 k（网格搜索，向上取足）。"""
    lam = n * p
    kmax = int(lam + 80.0 * np.sqrt(lam + 1.0)) + 2
    k = np.arange(1, kmax + 1)
    sf = stats.poisson.sf(k - 1, lam)
    hit = k[sf < omega]
    return int(hit[0]) if len(hit) else None


def run(q_bins, n_per_bin, frac_b, offset_b, omega, scenario_q,
        parents, variants, seed):
    q_bins = np.asarray(q_bins, dtype=float)
    la, lb, lp, n_a, n_b = learn_rates(q_bins, n_per_bin, frac_b, offset_b, seed)
    p_a, p_b = true_rate(q_bins, 0.0), true_rate(q_bins, offset_b)

    print("合成算例：两个测序 run，run B 比 run A 差 %d 个 Phred 档（≈ %.0f× 错误率）；"
          "每 Q 档 %d 次观测（run A %d / run B %d）" % (offset_b, 10 ** (offset_b / 10),
                                                   n_per_bin, n_a, n_b))
    print(f"OMEGA_A = {omega:g}（讲义 ④-4.2）；seed = {seed}\n")
    print(f"{'Q':>4} | {'p_A 真实':>10} | {'学A':>10} | {'p_B 真实':>10} | {'学B':>10} | "
          f"{'混学':>10} | {'混学/A':>7} | {'混学/B':>7}")
    print("-" * 88)
    for i, q in enumerate(q_bins):
        print(f"{q:>4.0f} | {p_a[i]:>10.2e} | {la[i]:>10.2e} | {p_b[i]:>10.2e} | "
              f"{lb[i]:>10.2e} | {lp[i]:>10.2e} | {lp[i]/p_a[i]:>7.2f} | {lp[i]/p_b[i]:>7.2f}")

    # 判定情景：单碱基错配，错配位 Q = scenario_q
    q0 = float(scenario_q)
    pA0, pB0 = true_rate(np.array([q0]), 0.0)[0], true_rate(np.array([q0]), offset_b)[0]
    p_pool0 = (1.0 - frac_b) * pA0 + frac_b * pB0     # 混学的期望错误率
    n_grid = np.array([1e3, 1e4, 1e5, 1e6])
    print(f"\n判定情景：单碱基错配，错配位 Q = {q0:.0f}（p_A = {pA0:.1e}、"
          f"p_B = {pB0:.1e}、混学期望 = {p_pool0:.1e}）")
    print("ASV/错误边界 k*（p_val < OMEGA_A 的最小变异拷贝数；None = 网格内不存在）：")
    print(f"{'亲本丰度 n':>12} | {'k*(runB 真实)':>14} | {'k*(混学)':>10} | "
          f"{'边界比 真/混':>10} | {'k*(runA 真实)':>14} | {'k*(混学)':>10}")
    bd = {}
    for n in n_grid:
        kb_t = k_boundary(n, pB0, omega)
        kb_p = k_boundary(n, p_pool0, omega)
        ka_t = k_boundary(n, pA0, omega)
        ka_p = k_boundary(n, p_pool0, omega)
        bd[n] = (kb_t, kb_p, ka_t, ka_p)
        ratio_b = kb_t / kb_p if (kb_t and kb_p) else float("nan")
        print(f"{n:>12.0e} | {kb_t!s:>14} | {kb_p!s:>10} | {ratio_b:>10.2f} | "
              f"{ka_t!s:>14} | {ka_p!s:>10}")
    print("判读：run B 的 k*(混学) < k*(真实) —— 错误率被低估 → 错误变异「看起来不像错误」"
          "→ 落入 [k*(混学), k*(真实)) 带的错误变异被误判为 ASV（ASV 数虚高，讲义 ⑨-4）；")
    print("run A 的 k*(混学) > k*(真实) —— 错误率被高估 → 真实变异被漏判。混学对两个"
          "批次方向相反地失真。")

    # 合成亲本队列：每个亲本的单碱基错误变异真实拷贝 K ~ Poisson(n·p_B)，
    # 数清「混学判 ASV / per-run 判 ASV」的数量差
    rng = np.random.default_rng(seed + 77)
    n_par = np.exp(rng.uniform(np.log(1e3), np.log(1e7), parents))
    lam = n_par * pB0
    kstar_pool = np.array([k_boundary(n, p_pool0, omega) for n in n_par])
    kstar_true = np.array([k_boundary(n, pB0, omega) for n in n_par])
    lam_eff = lam[kstar_pool > 0]
    kp = kstar_pool[kstar_pool > 0]
    kt = kstar_true[kstar_pool > 0]
    false_asv_pool, false_asv_true = 0, 0
    for lv, kpv, ktv in zip(np.array_split(lam_eff, 20),
                            np.array_split(kp, 20), np.array_split(kt, 20)):
        k_draw = rng.poisson(np.repeat(lv[:, None], variants, axis=1))
        false_asv_pool += int((k_draw >= kpv[:, None]).sum())
        false_asv_true += int((k_draw >= ktv[:, None]).sum())
    print(f"\n合成亲本队列（{parents} 个亲本 × {variants} 个单碱基错误变异，"
          f"变异真实拷贝 ~ Poisson(n·p_B)）：")
    print(f"  按 run B 真实模型判为 ASV 的错误变异：{false_asv_true}（应 ≈ 0）")
    print(f"  按混学模型判为 ASV 的错误变异：{false_asv_pool} —— 即「ASV 数虚高」的"
          "合成量级（两 run 谱差异设得较大以使机制可见；真实批次差异更微妙，方向相同）")
    print("真实数据对照（unverified）：PRJDB13364 跨 2017/2018/2019 三年，应按 run/年份"
          "分别 learnErrors 再 mergeSequenceTables（讲义 ⑨-4 Big Data 工作流）；"
          "error_model_F.png 中黑点不随 Q 下降即为混学症状（讲义 ⑥-6.2）。")
    return dict(la=la, lb=lb, lp=lp, p_a=p_a, p_b=p_b,
                p_pool0=p_pool0, pA0=pA0, pB0=pB0, bd=bd,
                false_pool=false_asv_pool, false_true=false_asv_true)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--q-bins", type=float, nargs="+",
                    default=[10, 15, 20, 25, 30, 35, 40])
    ap.add_argument("--n-per-bin", type=int, default=2000000)
    ap.add_argument("--frac-b", type=float, default=0.5)
    ap.add_argument("--offset-b", type=float, default=6.0)
    ap.add_argument("--omega", type=float, default=1e-40)
    ap.add_argument("--scenario-q", type=float, default=30.0)
    ap.add_argument("--parents", type=int, default=2000)
    ap.add_argument("--variants", type=int, default=30)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    r = run(args.q_bins, args.n_per_bin, args.frac_b, args.offset_b, args.omega,
            args.scenario_q, args.parents, args.variants, args.seed)

    if args.selftest:
        q_bins = np.asarray(args.q_bins, dtype=float)
        mid = q_bins >= 25
        ratio_a = r["p_pool0"] / r["pA0"]
        ratio_b = r["p_pool0"] / r["pB0"]
        band_ok = all(kb_t and kb_p and kb_t > kb_p
                      for kb_t, kb_p, _, _ in r["bd"].values())
        checks = [
            ("per-run 学习还原 run A 谱（Q≥25 档偏差 < 6%）",
             bool(np.max(np.abs(r["la"][mid] / r["p_a"][mid] - 1.0)) < 0.06)),
            ("per-run 学习还原 run B 谱（Q≥25 档偏差 < 6%）",
             bool(np.max(np.abs(r["lb"][mid] / r["p_b"][mid] - 1.0)) < 0.06)),
            (f"混学对 run B 低估（混学/B = {ratio_b:.3f} ∈ [0.55, 0.70]）",
             0.55 <= ratio_b <= 0.70),
            (f"混学对 run A 高估（混学/A = {ratio_a:.2f} ≥ 2.0）", ratio_a >= 2.0),
            ("混学谱在 scenario-q 处与学习谱一致（蒙特卡洛噪声内）",
             abs(r["lp"][list(q_bins).index(args.scenario_q)] / r["p_pool0"] - 1.0) < 0.03),
            ("run B 的 ASV 边界在混学下整体左移（全部 n 格 k*_混学 < k*_真实）", band_ok),
            (f"混学把错误变异误判为 ASV（{r['false_pool']} 个），"
             f"per-run 模型 ≈ 0（实际 {r['false_true']} 个）",
             r["false_pool"] >= 100 * max(r["false_true"], 1)),
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

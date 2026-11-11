#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch22_mnar_mar_imputation.py — 缺失机制错配的杀伤链：MNAR 用均值填补制造假阴性，
MAR 用 min/5 填补制造假阳性（合成算例）

服务于：教材第 22 章（多组学整合分析）§22.4 概念与方法（缺失机制与填补决策）、
§22.5 失效条件第 2 条（MNAR 缺失用 MAR 方法填补制造假信号），对应讲义 p06
§4.3（MNAR/MAR/MCAR 决策矩阵、算法错配的假阳性与假阴性杀伤链）、
⑤5.2 与 06_metabolome_preprocess.R（QC-RSD → 缺失率切除 → 机制诊断 →
按机制填补：MNAR 用观测值低分位数/5、MAR/MCAR 用行中位数）。

合成设定（不基于任何真实样本；每次模拟独立种子可复现）：
  部分 A（假阴性链）：某特征对照组 ~ N(6, 0.5²)、处理组 ~ N(4, 0.5²)（真实下调），
    检出限 LOD=4.5 → 处理组低于 LOD 的值记为缺失（低于检测限的 MNAR，
    合成设定下全矩阵缺失率约 40%）。比较三种分析：
    完整数据（参照）、均值填补（把 MAR 方法错配到 MNAR）、
    左截断填补（观测值 20% 分位数 / 5，脚本 --mnar-quantile 0.2 口径）。
    统计 4000 次模拟中「完整数据 p<0.05 但填补后 p≥0.05」的真阳性被抹杀比例。
  部分 B（假阳性链）：特征 X 的 5 个样本因离子抑制失谐缺失（MAR 物理机理），
    min/5 填补把缺失样本压到远低于数据主体（观测最小值/5）；
    200 个伙伴特征中一半恰在这 5 个样本真实偏高（共享样本来源结构，+1.2 SD）。
    比较 min/5 与行中位数填补下，X 与「偏高伙伴」的平均相关、
    以及 1500 次模拟中出现 |r|>0.8 假边的比例。
  部分 C（机制诊断）：300 个特征的缺失率随检出强度单调上升（MNAR 主导），
    复算 06_metabolome_preprocess.R 打印的 Spearman(缺失率, 平均 log2 强度)。

正文引用的输出（手算可对）：
  - 均值填补抹杀约七成真阳性（假阴性链），左截断填补基本不抹杀；
  - min/5 与「失谐样本偏高的特征」系统性强负相关（行中位数填补无此现象），
    近半数模拟伪造出 |r|>0.8 的强假边（假阳性链）；
  - 缺失率 ~ 检出强度 Spearman ≈ −0.9（MNAR 主导的诊断形态）。

参数：
  --n-per-group   每组样本数（默认 10）
  --lod           合成检出限（默认 4.5）
  --n-sim-a       部分 A 模拟次数（默认 4000）
  --n-sim-b       部分 B 模拟次数（默认 1500）
  --n-partners    部分 B 伙伴特征数（默认 200）
  --seed          随机种子基准（默认 20261105）

合成数据不得写成真实样本结果。只依赖 numpy/scipy；约 3 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch22_mnar_mar_imputation.py --selftest
"""
import argparse

import numpy as np
from scipy import stats


def corr_one_vs_many(x, Y):
    xc = x - x.mean()
    Yc = Y - Y.mean(axis=1, keepdims=True)
    return Yc @ xc / np.sqrt((xc @ xc) * (Yc * Yc).sum(axis=1))


def part_a(n_per_group, lod, n_sim, seed):
    """Welch t 检验的 numpy 向量化实现（与 scipy.stats.ttest_ind 同式）。"""
    def welch_p(x0, x1):
        m0, m1 = x0.mean(), x1.mean()
        v0, v1 = x0.var(ddof=1), x1.var(ddof=1)
        t = (m0 - m1) / np.sqrt(v0 / len(x0) + v1 / len(x1))
        df = (v0 / len(x0) + v1 / len(x1)) ** 2 / (
            (v0 / len(x0)) ** 2 / (len(x0) - 1) +
            (v1 / len(x1)) ** 2 / (len(x1) - 1))
        return 2.0 * stats.t.sf(np.abs(t), df)

    killed_mean, killed_lc, n_sig_full, miss_rates = 0, 0, 0, []
    for s in range(n_sim):
        r = np.random.default_rng(seed + 1000 + s)
        ctrl = r.normal(6.0, 0.5, n_per_group)
        trt = r.normal(4.0, 0.5, n_per_group)
        x = np.concatenate([ctrl, trt])
        g = np.array([0] * n_per_group + [1] * n_per_group)
        obs = x.copy()
        obs[(g == 1) & (x < lod)] = np.nan
        miss_rates.append(float(np.isnan(obs).mean()))
        with np.errstate(invalid="ignore", divide="ignore"):
            p_full = welch_p(ctrl, trt)
            imp_mean = np.where(np.isnan(obs), np.nanmean(obs), obs)
            p_mean = welch_p(imp_mean[g == 0], imp_mean[g == 1])
            q20 = np.nanquantile(obs, 0.2) / 5.0
            imp_lc = np.where(np.isnan(obs), q20, obs)
            p_lc = welch_p(imp_lc[g == 0], imp_lc[g == 1])
        n_sig_full += p_full < 0.05
        killed_mean += (p_full < 0.05) and (p_mean >= 0.05)
        killed_lc += (p_full < 0.05) and (p_lc >= 0.05)
    return dict(kill_mean=killed_mean / n_sim, kill_lc=killed_lc / n_sim,
                frac_sig=n_sig_full / n_sim, miss=float(np.mean(miss_rates)))


def part_b(n, n_partners, n_sim, seed):
    miss_idx = np.array([2, 5, 7, 11, 18])[:max(1, n // 4)]  # 离子抑制失谐样本
    r_mean_min5, r_mean_med, n_r08, = [], [], []
    for s in range(n_sim):
        r = np.random.default_rng(seed + 5000 + s)
        X = r.normal(100.0, 10.0, n)
        Y = r.normal(50.0, 5.0, (n_partners, n))
        bumped = np.arange(n_partners // 2, n_partners)
        Y[np.ix_(bumped, miss_idx)] += 1.2 * 5.0  # 这批样本真实偏高 1.2 SD
        obs = np.delete(X, miss_idx)
        x_min5 = X.copy()
        x_min5[miss_idx] = obs.min() / 5.0     # ≈14，远离数据主体（~100）
        x_med = X.copy()
        x_med[miss_idx] = np.median(obs)
        r5 = corr_one_vs_many(x_min5, Y)
        rm = corr_one_vs_many(x_med, Y)
        r_mean_min5.append(float(r5[n_partners // 2:].mean()))
        r_mean_med.append(float(rm[n_partners // 2:].mean()))
        n_r08.append(int((np.abs(r5) > 0.8).sum()))
    n_r08 = np.array(n_r08)
    return dict(r_min5=float(np.mean(r_mean_min5)), r_med=float(np.mean(r_mean_med)),
                frac_r08=float(np.mean(n_r08 > 0)), mean_r08=float(np.mean(n_r08)))


def part_c(seed):
    r = np.random.default_rng(seed + 9)
    n_feat, n = 300, 15
    mean_int = r.uniform(3.0, 12.0, n_feat)
    p_miss = np.clip(0.9 - 0.08 * mean_int, 0.02, 0.9)  # 越低越易缺失（MNAR）
    obs = np.array([r.normal(m, 0.3, n) for m in mean_int])
    mask = r.random(obs.shape) < p_miss[:, None]
    mr = mask.mean(axis=1)
    rho = stats.spearmanr(mr, mean_int)
    return dict(rho=float(rho.statistic), pval=float(rho.pvalue))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n-per-group", type=int, default=10)
    ap.add_argument("--lod", type=float, default=4.5)
    ap.add_argument("--n-sim-a", type=int, default=4000)
    ap.add_argument("--n-sim-b", type=int, default=1500)
    ap.add_argument("--n-partners", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    a = part_a(args.n_per_group, args.lod, args.n_sim_a, args.seed)
    n = 2 * args.n_per_group
    b = part_b(n, args.n_partners, args.n_sim_b, args.seed)
    c = part_c(args.seed)

    print("合成算例（不基于任何真实样本）")
    print()
    print(f"部分 A 假阴性链（MNAR 特征：真实下调，LOD={args.lod} 下缺失率 {a['miss']:.0%}，"
          f"{args.n_sim_a} 次模拟）")
    print(f"  完整数据检出 p<0.05 的比例            : {a['frac_sig']:.3f}（参照）")
    print(f"  真阳性被均值填补抹杀的比例            : {a['kill_mean']:.3f}"
          f" ← MAR 方法错配到 MNAR（假阴性）")
    print(f"  真阳性被 q20/5 左截断填补抹杀的比例   : {a['kill_lc']:.3f}"
          f" ← 脚本 --mnar-quantile 0.2 口径")
    print()
    print(f"部分 B 假阳性链（MAR：5/{n} 样本离子抑制失谐；"
          f"{args.n_partners // 2} 个伙伴在失谐样本真实偏高，{args.n_sim_b} 次模拟）")
    print(f"  X × 偏高伙伴 平均 r（min/5 填补）  : {b['r_min5']:+.3f} ← 系统性假负相关")
    print(f"  X × 偏高伙伴 平均 r（行中位数填补）: {b['r_med']:+.3f} ← 无系统信号")
    print(f"  ≥1 条 |r|>0.8 强假边的模拟比例      : {b['frac_r08']:.3f}"
          f"（平均 {b['mean_r08']:.2f} 条/次）")
    print()
    print(f"部分 C 机制诊断（{300} 特征，MNAR 主导合成数据）")
    print(f"  Spearman(缺失率, 检出强度) = {c['rho']:+.3f}（p={c['pval']:.1e}；"
          f"明显为负即 MNAR 主导，脚本打印同一统计量）")

    if args.selftest:
        checks = [
            (f"均值填补抹杀真阳性比例 {a['kill_mean']:.3f} > 0.5（假阴性链）",
             a["kill_mean"] > 0.5),
            (f"左截断填补抹杀比例 {a['kill_lc']:.3f} < 0.05",
             a["kill_lc"] < 0.05),
            (f"min/5 与偏高伙伴系统负相关 {b['r_min5']:+.3f} < -0.3",
             b["r_min5"] < -0.3),
            (f"行中位数填补无系统信号 {abs(b['r_med']):.3f} < 0.05",
             abs(b["r_med"]) < 0.05),
            (f"min/5 伪造 |r|>0.8 强边 {b['frac_r08']:.0%} > 25%（假阳性链）",
             b["frac_r08"] > 0.25),
            (f"诊断散点 Spearman {c['rho']:+.3f} ≤ −0.8（MNAR 主导形态）",
             c["rho"] <= -0.8),
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

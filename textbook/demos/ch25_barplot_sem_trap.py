#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch25_barplot_sem_trap.py — 柱状图 + SEM 的视觉陷阱：同一张柱头图，三种截然不同的数据（设例）

服务于：教材第 25 章（课题设计与图表叙事）§25.5 失效条件第 1 条
「图与要支持的论点不对应」的机制演示，对应讲义 p08 §4.3 反模式 1
（炸药图：均值与 SEM 对分布形态完全不敏感，Weissgerber et al. 2015）、
§4.5 审稿人防御点 2（n ≤ 10 时隐瞒原始散点）与点 6（视觉欺诈式修饰），
并为 §⑩-2 习题「2.3 倍 + 误差棒不重叠 + p < 0.01 该怎么质询」提供量化的数据原型。

本演示是确定性构造的设例（不消耗随机数、无需种子；三组数据可手算复核）：
  对照组 C（n=6）：[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
  场景 A（全体一致响应）：每点 +1.0 —— 「药物在全部受试者中稳定起效」
  场景 B（半数响应）：3 点不变、3 点 +2.0 —— 「仅半数响应，响应者效应反而更强」
  场景 C（单点拉动均值）：5 点 +0.2、1 点 +3.2 —— 「均值差主要来自一个点」

正文引用的输出：
  - 三个场景的处理组均值完全相同（A、B 精确相等，1.5 = 对照的 3.0 倍；
    C 为 1.2 = 2.4 倍）而显著性结论相反（A 显著，B、C 均不显著）——
    柱头图只能画 (mean, SEM)，画不出「在谁身上有效」，失效条件 1 的量化形态；
  - 场景 C 中最大值单个点贡献均值差的 71%（n=6 时 1 个点 = 16.7% 的样本），
    即审稿人点 2「n ≤ 10 必须展示原始散点」的数量级论据；
  - 每个场景打印 mean / SD / SEM / Welch t / Mann-Whitney，供正文表格引用。

参数：--alpha（判定阈值，默认 0.05）
合成数据不得写成真实样本结果。只依赖 numpy + scipy；约 0.1 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch25_barplot_sem_trap.py --selftest
"""
import argparse

import numpy as np
from scipy import stats

CONTROL = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
SCENARIOS = {
    "A 全体一致响应": CONTROL + 1.0,
    "B 半数响应": np.concatenate([CONTROL[:3], CONTROL[3:] + 2.0]),
    "C 单点拉动均值": np.array([0.2, 0.4, 0.6, 0.8, 1.0, 4.2]),
}


def summarize(name, treat, control, alpha):
    mean_t, mean_c = treat.mean(), control.mean()
    sd_t = treat.std(ddof=1)
    sem_t = sd_t / np.sqrt(len(treat))
    t_stat, p_t = stats.ttest_ind(treat, control, equal_var=False)
    u_stat, p_mw = stats.mannwhitneyu(treat, control, alternative="two-sided")
    ratio = mean_t / mean_c
    print(f"{name}")
    print(f"  处理组数据：{np.array2string(treat, precision=1, separator=', ')}")
    print(f"  均值 = {mean_t:.3f}（对照 {mean_c:.3f} 的 {ratio:.2f}×）  "
          f"SD = {sd_t:.3f}  SEM = {sem_t:.3f}")
    print(f"  Welch t p = {p_t:.4f}   Mann-Whitney p = {p_mw:.4f}"
          f"   → α = {alpha} 下 {'显著' if p_t < alpha else '不显著'}")
    return dict(name=name, mean=mean_t, sd=sd_t, sem=sem_t,
                p_t=float(p_t), p_mw=float(p_mw), ratio=ratio)


def run(alpha):
    print("设例（确定性构造，可手算复核）：对照组 n=6，三个处理组形态完全不同\n")
    res = {name: summarize(name, treat, CONTROL, alpha)
           for name, treat in SCENARIOS.items()}
    a, b, c = res["A 全体一致响应"], res["B 半数响应"], res["C 单点拉动均值"]
    print("\n柱头图视角：柱高 3.0× / 3.0× / 2.4×，看起来「都是上调」；"
          "但均值差的构成完全不同——")
    print("  A：6/6 个点各贡献 1.0；B：3/6 个点贡献 2.0、3/6 贡献 0；"
          "C：最大值单点贡献 71%")
    contrib_c = (c["mean"] - CONTROL.mean()
                 - (np.sort(SCENARIOS["C 单点拉动均值"])[:-1].mean()
                    - np.sort(CONTROL)[:-1].mean()))
    diff_c = c["mean"] - CONTROL.mean()
    print(f"  C 的均值差 {diff_c:.2f} 中，最大值单点贡献 {contrib_c:.2f} "
          f"（{contrib_c / diff_c:.0%}）")
    print("\n判读：柱头图 + SEM 无法承载「在谁身上有效」的论点；"
          "n = 6 时必须展示原始散点（审稿人点 2），"
          "否则会把手感不错的 B/C 场景写成 A 场景式的结论句。")
    return res, contrib_c / diff_c


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--alpha", type=float, default=0.05,
                    help="显著性判定阈值（默认 0.05）")
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    res, max_contrib = run(args.alpha)
    a = res["A 全体一致响应"]
    b = res["B 半数响应"]
    c = res["C 单点拉动均值"]

    if args.selftest:
        checks = [
            (f"A、B 均值精确相等（{a['mean']:.3f} vs {b['mean']:.3f}，柱高相同）",
             abs(a["mean"] - b["mean"]) < 1e-12),
            (f"A 显著（Welch p = {a['p_t']:.4f} < {args.alpha}）",
             a["p_t"] < args.alpha),
            (f"B 不显著（Welch p = {b['p_t']:.4f} > 0.1）", b["p_t"] > 0.1),
            (f"C 不显著（Welch p = {c['p_t']:.4f} > 0.1）", c["p_t"] > 0.1),
            (f"C 最大值单点贡献均值差 > 50%（实际 {max_contrib:.0%}）",
             max_contrib > 0.5),
        ]
        print("\n[selftest]")
        npass = sum(pass_ for _, pass_ in checks)
        for name, passed in checks:
            print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        print(f"{npass}/{len(checks)} PASS")
        if npass != len(checks):
            raise SystemExit(1)


if __name__ == "__main__":
    main()

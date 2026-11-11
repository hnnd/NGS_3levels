#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch11_pan_rarefaction.py — 合成基因存在/缺失矩阵上的泛基因组与核心基因
稀释曲线 + Heaps 定律拟合：「开放/封闭」是采样与选株的产物（合成算例）

服务章节：第 11 章 §11.4 泛基因组结构与稀释曲线小节、§11.5 失效条件第 3 条
（稀释曲线是否「开放」依赖采样深度与菌株选择，不是物种固有属性）。

数据性质：【合成算例】存在/缺失矩阵由固定种子的 Beta-伯努利模型生成，
与任何真实菌株无关；输出不得写成真实样本（如 Xoo PRJEB100987 完成图）的
实测结果。本课贯穿面板的真实稀释曲线需在集群跑 Roary/OrthoFinder 后
另行登记（unverified）。

模型简化（文件头声明）：真实基因获得/丢失用「每家族一个跨株共享的出现概率
p_f ~ Beta(a,b)，株级独立伯努利抽样」近似——它保留了「共享稀有家族 + 株特异
家族」这两个与结论相关的结构，省略了基因组重排与水平转移的细节。

正文引用的输出：
  - 开放/封闭两组合成参数下 pan(N)、core(N) 中位数曲线（N=1..n）
  - Heaps 拟合 P(N)=κ·N^γ 的 γ 与 α=1−γ（log-log 最小二乘）
  - 同一生成过程、不同选株面板（同簇 12 株 / 混簇 12 株 / 全部 24 株）的 γ 差异
    → 菌株选择改变「开放/封闭」判定
  - 小样本错觉：封闭组在 N≤6 时 pan 曲线仍在陡升
  - 核心占比随 N 下降（小样本核心虚高，呼应 u08 讲义 ⑥6.5 的统计效应提醒）

参数含义：
  --n-strains      面板菌株数 n（默认 24）
  --draws          每个 N 的无放回抽样次数（取中位数）
  --seed           随机种子（固定，保证可复现）
  --selftest       断言上述正文引用数字
"""
import argparse
import sys

import numpy as np

# 开放/封闭两组合成参数：(共享池大小, Beta(a,b), 株特异基因泊松强度)
# 开放组：大家族池 + 重尾出现概率（多数家族只零星出现）+ 每株大量新基因
OPEN = dict(pool=5000, beta=(0.25, 2.5), lam_unique=90.0, clade_pool=3500)
# 封闭组：中小家族池 + 偏稀有出现概率（先升后平——才有「小样本误判开放」的空间）
# + 每株极少新基因
CLOSED = dict(pool=1500, beta=(1.2, 3.5), lam_unique=4.0, clade_pool=0)


CLADE_FACTOR = 0.35


def simulate_panel(rng, n_strains, params, two_clades=False, seed_tag=""):
    """生成存在/缺失矩阵：行=基因家族，列=菌株。返回 (matrix, n_core)。

    two_clades=True 时后 half 株属于「远簇」：它们除了共享池打折外，
    还独占一个簇特异家族池（模拟亚群内部的水平转移与适应基因）。
    """
    n_core = 2600
    blocks = [np.ones((n_core, n_strains), dtype=bool)]  # 核心家族：株株皆有
    half = n_strains // 2
    p = rng.beta(params["beta"][0], params["beta"][1], size=params["pool"])
    acc = rng.random((params["pool"], n_strains)) < p[:, None]
    if two_clades:  # 远簇菌株少见共享池家族
        acc[:, half:] = rng.random((params["pool"], n_strains - half)) \
            < (p[:, None] * CLADE_FACTOR)
    blocks.append(acc)
    if two_clades and params["clade_pool"]:
        p2 = rng.beta(0.3, 2.0, size=params["clade_pool"])
        clade = rng.random((params["clade_pool"], n_strains - half)) < p2[:, None]
        blocks.append(np.hstack([np.zeros((params["clade_pool"], half),
                                          dtype=bool), clade]))
    for i in range(n_strains):  # 株特异真实家族（模拟水平转移/噬菌体新获）
        c = rng.poisson(params["lam_unique"])
        if c:
            m = np.zeros((int(c), n_strains), dtype=bool)
            m[:, i] = True
            blocks.append(m)
    mat = np.vstack(blocks)
    print(f"[{seed_tag}] 合成面板 n={n_strains}：核心家族 {n_core}，共享池家族 "
          f"{params['pool']}（p~Beta{params['beta']}），株特异 ~"
          f"Pois({params['lam_unique']})/株"
          + (f"，远簇另占簇特异池 {params['clade_pool']} 家族"
             if two_clades and params["clade_pool"] else ""))
    print(f"  矩阵规模 {mat.shape[0]} 家族 × {mat.shape[1]} 株；"
          f"总泛基因组 {mat.shape[0]} 家族")
    return mat, n_core


def rarefaction(mat, draws, rng):
    """对每个 N 无放回抽 draws 个菌株子集，返回 pan/core 中位数曲线。"""
    n = mat.shape[1]
    pan = np.zeros(n + 1)
    core = np.zeros(n + 1)
    for n_samp in range(1, n + 1):
        pans = np.empty(draws)
        cores = np.empty(draws)
        for d in range(draws):
            idx = rng.choice(n, size=n_samp, replace=False)
            sub = mat[:, idx]
            pans[d] = sub.any(axis=1).sum()
            cores[d] = sub.all(axis=1).sum()
        pan[n_samp] = np.median(pans)
        core[n_samp] = np.median(cores)
    return pan, core


def heaps_fit(pan, n, skip_first=1):
    """log-log 最小二乘拟合 P(N)=κ·N^γ；返回 (kappa, gamma, alpha)。"""
    ns = np.arange(skip_first + 1, n + 1, dtype=float)
    ps = pan[skip_first + 1:n + 1]
    gamma, log_k = np.polyfit(np.log(ns), np.log(ps), 1)
    return float(np.exp(log_k)), float(gamma), float(1.0 - gamma)


def report_panel(name, mat, pan, core, n, n_core):
    kappa, gamma, alpha = heaps_fit(pan, n)
    core_frac_n = core[n] / pan[n]
    core_frac_4 = core[4] / pan[4]
    inc_last5 = np.median(np.diff(pan[n - 4:n + 1]))
    print(f"  [{name}] pan({n})={pan[n]:.0f} core({n})={core[n]:.0f} "
          f"核心占比 core/pan：N=4 时 {core_frac_4:.1%} → N={n} 时 {core_frac_n:.1%}")
    print(f"  [{name}] Heaps 拟合 P(N)=κ·N^γ：κ={kappa:.0f} γ={gamma:.3f} "
          f"α=1−γ={alpha:.3f}；末 5 个 N 的 pan 增量中位数 {inc_last5:.0f} 家族/株")
    verdict = "开放倾向（γ 明显 >0）" if gamma > 0.2 else \
              ("封闭倾向（γ≈0）" if gamma < 0.1 else "过渡带（0.1≤γ≤0.2）")
    print(f"  [{name}] 按本合成演示判据：{verdict}")
    return dict(gamma=gamma, alpha=alpha, pan_n=pan[n], core_n=core[n],
                core_frac_n=core_frac_n, core_frac_4=core_frac_4,
                inc_last5=inc_last5, pan=pan, core=core)


def selftest():
    """固定种子复现正文引用的关键数字。"""
    print("=== SELFTEST（合成算例，固定种子 20261104）===")
    rng = np.random.default_rng(20261104)
    open_mat, _ = simulate_panel(rng, 24, OPEN, two_clades=True, seed_tag="开放组")
    open_r = rarefaction(open_mat, 200, rng)
    res_open = report_panel("开放·全部 24 株", open_mat, *open_r, 24, 2600)

    closed_mat, _ = simulate_panel(rng, 24, CLOSED, two_clades=False, seed_tag="封闭组")
    closed_r = rarefaction(closed_mat, 200, rng)
    res_closed = report_panel("封闭·全部 24 株", closed_mat, *closed_r, 24, 2600)

    # 选株效应：同一生成过程，同簇 12 株 vs 全部 24 株
    clade_only = open_mat[:, :12]
    res_clade = report_panel("开放·仅近簇 12 株", clade_only,
                             *rarefaction(clade_only, 200, rng), 12, 2600)
    mixed = np.hstack([open_mat[:, :6], open_mat[:, 12:18]])
    res_mixed = report_panel("开放·混簇 12 株", mixed,
                             *rarefaction(mixed, 200, rng), 12, 2600)

    # 断言：开放/封闭可区分（γ 分离 + 后半程增长对比——「平台」判据）
    assert res_open["gamma"] > 0.25, f"开放组 γ 应 >0.25，得 {res_open['gamma']:.3f}"
    assert res_closed["gamma"] < 0.12, f"封闭组 γ 应 <0.12，得 {res_closed['gamma']:.3f}"
    assert res_open["gamma"] > res_closed["gamma"] + 0.15
    grow_open = (res_open["pan_n"] - res_open["pan"][12]) / res_open["pan_n"]
    grow_closed = (res_closed["pan_n"] - res_closed["pan"][12]) / res_closed["pan_n"]
    assert grow_open > 0.18 and grow_closed < 0.08, \
        f"后半程（N>12）相对增长：开放 {grow_open:.1%} 应大，封闭 {grow_closed:.1%} 应≈0"
    # 断言：选株改变判定
    assert res_mixed["gamma"] > res_clade["gamma"] + 0.05, \
        f"混簇 γ({res_mixed['gamma']:.3f}) 应明显高于近簇 γ({res_clade['gamma']:.3f})"
    assert res_mixed["pan_n"] > res_clade["pan_n"] + 800, \
        f"混簇 pan(12)={res_mixed['pan_n']:.0f} 应明显大于近簇 {res_clade['pan_n']:.0f}"
    # 断言：小样本核心虚高
    assert res_open["core_frac_4"] > res_open["core_frac_n"] + 0.05
    # 断言：小样本错觉——N≤6 的 γ 估计把封闭组读成更开放
    _, g_closed_small, _ = heaps_fit(res_closed["pan"], 6)
    assert g_closed_small > res_closed["gamma"] + 0.015, (
        f"N≤6 的 γ 估计 {g_closed_small:.3f} 应高于全曲线 "
        f"{res_closed['gamma']:.3f}——小样本拟合高估开放性")
    # 断言：核心曲线随 N 单调不增（稀释的本质）
    assert np.all(np.diff(res_open["core"][1:]) <= 0)
    print(f"  [后半程增长核查] N>12 的相对增长：开放 {grow_open:.1%} vs 封闭 "
          f"{grow_closed:.1%}——平台是否出现是『能不能下结论』的直接判据")
    print(f"  [小样本错觉核查] 封闭组只用 N≤6 拟合 γ={g_closed_small:.3f}，"
          f"全曲线 γ={res_closed['gamma']:.3f}——小样本拟合高估开放性")
    print("SELFTEST PASS：开放/封闭 γ 分离、选株改变 γ 与 pan、核心占比随 N 下降、"
          "N≤6 的 γ 高估开放性（小样本错觉）均复现")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="合成泛基因组稀释曲线与 Heaps 拟合（合成算例，非真实样本结果）")
    ap.add_argument("--n-strains", type=int, default=24)
    ap.add_argument("--draws", type=int, default=200, help="每个 N 的抽样次数")
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    rng = np.random.default_rng(args.seed)
    for label, params in [("开放组", OPEN), ("封闭组", CLOSED)]:
        mat, n_core = simulate_panel(rng, args.n_strains, params,
                                     two_clades=True, seed_tag=label)
        report_panel(f"{label}·全部 {args.n_strains} 株", mat,
                     *rarefaction(mat, args.draws, rng), args.n_strains, n_core)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

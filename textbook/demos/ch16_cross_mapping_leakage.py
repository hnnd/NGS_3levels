#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch16_cross_mapping_leakage.py — 双 RNA-seq 读段拆分：分别比对（顺序归属 / 双向重复计数）
vs 合并参考竞争性比对，保守同源区读段的错配量级（合成算例）

服务章节：第 16 章 §16.4 概念与方法（拆分策略）、§16.5 失效条件第 1 条
（分别比对时保守区读段被两个物种重复计数；合并参考竞争比对才能分配歧义读段）。
源讲义：p03 §4.2（拆分策略对照表）、§4.3（交叉比对归属的不对称放大）、§4.9（歧义
read 的三种归宿）。DE/LRT 模型本身属第 14 章，本脚本只演示拆分阶段的几何量级。

模型（全部为合成玩具模型，非任何真实样本结果）：
  * 两个合成「基因组」：宿主与病原。各物种中比例为 c 的基因属跨物种保守家族
    （核糖体蛋白、肌动蛋白、热休克蛋白一类的假想物），序列近乎相同，
    来自它们的读段能同时比对上两个参考（歧义 read）；其余读段只比对来源物种。
  * p = 病原读段占文库的真实比例（合成设定，如 0.5% = 侵染早期）。
  * 三种拆分规则（对应讲义 §4.2 表格与 §4.9 三种归宿）：
      naive_dual       两个物种矩阵各自独立计下所有能比对上的 read
                       （分别比对后不做任何去重/交集）→ 歧义 read 双侧重复计数；
      sequential_host  顺序级联过滤：先比宿主，命中即定，剩下再比病原
                       （宿主先比，偏袒宿主）→ 病原保守 read 被宿主吞掉，且不留痕迹；
      competitive      合并参考竞争性比对 + 唯一比对过滤（STAR --outFilterMultimapNmax 1
                       或 Salmon 选择性联配的去歧义口径）→ 歧义 read 双侧对称剔除，
                       以 multimap 比例显式披露。
  * 闭式（手算规则）：设 c = 保守家族读段占比，p = 病原真实占比，则
      naive_dual 病原侧虚增 = c(1-p)/p；宿主侧虚增 = cp/(1-p)（可忽略）；
      sequential  病原侧缺失比例 = c（被先比的宿主吞掉）；
      competitive 两侧各损失 c（对称、可披露）。
    讲义 §4.3 的数字（c = ε = 0.1%、p = 0.5% → 19.9%；p = 30% → 0.23%）即
    naive_dual 虚增公式在 ε 口径下的取值，本脚本逐位复现。

参数（--help 可见）：
  --c              保守家族读段占比（默认 0.001 = 0.1%，对齐讲义 §4.3 的 ε）
  --n-reads        模拟读段数（默认 2_000_000）
  --seed           随机种子（默认 20261104）
  --selftest       断言闭式公式与讲义数字、模拟与闭式一致

正文引用的输出：
  - 三规则闭式对照表（病原/宿主侧虚增或缺失百分比，随 p = 0.5%→30%）
  - 讲义 §4.3 两个印刷数 19.9% / 0.23% 的复现（手算规则入口）
  - 「恒定渗漏率在时序上伪造出保守基因持续下调曲线」的定量演示
    （naive_dual 虚增 19.9% → 0.23%，表观倍数变化 ≈ 5 倍假下调）
  - 模拟实现值与闭式的一致性（selftest 断言）

依赖：Python 标准库 + numpy（scipy 不使用）。
合成算例：所有「读段」均为随机数生成器产物，与任何真实菌株、真实样本无关。
"""
import argparse
import sys

import numpy as np

SEED = 20261104


def closed_form(c, p):
    """三种拆分规则的闭式结果（返回值均为相对真值的偏差比例）。"""
    return {
        # 病原矩阵 = pN + c(1-p)N（宿主保守 read 也落进病原矩阵）→ 虚增 c(1-p)/p
        "naive_dual_path": c * (1.0 - p) / p,
        # 宿主矩阵 = (1-p)N + cpN → 虚增 cp/(1-p)
        "naive_dual_host": c * p / (1.0 - p),
        # 病原保守 read 被先比的宿主吞掉：病原只剩 p(1-c)N → 缺失 c
        "sequential_path_lost": c,
        # 竞争性唯一比对：歧义 read 双侧对称剔除，各损失 c
        "competitive_both_lost": c,
    }


def simulate(c, p, n_reads, seed):
    """按三规则模拟读段归属，返回各规则下宿主/病原矩阵计数与真值。"""
    rng = np.random.default_rng(seed)
    origin_path = rng.random(n_reads) < p          # 读段真实来源（病原 = True）
    # 每个物种内部：比例 c 的读段来自跨物种保守家族（歧义）
    conserved = rng.random(n_reads) < c
    ambiguous = conserved                          # 保守 read 两参考都能比对
    n_path_true = int(origin_path.sum())
    n_host_true = n_reads - n_path_true

    # naive_dual：歧义 read 在两侧矩阵各计一次
    host_naive = n_host_true + int((ambiguous & origin_path).sum())
    path_naive = n_path_true + int((ambiguous & ~origin_path).sum())
    # sequential（宿主先比）：歧义 read 归宿主；病原只拿到非歧义的病原 read
    host_seq = n_host_true + int((ambiguous & origin_path).sum())
    path_seq = int((~ambiguous & origin_path).sum())
    # competitive 唯一比对：歧义 read 双侧剔除
    host_comp = int((~ambiguous & ~origin_path).sum())
    path_comp = int((~ambiguous & origin_path).sum())
    return dict(host_true=n_host_true, path_true=n_path_true,
                host_naive=host_naive, path_naive=path_naive,
                host_seq=host_seq, path_seq=path_seq,
                host_comp=host_comp, path_comp=path_comp)


def main():
    ap = argparse.ArgumentParser(
        description="双 RNA-seq 拆分策略的保守区读段错配量级（合成算例；服务第 16 章 "
                    "失效条件 1，对齐讲义 p03 §4.2–4.3、§4.9）")
    ap.add_argument("--c", type=float, default=0.001,
                    help="保守家族读段占比（默认 0.001 = 0.1％，对齐讲义 §4.3 的 ε）")
    ap.add_argument("--n-reads", type=int, default=2_000_000,
                    help="模拟读段数（默认 200 万）")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    c, p_grid = args.c, [0.005, 0.02, 0.10, 0.30]

    # ---------------- Part 0：闭式（手算规则） ----------------
    print("=" * 78)
    print(f"[Part 0 · 手算规则] 保守读段占比 c = {c:.4%}；虚增/缺失均为相对真值的比例")
    print("=" * 78)
    print(f"{'病原真实占比 p':>12} | {'naive 病原虚增':>13} {'naive 宿主虚增':>13} | "
          f"{'顺序(宿主先) 病原缺失':>18} {'竞争性双侧剔除':>13}")
    for p in p_grid:
        cf = closed_form(c, p)
        print(f"{p:>11.1%} | {cf['naive_dual_path']:>12.3%} {cf['naive_dual_host']:>12.4%} | "
              f"{cf['sequential_path_lost']:>17.1%} {cf['competitive_both_lost']:>12.1%}")
    print("讲义 §4.3 的两个印刷数（ε = 0.1%）：")
    print(f"  p = 0.5%：c(1-p)/p = {c*(1-0.005)/0.005:.3%}（讲义印 19.9%）")
    print(f"  p = 30%：c(1-p)/p = {c*(1-0.30)/0.30:.3%}（讲义印 0.23%）")
    print("naive 病原虚增公式即讲义 §4.3 的渗漏放大式：宿主渗漏入病原的伪计数 = ε(1-p)，")
    print("相对病原真实份额 p 放大 ε(1-p)/p —— 渗透率 ε 恒定，p 随时序抬高，")
    print("虚增幅度随之塌缩 → 矩阵里出现『保守基因早期虚高、随侵染持续下调』的")
    print("完美假动力学（12→48 hpi 表观下调约 "
          f"{closed_form(c,0.005)['naive_dual_path']/closed_form(c,0.30)['naive_dual_path']:.1f} 倍）。")

    # ---------------- Part 1：模拟对照（合成算例） ----------------
    print()
    print("=" * 78)
    print(f"[Part 1 · 合成算例] N = {args.n_reads:,} 条读段，三规则模拟实现值"
          f"（seed={args.seed}）")
    print("=" * 78)
    print(f"{'p':>6} | {'naive 病原虚增(实现)':>18} | {'顺序病原缺失(实现)':>18} "
          f"| {'竞争 病原/宿主各损失':>18}")
    sim_rows = {}
    for p in p_grid:
        s = simulate(c, p, args.n_reads, args.seed)
        sim_naive = s["path_naive"] / s["path_true"] - 1.0
        sim_seq = 1.0 - s["path_seq"] / s["path_true"]
        sim_comp_h = 1.0 - s["host_comp"] / s["host_true"]
        sim_comp_p = 1.0 - s["path_comp"] / s["path_true"]
        sim_rows[p] = (s, sim_naive, sim_seq, sim_comp_h, sim_comp_p)
        print(f"{p:>5.1%} | {sim_naive:>17.3%} | {sim_seq:>17.3%} | "
              f"{sim_comp_p:>8.3%} / {sim_comp_h:<8.3%}")
    print("顺序归属的偏倚方向：先比宿主 → 病原保守 read 被宿主吞掉（病原缺失 ≈ c），")
    print("且流程里不产出歧义读段记录，后端彻底不可见（讲义 §4.2 核心风险列）。")
    print("竞争性唯一比对：两侧各损失 ≈ c，但损失以 multimap 比例显式披露（可审计）。")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        check("手算规则：c=0.1%、p=0.5% → naive 病原虚增 = 19.9%（讲义 §4.3 印刷值）",
              abs(closed_form(0.001, 0.005)["naive_dual_path"] - 0.199) < 1e-9)
        check("手算规则：c=0.1%、p=30% → naive 病原虚增 = 0.23%（讲义 §4.3 印刷值）",
              abs(closed_form(0.001, 0.30)["naive_dual_path"] - 0.0023333333) < 1e-6)
        for p in p_grid:
            s, sim_naive, sim_seq, sim_comp_h, sim_comp_p = sim_rows[p]
            cf = closed_form(c, p)
            # naive 虚增估计量 = 伪计数/真病原计数，delta 法标准误：
            # σ² ≈ [c(1-p) + c²(1-p)³/p] / (N·p²)；容差取 4σ
            sig_naive = np.sqrt((c * (1 - p) + c ** 2 * (1 - p) ** 3 / p)
                                / (args.n_reads * p ** 2))
            tol_naive = max(4.0 * sig_naive, 1e-4)
            check(f"p={p:.1%}：模拟 naive 病原虚增 {sim_naive:.4%} ≈ 闭式 "
                  f"{cf['naive_dual_path']:.4%}",
                  abs(sim_naive - cf["naive_dual_path"]) < tol_naive)
            check(f"p={p:.1%}：模拟顺序病原缺失 {sim_seq:.4%} ≈ 闭式 c = {c:.4%}",
                  abs(sim_seq - c) < max(5.0 * np.sqrt(c / args.n_reads), 2e-4))
            check(f"p={p:.1%}：竞争性双侧损失对称（病原 {sim_comp_p:.4%} vs "
                  f"宿主 {sim_comp_h:.4%}，均 ≈ c）",
                  abs(sim_comp_p - c) < 5e-4 and abs(sim_comp_h - c) < 5e-4)
        # 假动力学方向：早期虚增 > 晚期虚增（恒定渗透率 → 表观持续下调）
        check("假动力学方向：naive 病原虚增随 p 单调下降（早期 19.9% → 晚期 0.23%）",
              closed_form(c, 0.005)["naive_dual_path"]
              > closed_form(c, 0.30)["naive_dual_path"])
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

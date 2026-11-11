#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch04_ccs_vote.py — PacBio CCS 环形共识：独立随机错误被多数票稀释（合成算例）

服务章节：第 4 章 §4.4「PacBio SMRT 与 HiFi 环形共识」概念小节、§4.4 末
「Q 值」段「深度非线性冗余投票」论断、失效条件第 2 条的对照面
（投票只对*独立随机*错误有效——系统性偏差见 demos/ch04_homopolymer_indel.py）。

数据性质：【合成算例】错误由固定种子的伪随机数注入，与任何真实测序 run 无关；
所有输出不得写成真实样本（如 PRJEB100987 任何 Run）的实测结果。
模型口径：只模拟单碱基替换错误、每条 read 每位置独立同分布（讲义所称
「空间独立随机分布」的简化版），共识 = 4 碱基多数票；不模拟 indel。

正文引用的输出：
  - 共识残留错误率随 passes 增加近似指数下降（u03 §4.2「以指数级被迅速稀释」）
  - 「≥30 次独立覆盖、单点错误 0.1 时全部同错概率 (0.1)^30 = 1e-30」的算术复核
    与中等规模模拟对照（讲义 u03 §4.7 第 2 步跨越的保守界）
  - 多数票共识优于「任一单条 read」（HiFi 相对 CLR 的机制性收益，合成口径）

参数含义：
  --passes      共识轮数（绕圈次数）列表，逗号分隔；用奇数（偶数票会平票，
                平票仲裁本身引入额外错误，破坏「独立稀释」演示）
  --error-rate  单条 read 单碱基错误率 p（CLR 口径设例，默认 0.10）
  --n-pos       模拟位点数（越多估计越稳）
  --seed        随机种子（固定，保证可复现）
"""
import argparse
import sys

import numpy as np


def consensus_residual(p, n_passes, n_pos, rng):
    """n_passes 条独立 read 逐位多数票后的残留错误率（合成模型）。

    所有 pass 读同一物理分子：真实碱基逐位相同，错误各自独立注入。
    """
    true_base = rng.integers(0, 4, n_pos, dtype=np.int8)
    bases = np.broadcast_to(true_base, (n_passes, n_pos))
    err = rng.random((n_passes, n_pos)) < p
    # 出错位置换成随机错误碱基（可能与真实碱基相同，即「错成对的」）
    wrong = (bases + rng.integers(1, 4, (n_passes, n_pos))) % 4
    called = np.where(err, wrong, bases)
    # 多数票：0..3 各自计数，取最大；平票取小编号（对 4 进制近似无影响）
    counts = np.zeros((4, n_pos), dtype=np.int64)
    for b in range(4):
        counts[b] = (called == b).sum(axis=0)
    cons = counts.argmax(axis=0)
    return float((cons != true_base).mean())


def all_agree_prob(p, n_passes):
    """p^n：所有 read 在同一位点犯同一个特定错误的联合概率（讲义保守界口径）。"""
    return p ** n_passes


def main():
    ap = argparse.ArgumentParser(
        description="CCS 多数票共识稀释独立随机错误（合成算例，固定种子）")
    ap.add_argument("--passes", default="1,3,5,11,21,31")
    ap.add_argument("--error-rate", type=float, default=0.10)
    ap.add_argument("--n-pos", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=20261103)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    p = args.error_rate
    pass_list = [int(x) for x in args.passes.split(",")]
    rng = np.random.default_rng(args.seed)

    print("=" * 70)
    print(f"[合成算例] 单条 read 单碱基错误率 p = {p:.2f}，"
          f"多数票共识，{args.n_pos} 个位点/档，seed={args.seed}")
    print("=" * 70)
    print(f"{'passes':<8}{'共识残留错误率':<18}{'换算 Q 值':<12}{'相对单条改善'}")
    residuals = {}
    for k in pass_list:
        r = consensus_residual(p, k, args.n_pos, rng)
        residuals[k] = r
        if r > 0:
            q = -10.0 * np.log10(r)
            print(f"{k:<8}{r:<18.3e}{q:<12.1f}{p / r:,.0f}×")
        else:
            # 0 错：给出基于样本量的上界（95% CI：p_err < 3/n）
            print(f"{k:<8}{0.0:<18.3e}{f'>{-10*np.log10(3/args.n_pos):.1f}':<12}"
                  f"> {p/(3/args.n_pos):,.0f}×（0/{args.n_pos} 错，95%CI 上界）")
    print()
    print("[观察] 残留错误率随 passes 增加而快速下降（各档 passes 间隔不等，相邻档比值不是常数）"
          "（独立随机错误的稀释机制，合成口径）")

    print()
    print("=" * 70)
    print("[算术复核] 讲义 u03 §4.7：30 次独立覆盖、单点错误 0.1 时")
    print("           『全部同错概率 = (0.1)^30』")
    print("=" * 70)
    bound = all_agree_prob(0.1, 30)
    print(f"(0.1)^30 = {bound:.3e}  →  讲义表述 10^-30："
          f"{'一致' if abs(bound - 1e-30) / 1e-30 < 1e-9 else '不一致'}")
    # 中等规模直接模拟（10^7 位点 × 10 passes 全同错太稀疏，用 5 passes 演示趋势）
    rng2 = np.random.default_rng(args.seed + 1)
    n_demo = 2_000_000
    sim_all_wrong = {}
    for k in (3, 5):
        sim_all_wrong[k] = float(
            (rng2.random((k, n_demo)) < 0.1).all(axis=0).mean())
        print(f"模拟对照：{k} 条 read 全错同一位点的频率 = {sim_all_wrong[k]:.3e}"
              f"（理论 p^{k} = {all_agree_prob(0.1, k):.3e}）")

    if args.selftest:
        print()
        ok = True
        checks = [
            ("残留错误率随 passes 单调不增，检出限以上严格下降",
             all(residuals[a] >= residuals[b] for a, b in zip(pass_list, pass_list[1:]))
             and all(residuals[a] > residuals[b] for a, b in zip(pass_list, pass_list[1:])
                     if residuals[b] > 0)),
            ("11 passes 残留 < 单条 p 的 1%",
             residuals[11] < p * 0.01),
            ("21 passes 残留 < 11 passes 残留 / 5",
             residuals[21] < residuals[11] / 5),
            ("(0.1)^30 = 1e-30 算术一致", abs(bound - 1e-30) < 1e-40),
            ("p^3 模拟频率与理论同量级（±50%）",
             abs(sim_all_wrong[3] - 1e-3) < 0.5e-3),
        ]
        for name, passed in checks:
            print(f"  {'PASS' if passed else 'FAIL'}  {name}")
            ok = ok and passed
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

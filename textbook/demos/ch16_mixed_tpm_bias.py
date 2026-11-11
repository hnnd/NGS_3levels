#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch16_mixed_tpm_bias.py — 宿主与病原合并算 TPM 的方向性错误：病原被压低多少倍、
宿主/病原各自的虚假时序趋势（合成算例）

服务章节：第 16 章 §16.4 概念与方法（分开归一化）、§16.5 失效条件第 2 条
（宿主与病原合在一起算 TPM，病原表达被系统性压低，方向性错误）。
源讲义：p03 §4.4（分开归一化：合起来算 TPM 错在哪个方向）。

模型（全部为合成模型，非任何真实样本结果）：
  * 一个合成「混合组织」样本：H 个宿主基因 + P 个病原基因，各基因分子份额
    q_i（宿主）/ r_j（病原）在时序上恒定不变（没有一根基因真的差异表达）。
  * p = 病原分子占全部转录分子的比例，随时序从 0.5%（12 hpi）升到 30%（48 hpi）。
  * 测序 = 按分子份额抽 M 条读段（Multinomial）；TPM 先按读段计数除以基因长度
    再对全体基因归一到 10^6。
  * 两种归一化口径：
      merged   宿主+病原基因放进同一个分母（初学者致命错误）；
      separate 两个物种各自归一（本课程规定动作，讲义 §4.4）。
  * 闭式（手算规则）：分子份额 = 读段份额（合成模型无长度/GC 偏倚），故
      病原基因 merged TPM / separate TPM = p（精确），即病原被压低 1/p 倍；
      时序上恒定病原基因的 merged TPM 倍数变化 = p_晚/p_早（伪造全面暴涨）；
      恒定宿主基因的 merged TPM 倍数变化 = (1-p_晚)/(1-p_早)（伪造全面下调）。

参数（--help 可见）：
  --n-host / --n-path   宿主/病原基因数（默认 15000 / 12000）
  --molecules           每样本抽样分子数（默认 2e7，对齐数据 README 截取量级）
  --seed                随机种子（默认 20261104）
  --selftest            断言合并/分开比值 ≈ p 与两个虚假时序趋势

正文引用的输出：
  - 压低倍数表：p = 0.5% / 2% / 5% / 10% / 30% → merged 口径下病原表达
    被压低 200× / 50× / 20× / 10× / 3.3×（手算规则入口：倍数 = 1/p）
  - 虚假时序：全部（真实恒定的）病原基因在 merged TPM 里表观上调 ≈ 60 倍
    （p 0.5%→30%）、全部宿主基因表观下调 ≈ 30%（(1-p) 之比）——
    讲义 §4.4「宿主全面下调、病原全面暴涨」的定量注脚
  - 模拟实现值与闭式的一致性（selftest 断言）

依赖：Python 标准库 + numpy（scipy 不使用）。
合成算例：所有「基因表达」均为随机数生成器产物，与任何真实样本无关。
"""
import argparse
import sys

import numpy as np

SEED = 20261104
# 合成侵染时序：12 / 24 / 36 / 48 hpi 的病原真实分子占比（不设例出处，合成设定）
P_TIME = [0.005, 0.02, 0.10, 0.30]


def simulate(args):
    """返回 dict：每时相每重复的 merged/separate TPM 矩阵及基因份额。"""
    rng = np.random.default_rng(args.seed)
    n_h, n_p = args.n_host, args.n_path
    # 基因长度（只影响 TPM 内部权重，不影响闭式比值）
    len_h = rng.uniform(500.0, 6000.0, n_h)
    len_p = rng.uniform(500.0, 6000.0, n_p)
    # 分子份额（Dirichlet 一次性抽定，时序恒定）
    w_h = rng.gamma(0.3, 1.0, n_h)
    w_p = rng.gamma(0.3, 1.0, n_p)
    q_h = w_h / w_h.sum()
    q_p = w_p / w_p.sum()

    out = []
    for p in P_TIME:
        prob = np.concatenate([(1.0 - p) * q_h, p * q_p])
        for _ in range(3):  # 3 个生物学重复
            counts = rng.multinomial(args.molecules, prob)
            c_h, c_p = counts[:n_h], counts[n_h:]
            # TPM：读段/长度 → 各自分母归一到 1e6
            r_all = np.concatenate([c_h / len_h, c_p / len_p])
            tpm_merged = r_all / r_all.sum() * 1e6
            r_h, r_p = c_h / len_h, c_p / len_p
            tpm_h = r_h / r_h.sum() * 1e6
            tpm_p = r_p / r_p.sum() * 1e6
            out.append(dict(p=p, merged_h=tpm_merged[:n_h], merged_p=tpm_merged[n_h:],
                            sep_h=tpm_h, sep_p=tpm_p))
    return out


def main():
    ap = argparse.ArgumentParser(
        description="宿主+病原合并 TPM 的方向性畸变（合成算例；服务第 16 章失效条件 2，"
                    "对齐讲义 p03 §4.4）")
    ap.add_argument("--n-host", type=int, default=15000)
    ap.add_argument("--n-path", type=int, default=12000)
    ap.add_argument("--molecules", type=int, default=20_000_000,
                    help="每样本合成抽样分子数（默认 2e7，对齐主线数据截取量级）")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    # ---------------- Part 0：闭式（手算规则） ----------------
    print("=" * 78)
    print("[Part 0 · 手算规则] merged TPM 下病原被压低的倍数 = 1/p（p = 病原分子占比）")
    print("=" * 78)
    print(f"{'病原占比 p':>10} | {'病原被压低（merged vs separate）':>24} | "
          f"{'宿主基因表观变化（时序内）':>20}")
    for p in P_TIME:
        print(f"{p:>9.1%} | {'1/p = ' + format(1.0 / p, '>6.1f') + '×':>24} | "
              f"{'(1-p) 因子 = ' + format(1.0 - p, '.3f'):>20}")
    print(f"虚假时序：恒定病原基因 merged TPM 的 48/12 hpi 倍数 = "
          f"{P_TIME[-1] / P_TIME[0]:.1f}×（伪造全面暴涨）；恒定宿主基因 = "
          f"{(1 - P_TIME[-1]) / (1 - P_TIME[0]):.3f}（伪造全面下调 ≈ "
          f"{1 - (1 - P_TIME[-1]) / (1 - P_TIME[0]):.0%}）。")

    # ---------------- Part 1：模拟（合成算例） ----------------
    print()
    print("=" * 78)
    print(f"[Part 1 · 合成算例] {args.n_host} 宿主基因 + {args.n_path} 病原基因，"
          f"份额时序恒定；每样本抽 {args.molecules:.0e} 分子 × 3 重复"
          f"（seed={args.seed}）")
    print("=" * 78)
    rows = simulate(args)
    print(f"{'时相 p':>7} | {'median(merged/sep) 病原基因':>26} "
          f"| {'median(merged/sep) 宿主基因':>26}")
    for p in P_TIME:
        sel = [r for r in rows if r["p"] == p]
        ratio_p = np.median(np.concatenate(
            [r["merged_p"] / np.maximum(r["sep_p"], 1e-12) for r in sel]))
        ratio_h = np.median(np.concatenate(
            [r["merged_h"] / np.maximum(r["sep_h"], 1e-12) for r in sel]))
        print(f"{p:>6.1%} | {ratio_p:>25.4f} | {ratio_h:>25.4f}")
    # 时序倍数（取每时相重复均值再相比，围绕中位基因的代表性趋势）
    t_early = [r for r in rows if r["p"] == P_TIME[0]]
    t_late = [r for r in rows if r["p"] == P_TIME[-1]]
    mp_early = np.mean([r["merged_p"] for r in t_early], axis=0)
    mp_late = np.mean([r["merged_p"] for r in t_late], axis=0)
    mh_early = np.mean([r["merged_h"] for r in t_early], axis=0)
    mh_late = np.mean([r["merged_h"] for r in t_late], axis=0)
    fc_p = np.median(mp_late / np.maximum(mp_early, 1e-12))
    fc_h = np.median(mh_late / np.maximum(mh_early, 1e-12))
    print(f"虚假时序（实现值）：恒定病原基因 merged TPM 48/12 hpi 中位倍数 = {fc_p:.1f}×；"
          f"恒定宿主基因 = {fc_h:.3f}。")
    print("结构性注记：merged 口径下宿主占基因数与分子数双重多数且份额恒定，"
          "median-of-ratios size factor 将 ≈ 1，无法在下游统计里『自动纠正』这个")
    print("分母畸变 —— 必须在物理上拆分矩阵（讲义 §4.4、03_dual_deseq2_lrt.R 头部纪律）。")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        # 闭式：1/p 表
        check("手算规则：p=0.5% → 压低 200×", abs(1.0 / 0.005 - 200.0) < 1e-9)
        check("手算规则：p=30% → 压低 3.33×", abs(1.0 / 0.30 - 3.3333333) < 1e-5)
        # 模拟：每时相 merged/separate 中位比 ≈ p（Multinomial 噪声下放宽到 ±20%）
        for p in P_TIME:
            sel = [r for r in rows if r["p"] == p]
            ratio_p = np.median(np.concatenate(
                [r["merged_p"] / np.maximum(r["sep_p"], 1e-12) for r in sel]))
            check(f"p={p:.1%}：模拟 median(merged/separate) 病原 = {ratio_p:.4f} ≈ p",
                  abs(ratio_p - p) < 0.2 * p + 1e-4)
        # 虚假时序方向与量级
        check(f"恒定病原基因表观上调 {fc_p:.1f}× ≈ p 之比 {P_TIME[-1]/P_TIME[0]:.1f}×"
              f"（方向为上调）", abs(fc_p - P_TIME[-1] / P_TIME[0]) < 0.15 * fc_p)
        check(f"恒定宿主基因表观下调 {fc_h:.3f} ≈ (1-p晚)/(1-p早) "
              f"{(1 - P_TIME[-1]) / (1 - P_TIME[0]):.3f}（方向为下调）",
              abs(fc_h - (1 - P_TIME[-1]) / (1 - P_TIME[0])) < 0.05)
        # 份额恒定的自我锚定：separate TPM 时序几乎不变（假趋势只来自 merged 分母）
        sp_early = np.mean([r["sep_p"] for r in t_early], axis=0)
        sp_late = np.mean([r["sep_p"] for r in t_late], axis=0)
        fc_sp = np.median(sp_late / np.maximum(sp_early, 1e-12))
        check(f"分开归一化下同一批基因 48/12 hpi 倍数 = {fc_sp:.3f} ≈ 1"
              "（份额恒定，假趋势消失）", abs(fc_sp - 1.0) < 0.05)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

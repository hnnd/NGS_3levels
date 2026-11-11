#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch21_structure_confounding_ols.py — 群体结构如何伪造虚假关联：遗漏变量偏差
（OVB）恒等式核验、朴素 OLS 的假阳性泛滥、加 Q 协变量后回落（合成算例）

服务于：教材第 21 章（全基因组关联分析与后 GWAS）§21.4 概念与方法
（GLM → MLM 的模型谱系）、§21.5 失效条件第 1 条（群体结构未校正使 QQ 图
膨胀、假阳性泛滥），对应讲义 p05 ⑦-7.1（遗漏变量偏差推导式：
β̂ → (ȳ_A−ȳ_B)(p_A,j−p_B,j)·w_A·w_B / Var(x_j)）、§4.2 模型谱系表、
⑥-6.1 诊断矩阵第一行（整体系统性抬升 = 系统性假阳性灾难）。

合成设定（不基于任何真实群体；固定种子可复现；二倍体等位剂量 0/1/2 口径，
直接从模拟基因型矩阵做真实 OLS，不经过任何近似抽样）：
  - 两个亚群 A/B，样本权重 w_A / w_B（默认各 1/2），共 n 个个体；
  - 表型 y = Δ·I(属 A) + ε，ε ~ N(0,1) —— 表型均值差 ȳ_A−ȳ_B = Δ 与任何
    基因型无关（纯环境/栽培差异，合成设定）；
  - M 个中性 SNP：亚群间频率差 δ_j = p_A,j − p_B,j ~ N(0, σ_δ²)，群内
    哈代–温伯格平衡，x ∈ {0,1,2} 剂量，Var(x_j) = 2p_j(1−p_j)；
  - 对每个 SNP 做朴素一元回归（OLS，不加任何协变量）得到 β̂_j 与 z_j；
    再对「OLS + 亚群指示协变量」（即 GLM+Q 的两群退化形态：y 与 x 各自
    对 [1, I_A] 正交化后再回归）重算一遍作对照。
  - OVB 恒等式核验：剂量口径下 E[β̂_j] = Δ·δ_j·w_A·w_B/(p_j(1−p_j))
    （与讲义 ⑦-7.1 的写法 Δ·δ_j·w_A·w_B/Var(x_j) 等价——讲义把 Var(x)
    按单条等位基因指示量记为 p(1−p)，物理效应量相同）；把每个 SNP 的
    β̂_j 对 δ_j/(p_j(1−p_j)) 回归，斜率应 ≈ Δ·w_A·w_B。

正文引用的输出（手算可对）：
  - 朴素 OLS 下中性 SNP 的假阳性率（p<0.05 占比）远高于名义 5%，
    λ_GC 系统性 > 1；加入亚群指示协变量后假阳性率回到名义水平、λ 回落到
    ≈1 —— 讲义 ⑦-7.1「全基因组系统性假阳性，调高阈值在数学上无法破局」、
    §4.2「OLS 完全忽略群体结构 → 灾难性系统性假阳性」的合成复现；
  - OVB 恒等式斜率核验：给定 Δ=2、w_A=w_B=0.5，斜率应 ≈ 1.0；
  - 手算锚点：δ=0.3、Δ=2、w_A=w_B=0.5、p=0.5 →
    E[β̂] = 2×0.3×2×0.25/0.5 = 0.6（每单位剂量的表型差）。

参数：
  --n          总样本量（默认 400，两亚群各 200）
  --m          中性 SNP 数（默认 20000）
  --delta      亚群表型均值差 Δ（默认 2.0）
  --sigma-d    亚群间频率差 δ_j 的标准差（默认 0.15）
  --seed       随机种子（默认 20261104）

合成数据不得写成真实群体结果。只依赖 numpy/scipy；约 3 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch21_structure_confounding_ols.py --selftest
"""
import argparse

import numpy as np
from scipy import stats


def simulate(n, m, delta, sigma_d, seed):
    rng = np.random.default_rng(seed)
    n_a = n // 2
    n_b = n - n_a
    w_a, w_b = n_a / n, n_b / n

    # 亚群归属（前 n_a 个 = A）；表型均值差 Δ 与基因型独立
    is_a = np.zeros(n)
    is_a[:n_a] = 1.0
    y = delta * is_a + rng.standard_normal(n)
    y_c = y - y.mean()

    # 每个 SNP 的亚群频率与频率差
    d_j = rng.normal(0.0, sigma_d, m)
    p_b = rng.uniform(0.15, 0.85, m)
    p_a = np.clip(p_b + d_j, 0.02, 0.98)
    d_j = p_a - p_b
    p = w_a * p_a + w_b * p_b

    # 直接模拟基因型矩阵（m × n，int8）：群内 HWE 二项抽样
    x = np.empty((m, n), dtype=np.float64)
    for lo, hi, pj in ((0, n_a, p_a), (n_a, n, p_b)):
        x[:, lo:hi] = rng.binomial(2, pj[:, None], size=(m, hi - lo))
    x_c = x - x.mean(axis=1, keepdims=True)
    sxx = (x_c * x_c).sum(axis=1)
    sxy = x_c @ y_c
    beta = sxy / sxx
    rss = (y_c @ y_c) - beta * sxy
    se = np.sqrt((rss / (n - 2)) / sxx)
    z_ols = beta / se
    p_ols = 2.0 * stats.norm.sf(np.abs(z_ols))

    # 对照：GLM+Q 两群退化形态 —— y 与每个 x 都对 [1, I_A] 正交化后再回归
    u = np.column_stack([np.ones(n), is_a])
    mu = np.linalg.pinv(u.T @ u) @ u.T            # (2, n)：U 列空间的投影坐标映射
    my = y - u @ (mu @ y)                          # 残差化 y
    mx = x_c - (x_c @ u) @ mu                      # 逐 SNP 残差化 x（向量化）
    sxx_q = (mx * mx).sum(axis=1)
    sxy_q = mx @ my
    beta_q = sxy_q / sxx_q
    rss_q = (my @ my) - beta_q * sxy_q
    se_q = np.sqrt((rss_q / (n - 3)) / sxx_q)
    z_q = beta_q / se_q
    p_q = 2.0 * stats.norm.sf(np.abs(z_q))

    # OVB 恒等式：β̂_j 对 δ_j/(p_j(1−p_j)) 回归，斜率应 ≈ Δ·w_A·w_B
    g = d_j / (p * (1.0 - p))
    slope, _, _, _, _ = stats.linregress(g, beta)

    return dict(w_a=w_a, w_b=w_b, slope=slope,
                fpr_ols=float(np.mean(p_ols < 0.05)),
                fpr_q=float(np.mean(p_q < 0.05)),
                lam_ols=lambda_gc(p_ols), lam_q=lambda_gc(p_q),
                frac_p_lt_1e4_ols=float(np.mean(p_ols < 1e-4)))


def lambda_gc(p):
    """基因组膨胀因子：中位卡方 / 卡方(df=1) 理论中位数（讲义 ⑦-7.3）。"""
    p = p[np.isfinite(p) & (p > 0) & (p <= 1)]
    return float(np.median(stats.chi2.ppf(1.0 - p, df=1)) /
                 stats.chi2.ppf(0.5, df=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--m", type=int, default=20000)
    ap.add_argument("--delta", type=float, default=2.0)
    ap.add_argument("--sigma-d", type=float, default=0.15)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    r = simulate(args.n, args.m, args.delta, args.sigma_d, args.seed)

    print("合成算例：两亚群（w_A={:.2f} / w_B={:.2f}，n={}），表型均值差 Δ={}，"
          "中性 SNP {} 个（δ_j ~ N(0, {:.2f}²)）".format(
              r["w_a"], r["w_b"], args.n, args.delta, args.m, args.sigma_d))
    print("  —— 不基于任何真实群体；直接从模拟基因型矩阵做真实 OLS")
    print()
    print("朴素 OLS（不加协变量，对应 gemma -lm / GLM 对照行的行为）：")
    print("  中性 SNP 假阳性率 p<0.05 : {:.3f}（名义 0.05）".format(r["fpr_ols"]))
    print("  中性 SNP 中 p<1e-4 占比   : {:.4f}（无结构时应 ≈ 1e-4）".format(
        r["frac_p_lt_1e4_ols"]))
    print("  λ_GC                       : {:.3f}".format(r["lam_ols"]))
    print("OLS + 亚群指示协变量（GLM+Q 两群退化形态）：")
    print("  中性 SNP 假阳性率 p<0.05 : {:.3f}".format(r["fpr_q"]))
    print("  λ_GC                     : {:.3f}".format(r["lam_q"]))
    print()
    print("OVB 恒等式核验（讲义 ⑦-7.1，剂量 0/1/2 口径）：β̂_j 对 δ_j/(p_j(1−p_j)) 回归")
    print("  斜率观测值   : {:.4f}".format(r["slope"]))
    print("  理论值 Δ·w_A·w_B = {:.2f}×{:.3f}×{:.3f} = {:.4f}".format(
        args.delta, r["w_a"], r["w_b"], args.delta * r["w_a"] * r["w_b"]))
    print("  手算锚点：δ=0.3、Δ=2、w_A=w_B=0.5、p=0.5 → E[β̂]=0.6000（每单位剂量）")

    if args.selftest:
        checks = [
            (f"朴素 OLS 假阳性率({r['fpr_ols']:.3f}) 远超名义 0.05 —— 结构伪造关联",
             r["fpr_ols"] > 0.15),
            (f"OLS 极端尾部同比例膨胀（p<1e-4 占比 {r['frac_p_lt_1e4_ols']:.4f} "
             f"> 10×1e-4）", r["frac_p_lt_1e4_ols"] > 10 * 1e-4),
            (f"朴素 OLS λ_GC({r['lam_ols']:.3f}) > 1.3 —— QQ 整体抬升档",
             r["lam_ols"] > 1.3),
            (f"加 Q 协变量后假阳性率({r['fpr_q']:.3f}) 回到名义 5% 附近",
             0.035 <= r["fpr_q"] <= 0.065),
            (f"加 Q 协变量后 λ_GC({r['lam_q']:.3f}) ≈ 1",
             0.9 <= r["lam_q"] <= 1.1),
            (f"OVB 斜率({r['slope']:.4f}) ≈ Δ·w_A·w_B "
             f"({args.delta * r['w_a'] * r['w_b']:.4f})",
             abs(r["slope"] - args.delta * r["w_a"] * r["w_b"]) < 0.05),
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

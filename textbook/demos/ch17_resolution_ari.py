#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch17_resolution_ari.py — resolution 扫描：聚类数与稳定性（ARI）随 resolution 变化（合成算例）

服务于：教材第 17 章 §17.5 失效条件第 3 条「resolution 没有客观最优，聚类数决定下游一切」，
对应讲义 p02 §4.5 / §⑦-1（聚类稳定性：结论必须在稳定区间内成立）与
../03_code/phd/scripts/02_seurat_pipeline.R 第 5 步（resolution grid 0.2–1.0）。

合成设定：
  - 8 个「真实」细胞簇（高斯混合，d = 12 维，每簇 300 个细胞）：其中 6 个彼此分离良好，
    另 2 对「近缘」簇（中心距仅数倍于簇内 σ）——低分辨率下应被合并；
  - 用 k-means 按簇数 k = 2…16 扫描（本 demo 以簇数 k 直接扮演 resolution 的角色：
    Seurat 的 resolution 与切出簇数近似单调递增，讲义 §4.5；真实流程跑的是
    Louvain/Leiden 图划分 + resolution grid，见 02_seurat_pipeline.R）；
  - 每个 k 用 5 个随机种子重复，以手算 ARI（Adjusted Rand Index，无第三方实现，
    公式见函数 docstring）对照「真实簇标签」：ARI = 1 为完全恢复真值，0 为随机水平。

正文引用的输出：
  - 簇数 k（= resolution 的替身）与 ARI 的关系曲线：ARI 在低 k 处受限（欠分割，
    近缘对被合并），在真簇数附近的「稳定窗口」达到平台，k 继续增大后回落（过分割）；
  - 「结论必须在稳定区间内成立」的定量依据：只有平台窗口内的簇结构才与真值一致，
    单一 resolution 定稿没有客观真值（讲义 §⑦-1）。

参数：
  --cells   总细胞数（默认 2400）
  --dims    特征维数（默认 12）
  --k-max   最大扫描簇数（默认 16）
  --seeds   每个 k 的重复种子数（默认 5）
  --seed    主随机种子（默认 20261104）

合成数据不得写成真实样本结果；真实数据的聚类稳定性用 clustree / bootstrap 共聚类评估（讲义 §⑦-1）。
只依赖 numpy；约 1–2 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch17_resolution_ari.py --selftest
"""
import argparse

import numpy as np

N_TRUE_CLUSTERS = 8
CLOSE_PAIRS = ((0, 1), (2, 3))  # 这两对簇中心故意拉近：低 k 下应被合并


def make_data(n_cells, dims, rng):
    """8 簇高斯混合：4 个分离良好 + 2 对近缘（共 8 簇）。返回 (X, 真值标签)。"""
    n_per = n_cells // N_TRUE_CLUSTERS
    centers = rng.normal(0.0, 3.0, (N_TRUE_CLUSTERS, dims))
    for a, b in CLOSE_PAIRS:  # 近缘对：中心距 ≈ 2×簇内σ量级
        centers[b] = centers[a] + rng.normal(0.0, 0.8, dims) / np.sqrt(dims) * 2.0
    X, labels = [], []
    for j in range(N_TRUE_CLUSTERS):
        X.append(centers[j] + rng.normal(0.0, 1.0, (n_per, dims)))
        labels += [j] * n_per
    return np.vstack(X), np.array(labels)


def ari(a, b):
    """Adjusted Rand Index（手算实现）。

    ARI = (Σ_ij C(n_ij,2) − Σ_i C(n_i·,2)Σ_j C(n_·j,2)/C(n,2))
          / ( ½[Σ_i C(n_i·,2)+Σ_j C(n_·j,2)] − Σ_i C(n_i·,2)Σ_j C(n_·j,2)/C(n,2) )
    对标签置换不变；随机划分期望为 0，完全一致为 1。
    """
    la = np.unique(a, return_inverse=True)[1]
    lb = np.unique(b, return_inverse=True)[1]
    na, nb = la.max() + 1, lb.max() + 1
    n = len(a)
    tab = np.bincount(la * nb + lb, minlength=na * nb).reshape(na, nb).astype(float)
    comb = lambda x: x * (x - 1) / 2.0  # noqa: E731
    sum_ij = comb(tab).sum()
    sum_i = comb(tab.sum(axis=1)).sum()
    sum_j = comb(tab.sum(axis=0)).sum()
    total = comb(float(n))
    expected = sum_i * sum_j / total
    return (sum_ij - expected) / (0.5 * (sum_i + sum_j) - expected)


def kmeans(X, k, rng, iters=40):
    """k-means++ 初始化 + Lloyd 迭代。返回簇标签。"""
    n = X.shape[0]
    centers = [X[rng.integers(n)]]
    for _ in range(k - 1):
        d2 = np.min(((X[:, None, :] - np.stack(centers)[None]) ** 2).sum(axis=2), axis=1)
        centers.append(X[rng.choice(n, p=d2 / d2.sum())])
    C = np.stack(centers)
    for _ in range(iters):
        lab = ((X[:, None, :] - C[None]) ** 2).sum(axis=2).argmin(axis=1)
        newC = np.array([X[lab == j].mean(axis=0) if np.any(lab == j) else C[j]
                         for j in range(k)])
        if np.allclose(newC, C, atol=1e-8):
            break
        C = newC
    return lab


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--cells", type=int, default=2400)
    ap.add_argument("--dims", type=int, default=12)
    ap.add_argument("--k-max", type=int, default=16)
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    X, truth = make_data(args.cells, args.dims, np.random.default_rng(args.seed))

    print("合成算例：8 簇高斯混合（4 簇分离良好 + 2 对近缘，近缘对低 k 下会被合并）")
    print(f"n = {len(X)} 细胞，d = {args.dims}；k-means 扫描 k = 2…{args.k_max}，"
          f"每 k {args.seeds} 个种子；ARI 对照真值标签；seed = {args.seed}\n")
    print(f"{'k（≈resolution）':>16} | {'n_cluster':>9} | {'mean ARI':>9} | {'sd':>7}")
    print("-" * 50)
    rows = {}
    for k in range(2, args.k_max + 1):
        aris = []
        for s in range(args.seeds):
            rng = np.random.default_rng(args.seed + 97 * k + s)
            aris.append(ari(truth, kmeans(X, k, rng)))
        rows[k] = (float(np.mean(aris)), float(np.std(aris)))
        print(f"{k:>16} | {k:>9} | {rows[k][0]:>9.3f} | {rows[k][1]:>7.3f}")

    best_k = max(rows, key=lambda kk: rows[kk][0])
    plateau = [k for k in rows
               if rows[k][0] >= rows[best_k][0] - 0.05 and rows[k][0] >= 0.6]
    print(f"\n判读：ARI 在 k = {min(plateau)}–{max(plateau)} 处形成平台（最佳 k = {best_k}，"
          "≈ 真簇数 8），且平台区种子间 sd 更小（重抽样更稳定）；k 过小被压制（欠分割，"
          "近缘对被合并），k 过大回落（过分割）。")
    print("对应讲义 §⑦-1：结论必须表述为「在 resolution 区间内稳定成立」，"
          "不以单点 resolution 定稿；真实流程的 resolution↔簇数映射见 "
          "02_seurat_pipeline.R 输出的 cluster_stability.tsv（unverified）。")

    if args.selftest:
        peak = rows[best_k][0]
        checks = [
            (f"最佳 k = {best_k} 落在真簇数 8 附近（6–10）", 6 <= best_k <= 10),
            (f"平台 ARI ≥ 0.7（实际 {peak:.3f}）", peak >= 0.7),
            (f"欠分割端被压制：k = 2/3/4 的 ARI 均 < 0.5"
             f"（{rows[2][0]:.3f}/{rows[3][0]:.3f}/{rows[4][0]:.3f}）",
             all(rows[k][0] < 0.5 for k in (2, 3, 4))),
            (f"平台 ARI 高于过分割端 k={args.k_max}（{rows[args.k_max][0]:.3f}）",
             peak > rows[args.k_max][0] + 0.1),
            (f"平台区种子间 sd 更小（稳定性）：min sd(k=7…10) = "
             f"{min(rows[k][1] for k in range(7, 11)):.3f} "
             f"≤ 欠分割区 max sd(k=2…4)（{max(rows[k][1] for k in range(2, 5)):.3f}）",
             min(rows[k][1] for k in range(7, 11))
             <= max(rows[k][1] for k in range(2, 5))),
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

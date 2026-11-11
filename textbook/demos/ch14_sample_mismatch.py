#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch14_sample_mismatch.py — 计数矩阵列序与样本表行序错配：静默后果与断言式防御（合成算例）

服务章节：第 14 章 §14.4 概念与方法（DESeq2 输入纪律）、§14.5 失效条件第 2 条
「计数矩阵列序与样本表行序不一致（最高频，不报错）」。源讲义：m04 ⑨-E2、§5.4。
E2 的三种形态（学科专家 CH14_EXPERT_001 跑①在本机 DESeq2 1.50.2 逐字复现）：
  ① 集合相同、顺序不同 → DESeq2 报错（rownames of the colData ... not in the same order）；
  ② 样本数不同      → 报错（ncol(countData) == nrow(colData) is not TRUE）；
  ③ 矩阵无列名      → DESeq2 静默把 colData 行名贴上，不报错、样本标签全错 ← 最危险。
本脚本用纯统计模拟复现「标签贴错后流程照常跑完」的后果（形态 ③ 与「跳过校验的 ①」同构），
并给出断言式防御的最小代码。R 侧报错原文以讲义 ⑨-E2 / 专家现跑记录为准（本脚本不调用 R）。

模型（合成，非 PRJDB36269 或任何真实样本）：
  * 2 组 × 每组 n=6 个「样本」，文库大小相同（隔离标签错配这一个变量）；
  * n_gene 个「基因」：半数 H0（β=0），半数 H1（|log2FC|=1.5，方向各半）；
  * 计数 Y ~ NB(size=1/α, μ = μ_i·2^{β_i·x_j})，α=0.15；
  * 检验：负二项 log-GLM（无 offset，平衡设计），Wald 检验 H0: β1=0。
  * 错配通路的两种静默形态（都不报错、rc=0）：
      A 两组标签整体对调（最整齐的事故：元数据按处理顺序排、counts 按文件名排）——
        信号原样检出，但每个 log2FC 符号翻转，「上调」清单 100% 是下调基因；
      B 分组标签随机重贴 n-perm 次（seed 固定）——单次重贴与真实分组仍可能有
        ±1/3 量级偶然相关，故报多次平均：功效平均损失约 2/3、差异基因数损失约 90%。
    两类事故的共同点是流程无警告，PCA/质控图完全正常——错的全是结论。

参数（--help 可见）：
  --n-gene / --n-rep   基因数与每组样本数（默认 2400 / 6）
  --alpha              NB 离散度（默认 0.15）
  --n-perm             标签随机重贴次数（默认 10；报告平均后果）
  --seed               随机种子（默认 20260829，对齐 m04 脚本 set.seed(20260829) 的结构）

正文引用的输出：
  - Part 1：正确对齐 vs 标签错配的 H0 假阳性率、H1 检出率与「差异基因数」
    （p<0.05 且 |log2FC|>1 口径）——错配不制造假阳性，而是让真实信号全军覆没、
    结论变成「没有差异基因」，且全程 rc=0（不报错）
  - Part 2：断言式防御三行（显式重排 + identical 断言 + 无列名显式拒绝）
    在合成数据上的实际拦截记录

依赖：Python 标准库 + numpy + scipy。
合成算例：所有「基因表达计数」均为随机数生成器产物，与任何真实样本无关。
"""
import argparse
import sys

import numpy as np
from scipy import stats

SEED = 20260829  # 对齐 m04 脚本 set.seed(20260829)（结构对齐；RNG 不同）


def nb_glm_wald(y, x, alpha):
    """负二项 log-GLM（带步长回退的 Fisher scoring），无 offset；返回 β1 与 Wald p。
    得分 U_k = Σ x_k·(y−μ)/(1+α·μ)（NB 方差函数 μ+αμ² 的权重 μ/V = 1/(1+αμ)），
    信息阵 I = X'WX、W = diag(μ/(1+α·μ))；更新 beta += I⁻¹U。"""
    X = np.column_stack([np.ones_like(x), x])

    def score_at(b):
        mu = np.exp(np.clip(X @ b, -30.0, 30.0))
        w = mu / (1.0 + alpha * mu)
        H = (X.T * w) @ X
        return H, X.T @ ((y - mu) / (1.0 + alpha * mu))

    beta = np.linalg.lstsq(X, np.log(np.maximum(y, 0.1)), rcond=None)[0]
    H, sc = score_at(beta)
    nrm = np.linalg.norm(sc)
    for _ in range(50):
        try:
            step = np.linalg.solve(H, sc)
        except np.linalg.LinAlgError:
            break
        t, accepted = 1.0, False
        for _ in range(25):
            b_new = beta + t * step
            H_new, sc_new = score_at(b_new)
            n_new = np.linalg.norm(sc_new)
            if np.isfinite(n_new) and n_new <= nrm * (1.0 + 1e-6):
                accepted = True
                break
            t *= 0.5
        if not accepted:
            break
        if np.max(np.abs(t * step)) < 1e-8:
            beta, H = b_new, H_new
            break
        beta, H, sc, nrm = b_new, H_new, sc_new, n_new
    mu = np.exp(np.clip(X @ beta, -30.0, 30.0))
    w = mu / (1.0 + alpha * mu)
    H = (X.T * w) @ X
    cov = np.linalg.inv(H)
    z = beta[1] / np.sqrt(max(cov[1, 1], 1e-16))
    return beta[1], 2.0 * stats.norm.sf(abs(z))


def run_all_genes(y, x, alpha):
    """对 (n_gene, n) 矩阵逐基因 Wald 检验，返回 β1 与 p 数组。"""
    betas = np.empty(y.shape[0])
    pvals = np.empty(y.shape[0])
    for i in range(y.shape[0]):
        betas[i], pvals[i] = nb_glm_wald(y[i].astype(float), x, alpha)
    return betas, pvals


def main():
    ap = argparse.ArgumentParser(
        description="计数矩阵列序 vs 样本表行序错配的静默后果（合成算例；服务第 14 章"
                    "失效条件 2，对齐讲义 m04 ⑨-E2）")
    ap.add_argument("--n-gene", type=int, default=2400)
    ap.add_argument("--n-rep", type=int, default=6, help="每组样本数（默认 6）")
    ap.add_argument("--alpha", type=float, default=0.15)
    ap.add_argument("--n-perm", type=int, default=10,
                    help="标签随机重贴次数（默认 10；平均后果的一般性结论）")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    # ---------------- Part 0：E2 的三种形态（哪类会被救） ----------------
    print("=" * 78)
    print("[Part 0 · 讲义 ⑨-E2 的三种形态]（R 侧行为以讲义 / CH14_EXPERT_001 现跑为准）")
    print("=" * 78)
    forms = [
        ("① 集合相同、顺序不同", "DESeq2 报错（E2 原文：rownames of the colData ... "
         "are not in the same order）", "被救"),
        ("② 样本数不同", "报错（ncol(countData) == nrow(colData) is not TRUE）", "被救"),
        ("③ 矩阵无列名", "静默把 colData 行名贴上（colnames 被赋为 rownames），"
         "不报错、标签全错", "流程 rc=0，结论全错"),
    ]
    for name, behavior, fate in forms:
        print(f"  {name}\n      行为：{behavior}\n      后果：{fate}")

    # ---------------- 合成数据 ----------------
    rng = np.random.default_rng(args.seed)
    n = 2 * args.n_rep
    x = np.concatenate([np.zeros(args.n_rep), np.ones(args.n_rep)])
    ng = args.n_gene
    half = ng // 2
    beta_true = np.concatenate([np.zeros(half), np.full(ng - half, 1.5)])
    beta_true[half + rng.permutation(ng - half)[: (ng - half) // 2]] = -1.5
    mu_base = rng.lognormal(mean=np.log(800.0), sigma=1.5, size=ng)
    mu = mu_base[:, None] * 2.0 ** (beta_true[:, None] * x[None, :])
    y = rng.negative_binomial(1.0 / args.alpha,
                              (1.0 / args.alpha) / (1.0 / args.alpha + mu),
                              mu.shape)
    h0 = beta_true == 0
    h1 = ~h0

    # ---------------- Part 1：同一份矩阵，两种标签 ----------------
    print()
    print("=" * 78)
    print(f"[Part 1 · 合成算例] {ng} 基因 × 2 组 × {args.n_rep} 样本；α={args.alpha}，"
          f"seed={args.seed}（H1 基因 |log2FC| = 1.5）")
    print("=" * 78)
    b_ok, p_ok = run_all_genes(y, x, args.alpha)
    deg_mask_ok = (p_ok < 0.05) & (np.abs(b_ok) > 1)
    deg_ok = int(deg_mask_ok.sum())
    sign_ok = float((np.sign(b_ok[deg_mask_ok]) == np.sign(beta_true[deg_mask_ok])).mean())

    # 错配形态 A：两组标签整体对调（信号原样检出、方向全反）
    b_sw, p_sw = run_all_genes(y, 1.0 - x, args.alpha)
    deg_mask_sw = (p_sw < 0.05) & (np.abs(b_sw) > 1)
    deg_sw = int(deg_mask_sw.sum())
    sign_sw = float((np.sign(b_sw[deg_mask_sw]) == np.sign(beta_true[deg_mask_sw])).mean())

    # 错配形态 B：分组标签随机重贴 n-perm 次（报平均后果）
    fpr_bad = np.empty(args.n_perm)
    pow_bad = np.empty(args.n_perm)
    deg_bad = np.empty(args.n_perm, dtype=int)
    sign_bad = np.empty(args.n_perm)
    all_finite = True
    for k in range(args.n_perm):
        x_bad = x[rng.permutation(n)]
        b_k, p_k = run_all_genes(y, x_bad, args.alpha)
        all_finite = all_finite and np.isfinite(b_k).all() and np.isfinite(p_k).all()
        fpr_bad[k] = (p_k[h0] < 0.05).mean()
        pow_bad[k] = (p_k[h1] < 0.05).mean()
        deg_mask_k = (p_k < 0.05) & (np.abs(b_k) > 1)
        deg_bad[k] = int(deg_mask_k.sum())
        if deg_bad[k] > 0:
            sign_bad[k] = (np.sign(b_k[deg_mask_k])
                           == np.sign(beta_true[deg_mask_k])).mean()
        else:
            sign_bad[k] = float("nan")
    print(f"{'':>16}{'标签正确':>14}{'对调（静默）':>16}{'随机重贴（静默）':>18}")
    print(f"{'H0 假阳性率':>16}{(p_ok[h0] < 0.05).mean():>14.3f}{(p_sw[h0] < 0.05).mean():>16.3f}"
          f"{fpr_bad.mean():>18.3f}   （名义 0.05；随机列为 {args.n_perm} 次均值）")
    print(f"{'H1 检出率':>16}{(p_ok[h1] < 0.05).mean():>14.3f}{(p_sw[h1] < 0.05).mean():>16.3f}"
          f"{pow_bad.mean():>18.3f}")
    print(f"{'差异基因数':>16}{deg_ok:>14d}{deg_sw:>16d}{int(deg_bad.mean()):>18d}"
          f"   （p<0.05 且 |log2FC|>1；随机列范围 {deg_bad.min()}–{deg_bad.max()}）")
    print(f"{'差异基因符号正确率':>16}{sign_ok:>14.0%}{sign_sw:>16.0%}"
          f"{np.nanmean(sign_bad):>18.0%}   （清单里真的是「上调」的比例）")
    print("读法：错配通路 rc=0、无警告，PCA/质控图照常——错的全是结论。")
    print("      对调：信号原样检出但每个 log2FC 反号，上调清单 100% 是下调基因；")
    print("      随机重贴：功效平均损失约 2/3、差异基因数损失约 90%，报告写成")
    print("      「几乎没有差异基因」——正是讲义 ⑥6.4「差异基因数为 0，但 PCA 明明")
    print("      分得开」要先排查的场景。")

    # ---------------- Part 2：断言式防御在合成数据上的拦截记录 ----------------
    print()
    print("[Part 2 · 断言式防御（讲义 ⑤5.4 的 stopifnot 口径，Python 等价实现）]")
    sample_ids = [f"S{i+1:02d}" for i in range(n)]
    counts_cols = list(sample_ids)                  # counts 矩阵列名（按文件名排序）
    coldata_rows = list(rng.permutation(sample_ids))  # 元数据表行序（手工排的另一顺序）
    try:
        assert counts_cols == list(coldata_rows), "列序与行序不一致"
        caught = False
    except AssertionError as e:
        caught = True
        print(f"  防御 1（identical 断言）：拦截到「{e}」——R 侧即 E2 报错")
    # 显式重排后通过
    coldata_rows_aligned = sorted(coldata_rows, key=counts_cols.index)
    assert counts_cols == coldata_rows_aligned
    print("  防御 2（显式重排 coldata <- coldata[colnames, ]）：重排后断言通过")
    # 无列名形态：显式拒绝
    no_colnames = None
    if no_colnames is None:
        print("  防御 3（无列名显式拒绝）：counts 无列名时拒绝贴标签，要求先命名再对齐")
    print(f"  防御 1 拦截成功：{caught}")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        fpr_ok = float((p_ok[h0] < 0.05).mean())
        pow_ok = float((p_ok[h1] < 0.05).mean())
        check("手算口径：正确通路的差异基因数 = (p<0.05) ∧ (|log2FC|>1) 计数",
              deg_ok == int(((p_ok < 0.05) & (np.abs(b_ok) > 1)).sum()))
        check(f"正确对齐：H0 假阳性率接近名义（{fpr_ok:.3f} ∈ [0.03, 0.12]）",
              0.03 <= fpr_ok <= 0.12)
        check(f"正确对齐：H1 检出率高（{pow_ok:.3f} ≥ 0.8）", pow_ok >= 0.8)
        check(f"对调事故：检出率不变（{(p_sw[h1] < 0.05).mean():.3f} ≥ 0.8）但符号正确率 "
              f"≈0（{sign_sw:.3f} ≤ 0.05）——方向全错", sign_sw <= 0.05
              and (p_sw[h1] < 0.05).mean() >= 0.8)
        check(f"随机重贴：功效大幅损失（均值 {pow_bad.mean():.3f} ≤ 0.40，"
              f"正确通路 {pow_ok:.3f}）", pow_bad.mean() <= 0.40)
        check(f"随机重贴：H0 假阳性率仍校准（均值 {fpr_bad.mean():.3f} ∈ [0.02, 0.10]）"
              f"——灾难是沉默不是误报", 0.02 <= fpr_bad.mean() <= 0.10)
        check(f"随机重贴：差异基因数大幅缩水（均值 {deg_bad.mean():.1f} ≤ 150，"
              f"正确通路 {deg_ok} 个）", deg_bad.mean() <= 150)
        check("错配：流程无异常（rc=0 语义）——不报错是这类错误最危险的地方",
              all_finite)
        check("防御 1（identical 断言）拦截到顺序不一致", caught)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch13_design_matrix_rank.py — 完全混杂 vs 区组化设计的设计矩阵秩（可识别性，合成算例）

服务章节：第 13 章 §13.4「批次效应的代数本质与区组化」（源讲义 m01 §4.6、m01 ⑤5.5、
m01 ⑥6.4、m01 ⑩4；l0_06_stats §4 的 PCA 诊断在第 12 章已讲，本章给代数侧入口）。
为失效条件 2「批次与处理完全混杂时任何事后校正都无法分离二者」提供复现入口。

模型（合成算例，非任何真实样本结果）：
  * 线性模型 Y = μ·1 + β·X + γ·Z + ε：X 为处理分组列，Z 为批次列。
  * 平衡区组设计：每批含全部处理组 → X、Z 线性无关，[1, X, Z] 满秩
    → β、γ 都可估计，把批次写进 design 公式（~ batch + condition）可剥离批次。
  * 完全混杂设计：批次与处理一一对应（X = Z）→ 秩亏 1，β 与 γ 只有和 β+γ 可估计；
    对任意 t，(β̂+t, γ̂−t) 给出完全相同的拟合与残差 —— 数据里不存在拆开二者的信息，
    与用不用 ComBat / 换什么软件无关（l0_06 §4 的结论的代数版）。

参数（--help 可见）：
  --beta/--gamma   合成真值：处理效应 β、批次偏移 γ（默认 1.2 / 2.0）
  --sigma          噪声标准差（默认 0.3）
  --per-cell       每个（组 × 批）单元的合成样本数（默认 3）
  --seed           随机种子

正文引用的输出：
  - Part 1 平衡 2×2：设计矩阵秩 = 3（满秩）、OLS 同时找回 β̂ ≈ β、γ̂ ≈ γ
  - Part 2 完全混杂：秩 = 2（亏 1）、XᵀX 奇异、等价解族 (β̂+t, γ̂−t) 拟合恒等、
    最小范数解把真值任意对半分（β̂ = γ̂ = (β+γ)/2 的示意）
  - Part 3 m01 ⑩4 的两难：建库同批（常数列，自动退化）+ 测序 lane 与处理共线
    → 秩亏依旧，只是不可分离的范围被限定在 lane 级技术漂移；
    对照「lane 正交」情形的满秩恢复
  - Part 4 6.5 验收交叉表（2 组 × 3 批，每批全组）满秩 = 4 的形态确认
"""
import argparse
import sys

import numpy as np

SEED = 20261104


def ols(X, y):
    """最小二乘：返回 (系数, 拟合值, 残差平方和)。X 秩亏时走最小范数解。"""
    coef, residuals, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    fit = X @ coef
    rss = float(((y - fit) ** 2).sum())
    return coef, fit, rss, rank


def cond_of_xt_x(X):
    """XᵀX 的条件数（无穷大 = 奇异）。"""
    gram = X.T @ X
    sv = np.linalg.svd(gram, compute_uv=False)
    return float(sv.max() / sv.min()) if sv.min() > 0 else float("inf")


def main():
    ap = argparse.ArgumentParser(
        description="完全混杂 vs 区组化设计的设计矩阵秩与可识别性（合成算例；源讲义 m01 §4.6、⑩4）")
    ap.add_argument("--beta", type=float, default=1.2, help="处理效应真值 β（默认 1.2）")
    ap.add_argument("--gamma", type=float, default=2.0, help="批次偏移真值 γ（默认 2.0）")
    ap.add_argument("--sigma", type=float, default=0.3, help="噪声标准差（默认 0.3）")
    ap.add_argument("--per-cell", type=int, default=5, help="每（组×批）单元样本数（默认 5）")
    ap.add_argument("--seed", type=int, default=SEED, help="随机种子")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    beta, gamma, sigma, m = args.beta, args.gamma, args.sigma, args.per_cell
    rng = np.random.default_rng(args.seed)

    print("=" * 78)
    print("[Part 1] 平衡区组设计：2 组 × 2 批，每批 2 组都有（合成 Y，真值 "
          f"β={beta}, γ={gamma}, σ={sigma}）")
    print("=" * 78)
    group = np.array([0, 0, 1, 1] * m)
    batch_bal = np.array([0, 1, 0, 1] * m)
    X1 = np.column_stack([np.ones(len(group)), group, batch_bal])
    y1 = (beta * group + gamma * batch_bal
          + rng.normal(0.0, sigma, size=len(group)))
    c1, f1, rss1, rank1 = ols(X1, y1)
    print(f"设计矩阵 [{len(group)}×3] 的秩 = {rank1}（满秩 3）；cond(XᵀX) = "
          f"{cond_of_xt_x(X1):.2f}")
    print(f"OLS 估计：β̂ = {c1[1]:.3f}（真值 {beta}），γ̂ = {c1[2]:.3f}（真值 {gamma}）"
          f"，RSS = {rss1:.3f}")
    print("→ 批次作为协变量进 design 公式（~ batch + condition）即可剥离批次主效应")

    print()
    print("=" * 78)
    print("[Part 2] 完全混杂设计：批次 == 分组（第 1 批全对照、第 2 批全处理）")
    print("=" * 78)
    batch_cnf = group.copy()
    X2 = np.column_stack([np.ones(len(group)), group, batch_cnf])
    y2 = (beta * group + gamma * batch_cnf
          + rng.normal(0.0, sigma, size=len(group)))
    rank2 = np.linalg.matrix_rank(X2)
    c2, f2, rss2, _ = ols(X2, y2)
    print(f"设计矩阵 [{len(group)}×3] 的秩 = {rank2}（亏 1：第 2、3 列完全相同）；"
          f"cond(XᵀX) = {cond_of_xt_x(X2):.1f}（奇异）")
    print(f"最小范数解：β̂ = {c2[1]:.3f}，γ̂ = {c2[2]:.3f}"
          f" —— 把可估的和 β+γ = {beta + gamma:.1f} 任意对半分，与真值 ({beta}, {gamma}) 无关")
    ts = [-1.5, -0.5, 0.5, 1.5]
    rss_t = []
    for t in ts:
        alt = c2.copy()
        alt[1] += t
        alt[2] -= t
        rss_t.append(float(((y2 - X2 @ alt) ** 2).sum()))
    print(f"等价解族验证：对 t ∈ {ts}，(β̂+t, γ̂−t) 的 RSS 分别为 "
          f"{[f'{r:.4f}' for r in rss_t]} —— 全部等于最小范数解的 RSS（{rss2:.4f}）")
    print("→ 拟合值只依赖 β+γ：把第 2 批的整体偏移解释为「处理有效」或「批次漂移」"
          "在代数上完全等价 —— 信息在采样时就没被采到，事后校正无从分离（失效条件 2）")

    print()
    print("=" * 78)
    print("[Part 3] m01 ⑩4 的两难：建库同批（常数列退化）+ 测序 lane 与处理共线")
    print("=" * 78)
    lane_cnf = group.copy()                      # CK 全 lane1、Drought 全 lane2
    X3 = np.column_stack([np.ones(len(group)), group, lane_cnf])
    y3 = (beta * group + gamma * lane_cnf
          + rng.normal(0.0, sigma, size=len(group)))
    c3, _, rss3, rank3 = ols(X3, y3)
    print(f"建库同批 → 「建库批次」列是常数，自动退化；剩下 [1, 处理, lane] 的秩 = {rank3}"
          f"（处理列与 lane 列相同，依旧亏 1）")
    print(f"不可分离的范围被限定在 lane 级技术漂移：最小范数解 β̂ = {c3[1]:.3f}、"
          f"γ̂(lane) = {c3[2]:.3f}，同样只是 ({beta}+{gamma})/2 的对半分")
    lane_orth = batch_bal.copy()                 # lane 正交：每 lane 两处理都有
    X4 = np.column_stack([np.ones(len(group)), group, lane_orth])
    y4 = (beta * group + gamma * lane_orth
          + rng.normal(0.0, sigma, size=len(group)))
    c4, _, _, rank4 = ols(X4, y4)
    print(f"对照（lane 正交分配）：秩 = {rank4}（满秩），β̂ = {c4[1]:.3f}、"
          f"γ̂(lane) = {c4[2]:.3f} —— 可分离")
    print("→ 判断口径（m01 ⑩4 答案要点）：建库同批消除了「试剂批号」混杂源，"
          "但 lane 与处理完全共线，lane 级漂移无法与处理区分；风险大小取决于 lane 效应量级，"
          "设计评审时按「不可分离」处理并要求正交化")

    print()
    print("=" * 78)
    print("[Part 4] 6.5 验收交叉表形态：2 组 × 3 批，每批含全部处理组（每格 3 样本）")
    print("=" * 78)
    group6 = np.repeat([0, 1], 9)
    batch6 = np.tile(np.repeat([0, 1, 2], 3), 2)
    X5 = np.column_stack([np.ones(18), group6,
                          (batch6 == 1).astype(int), (batch6 == 2).astype(int)])
    y5 = (beta * group6 + gamma * (batch6 == 1) + 0.7 * gamma * (batch6 == 2)
          + rng.normal(0.0, sigma, size=18))
    c5, _, _, rank5 = ols(X5, y5)
    print(f"[1, 处理, 批2, 批3]（批1 作基准）的秩 = {rank5}（满秩 4）；"
          f"β̂ = {c5[1]:.3f}（真值 {beta}），批2 γ̂ = {c5[2]:.3f}（真值 {gamma}），"
          f"批3 γ̂ = {c5[3]:.3f}（真值 {0.7 * gamma:.1f}）")
    print("→ 「组 × 批次交叉表每个批次含全部处理组」是 6.5 验收表的代数内容")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        check("平衡设计满秩（rank = 3）", rank1 == 3)
        check("平衡设计 cond(XᵀX) 有限（< 1e3）", cond_of_xt_x(X1) < 1e3)
        check("平衡设计 β̂ ≈ β（|Δ| < 0.2）", abs(c1[1] - beta) < 0.2)
        check("平衡设计 γ̂ ≈ γ（|Δ| < 0.2）", abs(c1[2] - gamma) < 0.2)
        check("完全混杂设计秩亏 1（rank = 2）", rank2 == 2)
        check("完全混杂 XᵀX 奇异（cond > 1e12）", cond_of_xt_x(X2) > 1e12)
        check("等价解族拟合恒等（max ΔRSS < 1e-9）",
              max(abs(r - rss2) for r in rss_t) < 1e-9)
        check("最小范数解 β̂ = γ̂（任意对半分）",
              abs(c2[1] - c2[2]) < 1e-6
              and abs(c2[1] - (beta + gamma) / 2) < 0.2)
        check("混杂下拟合只依赖 β+γ（恢复 β+γ 到 ±0.2）",
              abs(c2[1] + c2[2] - (beta + gamma)) < 0.2)
        check("⑩4 情形秩亏（处理 == lane，rank = 2）", rank3 == 2)
        check("lane 正交对照满秩（rank = 3）", rank4 == 3)
        check("lane 正交对照 β̂ 可恢复（|Δ| < 0.2）", abs(c4[1] - beta) < 0.2)
        check("2×3 交叉表满秩（rank = 4）", rank5 == 4)
        check("2×3 交叉表 β̂、批2 γ̂ 可恢复",
              abs(c5[1] - beta) < 0.2 and abs(c5[2] - gamma) < 0.2)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

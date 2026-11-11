#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch14_reversed_reflevel.py — 对照组水平设反：log2FC 符号静默翻转（合成算例）

服务章节：第 14 章 §14.4 概念与方法（设计矩阵与参考水平）、§14.5 失效条件第 3 条
「对照组水平设反使 log2FC 方向颠倒」。源讲义：m04 ⑨-E6、§4.3.3、⑦-2。
机制（讲义 ⑦-2 + CH14_EXPERT_001 跑⑤实证）：R 因子水平默认按字母序，
results() 默认报「最后一个水平 vs 第一个水平」的系数；若处理名恰好排在对照名前
（讲义设例：KO < WT），默认结果就是 WT vs KO——每个 log2FC 与预期反号，且**不报错**。
DESeq2 的自查提示：最后一个设计变量的水平含 control/Control/CONTROL 且非参考水平时，
DESeqDataSet 构造会 message 提示（专家跑 DESeqDataSet 源码 controlSynonyms 确认）——
本脚本以文本记录该行为，不调用 R。

模型（合成，非 PRJDB36269 或任何真实样本）：
  * 2 组 × 每组 n=6 个「样本」（组名用 K=对照 / N=复氮，对齐贯穿数据命名）；
  * n_gene 个「基因」：半数 H0（β=0），半数 H1（|log2FC|=1.5，方向各半）；
  * 计数 Y ~ NB(size=1/α, μ = μ_i·2^{β_i·x_j})，α=0.15；
  * 检验：负二项 log-GLM（无 offset，平衡设计），Wald 检验。
  * 两条通路唯一差别：因子水平顺序——「显式 relevel(ref=control) + contrast」
    vs 「默认字母序 accidents」（让对照名排在处理名之后，模拟 KO/WT 式事故）。

参数（--help 可见）：
  --n-gene / --n-rep   基因数与每组样本数（默认 2400 / 6）
  --alpha              NB 离散度（默认 0.15）
  --seed               随机种子（默认 20260829，对齐 m04 脚本 set.seed(20260829) 的结构）

正文引用的输出：
  - Part 1：正确参考水平 vs 设反参考水平下，H1 基因 log2FC 估计的符号正确率
    （正确 ≈100%，设反 ≈0%）与「N 上调基因清单」的成分（设反时 100% 是下调基因）；
    显著性名单（padj/p 口径）完全不变——收缩、富集照旧，只有方向全反
  - Part 2：下游连锁后果——按符号分组的「上调清单」拿去做 ORA 时上下调必须分开做
    （讲义 ⑥6.4），方向反了等于拿下调基因当上调富集；以及两行防御代码
    （relevel + 显式 contrast / 读 mcols(res)$description[2]）在合成数据上的拦截记录

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
    信息阵 I = X'WX、W = diag(μ/(1+α·μ))；更新 beta += I⁻¹U。
    x 为 0/1 分组，β1 即「x=1 组 vs x=0 组」的 log2 倍数变化——x 的编码即参考水平。"""
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


def main():
    ap = argparse.ArgumentParser(
        description="对照组水平设反使 log2FC 静默翻转（合成算例；服务第 14 章失效"
                    "条件 3，对齐讲义 m04 ⑨-E6）")
    ap.add_argument("--n-gene", type=int, default=2400)
    ap.add_argument("--n-rep", type=int, default=6, help="每组样本数（默认 6）")
    ap.add_argument("--alpha", type=float, default=0.15)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    # ---------------- Part 0：机制（讲义 ⑦-2 / ⑨-E6 的算术化） ----------------
    print("=" * 78)
    print("[Part 0 · 机制] results() 默认报「最后水平 vs 首水平」；字母序决定谁是首水平")
    print("=" * 78)
    print("  例：因子水平 c(\"KO\",\"WT\")（字母序）→ 默认结果 = WT vs KO")
    print("  一个真值为「KO 高 WT 低」的基因，log2FC 被报成负数——方向反了，不报错。")
    print("  专家现跑（跑⑤，DESeq2 1.50.2）：该设例默认 lfc = −3.093（反号实证）。")
    print("  对齐贯穿数据：处理 = 复氮(N)、对照 = 对照(K)；K < N 字母序碰巧正确——")
    print("  「碰巧正确」正是事故的土壤：换一个命名（如 N_resupply vs ctrl）即翻转。")

    # ---------------- 合成数据 ----------------
    rng = np.random.default_rng(args.seed)
    n = 2 * args.n_rep
    x = np.concatenate([np.zeros(args.n_rep), np.ones(args.n_rep)])  # 0=对照K, 1=复氮N
    ng = args.n_gene
    half = ng // 2
    beta_true = np.concatenate([np.zeros(half), np.full(ng - half, 1.5)])
    beta_true[half + rng.permutation(ng - half)[: (ng - half) // 2]] = -1.5
    mu_base = rng.lognormal(mean=np.log(800.0), sigma=1.5, size=ng)
    mu = mu_base[:, None] * 2.0 ** (beta_true[:, None] * x[None, :])
    y = rng.negative_binomial(1.0 / args.alpha,
                              (1.0 / args.alpha) / (1.0 / args.alpha + mu),
                              mu.shape)
    h1 = beta_true != 0

    # ---------------- Part 1：两条通路的唯一差别是 x 的编码方向 ----------------
    print()
    print("=" * 78)
    print(f"[Part 1 · 合成算例] {ng} 基因 × 2 组 × {args.n_rep} 样本；α={args.alpha}，"
          f"seed={args.seed}（H1 基因真值 |log2FC| = 1.5，方向各半）")
    print("=" * 78)
    # 正确通路：x = 0(对照) / 1(处理)，β1 = 「处理 vs 对照」
    b_ok = np.empty(ng)
    p_ok = np.empty(ng)
    # 设反通路：x_rev = 1(对照) / 0(处理)，β1_rev = 「对照 vs 处理」= −β1（不报错）
    b_rev = np.empty(ng)
    p_rev = np.empty(ng)
    for i in range(ng):
        b_ok[i], p_ok[i] = nb_glm_wald(y[i].astype(float), x, args.alpha)
        b_rev[i], p_rev[i] = nb_glm_wald(y[i].astype(float), 1.0 - x, args.alpha)
    sig_ok = p_ok < 0.05
    sig_rev = p_rev < 0.05
    up_ok = sig_ok & (b_ok > 1)          # 「N 上调」清单（正确口径）
    up_rev = sig_rev & (b_rev > 1)       # 「N 上调」清单（设反口径）
    sign_correct = float((np.sign(b_ok[h1]) == np.sign(beta_true[h1])).mean())
    sign_rev = float((np.sign(b_rev[h1]) == np.sign(beta_true[h1])).mean())
    up_rev_true_dir = float((np.sign(beta_true[up_rev]) > 0).mean()) if up_rev.any() else float("nan")
    print(f"{'':>18}{'正确（relevel+contrast）':>26}{'设反（默认字母序）':>22}")
    print(f"{'H1 符号正确率':>18}{sign_correct:>26.1%}{sign_rev:>22.1%}")
    print(f"{'显著基因数':>18}{sig_ok.sum():>26d}{sig_rev.sum():>22d}"
          f"   （p<0.05 口径）")
    print(f"{'「N 上调」清单数':>18}{up_ok.sum():>26d}{up_rev.sum():>22d}"
          f"   （p<0.05 且 log2FC>1）")
    print(f"{'清单方向正确率':>18}"
          f"{float((np.sign(beta_true[up_ok]) > 0).mean()):>25.0%}"
          f"{up_rev_true_dir:>22.0%}   （清单里真为上调的比例）")
    print("读法：两条通路的 p 值逐位相同（检验对符号翻转不变），显著名单一模一样；")
    print("      唯一变的是 log2FC 的符号——设反时「N 上调」清单 100% 由下调基因组成。")

    # ---------------- Part 2：下游连锁与两行防御 ----------------
    print()
    print("[Part 2 · 下游连锁与防御]")
    print("  连锁：讲义 ⑥6.4 要求上调/下调分开富集；方向反了 = 拿下调基因当上调做 ORA，")
    print("        富集出的通路生物学解释全部南辕北辙——而 padj 完全正常。")
    print("  防御 1（建 dds 前）：coldata$condition <- relevel(factor(condition), ref = \"K\")")
    print("  防御 2（取结果时）：contrast = c(\"condition\", \"N\", \"K\")")
    print("  防御 3（拿到表后）：读 mcols(res)$description[2]，应写明 \"condition N vs K\"；")
    print("        DESeq2 对含 control 同义词的非参考水平会 message 提示（controlSynonyms）。")
    contrast_str_ok = "condition N vs K"
    contrast_str_rev = "condition K vs N"
    print(f"  本脚本正确通路 contrast 字符串：「{contrast_str_ok}」；"
          f"设反通路实际报告：「{contrast_str_rev}」")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        check("正确通路：H1 符号正确率 ≈100%（{:.1%} ≥ 99%）".format(sign_correct),
              sign_correct >= 0.99)
        check(f"设反通路：H1 符号正确率 ≈0（{sign_rev:.1%} ≤ 1%）——静默翻转",
              sign_rev <= 0.01)
        check(f"设反通路：p 值与正确通路逐位一致（max |Δp| = "
              f"{float(np.max(np.abs(p_ok - p_rev))):.1e} ≤ 1e-12）——显著名单不变",
              float(np.max(np.abs(p_ok - p_rev))) <= 1e-12)
        check(f"设反通路：log2FC 精确反号（max |β_ok + β_rev| = "
              f"{float(np.max(np.abs(b_ok + b_rev))):.1e} ≤ 1e-8）",
              float(np.max(np.abs(b_ok + b_rev))) <= 1e-8)
        check(f"设反通路的「N 上调」清单 100% 是下调基因（方向正确率 {up_rev_true_dir:.0%}）",
              up_rev_true_dir <= 0.01)
        check("正确通路的「N 上调」清单 ≈100% 真上调",
              float((np.sign(beta_true[up_ok]) > 0).mean()) >= 0.99)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch14_tpm_rounding.py — 把 TPM/FPKM 取整喂给负二项 GLM：方差模型失效、Wald 检验失准（合成算例）

服务章节：第 14 章 §14.4 概念与方法（归一化与 DESeq2 输入纪律）、§14.5 失效条件第 1 条
「把 TPM/FPKM 取整喂给 DESeq2 不一定报错，但方差模型已失效」。源讲义：m04 §4.2、⑨-E3。
DESeq2 的真实报错/提示行为属 R 包内部，本脚本用同结构统计模型（负二项 log 连接 GLM +
固定离散度 + Wald 检验）复现「同一批数据，raw counts  vs round(TPM) 两种喂法」的后果；
讲义断言 `round(tpm)` 后 DESeq2 只打印一句 `converting counts to integer mode` 照跑，
此行为以讲义 ⑨-E3 原文为准（本脚本不调用 R）。

模型（全部为合成模型，非 PRJDB36269 或任何真实样本结果）：
  * 2 组 × 每组 n=6 个「样本」，组内文库深度差异大（size factor 0.4–3.0，
    两组配置镜像，深度与分组不相关——排除组成性偏差的干扰，只暴露「喂错矩阵」本身）；
  * n_gene 个「基因」：基础丰度 μ_i ~ 对数正态；半数基因 H0（β=0），半数 H1（|log2FC|=1.5）；
  * 原始计数 Y ~ NB(size=1/α, μ = s_j·μ_i·2^{β_i·x_j})，α = 0.15（生物学重复口径）；
  * TPM 通路：TPM_ij = Y_ij / (len_i[kb] · N_j) × 1e6，N_j = 样本 j 的实测总读数
    （对齐课程降采样后每样本 300 万条 read 的量级，06_data/master/README.md），再取整
    ——即 E3 的 `round(tpm)`；长度 len_i ~ 对数正态（均值 2 kb，纯合成）。
  * 检验：每组基因按矩估计离散度 α̂ = max((var−mean)/mean², 1e-4)（offset 校正后），
    负二项 GLM（log 连接，IRLS）拟合 β0+β1·x，Wald 检验 H0: β1=0。
    同一份数据、同一个检验器，唯一差别是输入矩阵。

参数（--help 可见）：
  --n-gene / --n-rep   基因数与每组样本数（默认 4000 / 6；n 太小矩估计 α̂ 抖动大，
                       raw 通路自身校准变差，对照失去意义）
  --alpha              NB 离散度（默认 0.15）
  --seed               随机种子（默认 20260829，对齐 m04 脚本 set.seed(20260829) 的结构）

正文引用的输出：
  - Part 0 手算规则：1 read @ 1M 文库 与 100 reads @ 100M 文库 TPM 相同，
    泊松变异系数 1/√c：100% vs 10%（讲义 §4.2 数值的复现入口）
  - Part 1：同一合成数据集 raw counts vs round(TPM) 的 H0 假阳性率（名义 0.05）与
    H1 检出率——round(TPM) 通路的 p 值不再可校准（可升可降，方向取决于深度配置，
    与 raw 通路对照即「失准幅度」）
  - Part 2：深度证据消失检验——median-of-ratios 对 round(TPM) 的 size factor 全部
    ≈1（讲义 ⑨-E3「趋近 1」的复现），而真实文库大小因子跨 7.5 倍；浅/深文库组内
    方差比在两通路都 ≈1（均值与方差层面的深度差都被 TPM 抹平）——失明的不是方差，
    而是「每个样本带多少证据」的权重信息（offset≈0 后深/浅样本被等量加权）
    （实现注记：TPM 通路的失准幅度依赖检验器实现，方向与「不可校准」结论稳健；
    本脚本固定种子、输出确定，正文引用以本脚本现跑输出为准）

依赖：Python 标准库 + numpy + scipy。
合成算例：所有「基因表达计数」均为随机数生成器产物，与任何真实样本无关。
"""
import argparse
import sys

import numpy as np
from scipy import stats

SEED = 20260829  # 对齐 m04 脚本 set.seed(20260829)（结构对齐；RNG 不同）


def nb_glm_wald(y, x, offset, alpha):
    """负二项 log-GLM（带步长回退的 Fisher scoring），返回 β1 与 Wald p。
    y: (n,) 计数；x: (n,) 0/1；offset: (n,) log 文库因子；alpha: 固定离散度。
    得分 U_k = Σ x_k·(y−μ)/(1+α·μ)（NB 方差函数 μ+αμ² 的权重 μ/V = 1/(1+αμ)），
    信息阵 I = X'WX、W = diag(μ/(1+α·μ))；更新 beta += I⁻¹U——offset 只进 eta，
    不出现在响应变量里（讲义 §4.3.3：s_j 以 offset 形式进入 GLM）；
    步长按 ||U|| 单调不增回退，防止低计数基因 + 小 alpha 时发散。"""
    X = np.column_stack([np.ones_like(x), x])

    def score_at(b):
        mu = np.exp(np.clip(X @ b + offset, -30.0, 30.0))
        w = mu / (1.0 + alpha * mu)
        H = (X.T * w) @ X
        return H, X.T @ ((y - mu) / (1.0 + alpha * mu))

    beta = np.linalg.lstsq(X, np.log(np.maximum(y, 0.1)) - offset, rcond=None)[0]
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
    mu = np.exp(np.clip(X @ beta + offset, -30.0, 30.0))
    w = mu / (1.0 + alpha * mu)
    H = (X.T * w) @ X
    cov = np.linalg.inv(H)
    se = np.sqrt(max(cov[1, 1], 1e-16))
    z = beta[1] / se
    p = 2.0 * stats.norm.sf(abs(z))
    return beta[1], p


def moment_alpha(y, offset):
    """offset 校正后的矩估计离散度 max((var-mean)/mean^2, 1e-4)。"""
    mu = np.exp(np.log(np.maximum(y, 1e-6)) - offset).mean()
    var = np.exp(np.log(np.maximum(y, 1e-6)) - offset).var(ddof=1)
    return max((var - mu) / max(mu, 1e-12) ** 2, 1e-4)


def median_of_ratios(mat):
    """DESeq2 的 median-of-ratios size factor：基因几何均值为伪参考样本，
    取每样本计数/伪参考比值的中位数。mat: (n_gene, n) 非负矩阵。"""
    pos = mat[mat.sum(axis=1) > 0]
    geo = np.exp(np.log(np.maximum(pos, 1e-6)).mean(axis=1))
    return np.median(pos / geo[:, None], axis=0)


def run_path(y, x, offset, log_offset):
    """对 (n_gene, n) 矩阵逐基因估计 α̂ 并做 Wald 检验，返回 p 值与 α̂ 数组。"""
    pvals, alphas = np.empty(y.shape[0]), np.empty(y.shape[0])
    for i in range(y.shape[0]):
        a = moment_alpha(y[i], log_offset)
        alphas[i] = a
        _, p = nb_glm_wald(y[i].astype(float), x, offset, a)
        pvals[i] = p
    return pvals, alphas


def main():
    ap = argparse.ArgumentParser(
        description="TPM/FPKM 取整喂 NB-GLM 的失准演示（合成算例；服务第 14 章失效条件 1，"
                    "对齐讲义 m04 §4.2 与 ⑨-E3）")
    ap.add_argument("--n-gene", type=int, default=4000)
    ap.add_argument("--n-rep", type=int, default=6, help="每组样本数（默认 6）")
    ap.add_argument("--alpha", type=float, default=0.15)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    # ---------------- Part 0：手算规则（讲义 §4.2 的算术复现） ----------------
    print("=" * 78)
    print("[Part 0 · 手算规则] TPM 相同 ≠ 统计证据相同（讲义 §4.2 的场景算术化）")
    print("=" * 78)
    # 前提（CNT-CH14-02）：TPM = (c/L) / Σ(c_j/L_j) × 1e6。只有当全部基因有效长度
    # 相等（此处均取 L = 1 kb）时，样本 RPK 总和 Σ(c_j/L_j) 才等于文库读段总数，
    # TPM 才退化成「计数 / 文库大小 × 1e6」。长度或组成不同则不能这样推。
    print("  前提：全部基因有效长度相等（均取 1 kb）→ 样本 RPK 总和 = 文库读段总数，")
    print("        TPM = 计数 / 文库大小 × 1e6；长度或其余基因组成不同时此式不成立")
    def tpm_of(c, l_kb, rpk_sum):
        return c / l_kb / rpk_sum * 1e6

    # 等长：RPK 总和 = 文库读段总数（1e6 与 100e6）
    tpm_a = tpm_of(1, 1.0, 1e6 / 1.0)  # 1 read @ 1M 文库 → 相对丰度 1e-6
    tpm_b = tpm_of(100, 1.0, 100e6 / 1.0)
    # 反例：B 中其余基因有效长度均为 2 kb → RPK 总和约减半，TPM 不再等于 A
    tpm_b_unequal = tpm_of(100, 1.0, 100 / 1.0 + (100e6 - 100) / 2.0)
    print(f"  样本 A（1M 文库）1 read：相对丰度 = {1 / 1e6:.2e} → TPM = {tpm_a:.0f}")
    print(f"  样本 B（100M 文库）100 reads：相对丰度 = {100 / 100e6:.2e} → TPM = {tpm_b:.0f}")
    print(f"  两样本 TPM 相等：{abs(tpm_a - tpm_b) < 1e-9}")
    print(f"  泊松变异系数 1/√c：A = {1 / np.sqrt(1):.0%}，B = {1 / np.sqrt(100):.0%}"
          " —— TPM 把证据差 10 倍的信息抹平了")
    print(f"  反例（B 中其余基因均为 2 kb）：B 的 TPM = {tpm_b_unequal:.2f} ≠ A —— 等长前提不可省")

    # ---------------- 合成数据 ----------------
    rng = np.random.default_rng(args.seed)
    n = 2 * args.n_rep
    x = np.concatenate([np.zeros(args.n_rep), np.ones(args.n_rep)])
    # 组内深度差异大、两组配置镜像（深度与分组不相关，排除组成性干扰）：
    # 基础向量 tile 后两组天然同多重集，只在组内各自打乱（不打乱全体，
    # 否则随机置换会把深度与分组偶然混杂，违背设计意图）
    s = np.tile(np.array([0.4, 0.5, 0.7, 1.5, 2.0, 3.0]), 2)
    s[: args.n_rep] = s[: args.n_rep][rng.permutation(args.n_rep)]
    s[args.n_rep:] = s[args.n_rep:][rng.permutation(args.n_rep)]
    log_s = np.log(s)
    half = args.n_gene // 2
    beta = np.concatenate([np.zeros(half), np.full(args.n_gene - half, 1.5)])
    beta[rng.permutation(args.n_gene)[: args.n_gene // 4]] *= -1  # 四分之一下调
    mu_base = rng.lognormal(mean=np.log(800.0), sigma=1.5, size=args.n_gene)
    len_kb = rng.lognormal(mean=np.log(2.0), sigma=0.5, size=args.n_gene)
    mu = mu_base[:, None] * s[None, :] * 2.0 ** (beta[:, None] * x[None, :])
    y = rng.negative_binomial(1.0 / args.alpha,
                              (1.0 / args.alpha) / (1.0 / args.alpha + mu),
                              mu.shape)
    # TPM 通路：长度 ÷ 深度 × 1e6，再取整（= 讲义 ⑨-E3 的 round(tpm)）
    n_j = y.sum(axis=0, keepdims=True)
    tpm = y / (len_kb[:, None] * n_j) * 1e6
    tpm_round = np.rint(tpm)

    # ---------------- Part 1：同一份数据，两种喂法 ----------------
    print()
    print("=" * 78)
    print(f"[Part 1 · 合成算例] {args.n_gene} 基因 × 2 组 × {args.n_rep} 样本；"
          f"文库因子 {np.sort(np.round(s, 1)).tolist()}（α={args.alpha}，seed={args.seed}）")
    print("=" * 78)
    p_raw, _ = run_path(y, x, log_s, log_s)
    p_tpm, _ = run_path(tpm_round, x, np.zeros(n), np.zeros(n))
    h0 = beta == 0
    h1 = ~h0
    fpr_raw = float((p_raw[h0] < 0.05).mean())
    fpr_tpm = float((p_tpm[h0] < 0.05).mean())
    pow_raw = float((p_raw[h1] < 0.05).mean())
    pow_tpm = float((p_tpm[h1] < 0.05).mean())
    print(f"{'':>18}{'raw counts（合法输入）':>26}{'round(TPM)（失效条件 1）':>28}")
    print(f"{'H0 假阳性率':>18}{fpr_raw:>26.3f}{fpr_tpm:>28.3f}   （名义 0.05）")
    print(f"{'H1 检出率':>18}{pow_raw:>26.3f}{pow_tpm:>28.3f}")
    print("读法：同一检验器、同一批基因，唯一差别是输入矩阵。raw 通路接著名义水平；")
    print("      round(TPM) 通路的假阳性率/检出率偏离对照——方差结构已坏，p 值不再可校准。")

    # ---------------- Part 2：深度证据的消失（size factor ≈ 1 的失明） ----------------
    print()
    print("[Part 2 · 深度证据的消失：median-of-ratios 对 round(TPM) 失明]")
    shallow = s < 1.0
    deep = s > 1.0
    sf_tpm = median_of_ratios(tpm_round)
    s_rel = s / np.exp(np.log(s).mean())
    print(f"  真实文库大小因子（相对几何均值）：{[round(float(v), 2) for v in s_rel]}（跨 "
          f"{s_rel.min():.2f}–{s_rel.max():.2f}，最深/最浅 = {s_rel.max()/s_rel.min():.1f} 倍）")
    print(f"  median-of-ratios 对 round(TPM) 的估计：{[round(float(v), 2) for v in sf_tpm]}"
          f"（全部 ≈1：讲义 ⑨-E3「size factor 趋近 1」的复现）")
    # 均值（乃至方差）层面的深度差确实被 TPM 抹平——这正是 TPM 作为表达量读数的设计目的；
    # 统计推断要的不是把深度从均值里除掉，而是知道每个样本带了多少证据
    rel_tpm = tpm_round / np.maximum(tpm_round.mean(axis=1, keepdims=True), 1e-12)
    v_tpm_sh = rel_tpm[:, shallow].var(axis=1, ddof=1)
    v_tpm_dp = rel_tpm[:, deep].var(axis=1, ddof=1)
    m_tpm = (v_tpm_sh > 0) & (v_tpm_dp > 0) & (tpm_round.mean(axis=1) > 0)
    var_ratio_tpm = float(np.median(v_tpm_sh[m_tpm] / v_tpm_dp[m_tpm]))
    rel_raw = y / s / np.maximum((y / s).mean(axis=1, keepdims=True), 1e-12)
    v_raw_sh = rel_raw[:, shallow].var(axis=1, ddof=1)
    v_raw_dp = rel_raw[:, deep].var(axis=1, ddof=1)
    m_raw = (v_raw_sh > 0) & (v_raw_dp > 0)
    var_ratio_raw = float(np.median(v_raw_sh[m_raw] / v_raw_dp[m_raw]))
    print(f"  浅/深文库组内方差比中位数（H0 基因）：raw {var_ratio_raw:.2f} / "
          f"round(TPM) {var_ratio_tpm:.2f} —— 均值与方差层面的深度差都被 TPM 抹平")
    print("读法：raw 通路用 offset 保住「每样本证据量」，检验按证据加权；round(TPM) 让")
    print("      offset≈0、size factor≈1，深文库的高证据与浅文库的低证据被等量加权——")
    print(f"      Part 1 的失准（假阳性率 {fpr_raw:.3f}→{fpr_tpm:.3f}、检出率 {pow_raw:.3f}→{pow_tpm:.3f}）即由此而来。")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        check("手算规则：1 read@1M 与 100 reads@100M 的 TPM 均为 1，CV 100% vs 10%",
              abs(tpm_a - tpm_b) < 1e-9 and abs(1 / np.sqrt(1) - 1.0) < 1e-12
              and abs(1 / np.sqrt(100) - 0.1) < 1e-12)
        check(f"等长前提：其余基因改为 2 kb 时 B 的 TPM = {tpm_b_unequal:.2f} ≠ 1",
              abs(tpm_b_unequal - 1.0) > 0.5)
        check(f"raw counts 通路 H0 假阳性率接近名义 0.05（{fpr_raw:.3f} ∈ [0.03, 0.12]，"
              f"上限放宽到 0.12：n=12 + 单基因矩估计离散度的 Wald 可偏乐观，DESeq2 的跨基因收缩"
              f"正是为压这个）",
              0.03 <= fpr_raw <= 0.12)
        check(f"round(TPM) 通路失准幅度 ≥3× raw 通路"
              f"（|{fpr_tpm:.3f}−0.05| = {abs(fpr_tpm - 0.05):.3f} vs "
              f"|{fpr_raw:.3f}−0.05| = {abs(fpr_raw - 0.05):.3f}）",
              abs(fpr_tpm - 0.05) >= 3 * abs(fpr_raw - 0.05))
        check(f"round(TPM) 通路 H1 检出率低于 raw 通路（{pow_tpm:.3f} < {pow_raw:.3f}）",
              pow_tpm < pow_raw)
        check(f"raw 通路深度已校正（Var比 {var_ratio_raw:.2f} ∈ [0.5, 2]）",
              0.5 <= var_ratio_raw <= 2.0)
        check(f"round(TPM) 的 size factor 全部 ≈1（{sf_tpm.min():.2f}–{sf_tpm.max():.2f} ⊆ "
              f"[0.85, 1.20]）而真实深度因子跨 {s_rel.max()/s_rel.min():.1f} 倍",
              0.85 <= float(sf_tpm.min()) and float(sf_tpm.max()) <= 1.20
              and s_rel.max() / s_rel.min() >= 5.0)
        check(f"round(TPM) 均值/方差层面深度已抹平（Var比 {var_ratio_tpm:.2f} ∈ [0.5, 2]）"
              f"——失明的是证据权重，不是方差比本身",
              0.5 <= var_ratio_tpm <= 2.0)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

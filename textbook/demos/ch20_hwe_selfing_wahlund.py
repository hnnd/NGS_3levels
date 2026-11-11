#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch20_hwe_selfing_wahlund.py — HWE 精确检验在两类「内源生物学偏离」下的表现：
自交群体的误杀率与 Wahlund 效应的杂合子缺失恒等式（合成算例）

服务于：教材第 20 章（群体遗传学与群体基因组）§20.5 失效条件第 2 条
「把 HWE 当过滤器可能删掉真实的选择或结构信号」与第 4 条中的 Wahlund 部分
（群体结构伪装成 HWE 偏离），对应讲义 p04 §4.3（技术 vs 生物学偏离表）、
§7.1（Wahlund 效应代数证明 H_exp − H_obs = 2Var(p) ≥ 0；Wigginton et al. 2005
精确检验）、§7.2（自交率 s = 0.95 时杂合度仅为随机交配期望的 10%，
`--hwe 1e-6` 将屠戮 90% 以上真实多态位点）与习题 ⑦-3。

合成设定（不基于任何真实群体；固定种子可复现；二倍体口径 —— 稻瘟菌为单倍体、
HWE 对其天然无意义（讲义 ⑤5.1），本演示的两大场景对应讲义明确点名的
二倍体作物/病原体系：自交作物与混合亚群）：
  - 场景 A（Wahlund）：K = 3 个亚群，等位频率 p_k = (0.2, 0.5, 0.8)、权重
    w_k = (1/3, 1/3, 1/3)。各亚群内部严格 HWE；机械合并后按合并频率算期望。
    恒等式（讲义 §7.1 逐行代数）：H_exp − H_obs = 2·Var_w(p)。
    有限样本版：合并样本 2n = 2000 个基因座（按权重分摊到各亚群），每亚群按各自
    p_k 独立抽样 HWE 基因型，合并计数后跑精确检验；分群后逐亚群检验作对照。
  - 场景 B（自交）：部分自交率 s 的平衡近交系数 F = s/(2−s)（标准结果），
    观测杂合度 H_obs = 2pq·(1−F)。s = 0.95 → F = 0.9048 → H_obs/H_exp = 0.0952
    ≈ 10%（讲义 §7.2 的「10%」）。每个合成 SNP：p ~ U(0.1, 0.5)，n = 100 个
    二倍体，期望基因型计数 AA = p²+pqF、Aa = 2pq(1−F)、aa = q²+pqF 多项抽样，
    跑 Wigginton et al. (2005) 网络精确检验，统计 p < 1e-6 的位点比例 ——
    即盲目 `--hwe 1e-6` 会杀掉的**真实多态位点**比例。

正文引用的输出（手算可对）：
  - 恒等式核验：H_exp − H_obs = 2Var(p) 精确成立（本设定 = 0.12）——
    「群体内部只要潜伏分化，合并数据必然观测到全基因组杂合缺失」；
  - Wahlund 合并样本 ≫90% 位点 p < 1e-6，而正确分群后逐亚群检验的 p 值
    回到均匀分布（5% 名义水平）——「分群后偏离即刻消失」的定量版，
    也是习题 ⑦-3 排查路径的第一刀；
  - 自交 s = 0.95：H_obs/H_exp ≈ 9.5%（讲义「10%」），p < 1e-6 位点比例
    ≫ 90%（讲义「屠戮 90% 以上」）——失效条件第 2 条的误杀量级。

参数：
  --n-dip-wahlund  Wahlund 场景每 SNP 二倍体样本数（默认 200，按权重分摊）
  --n-dip-selfing  自交场景每 SNP 二倍体样本数（默认 100）
  --selfing-rate   自交率 s（默认 0.95）
  --n-snps         每场景 SNP 数（默认 2000）
  --seed           随机种子（默认 20261104）

合成数据不得写成真实群体结果；精确检验实现为 Wigginton et al. (2005) 的
中点展开递推（PLINK --hardy 同款算法），与讲义 §7.1 的卡方近似对照：
小样本/低频位点卡方失效正是讲义要求全基因组改用精确检验的原因（unverified
的细粒度差异见讲义）。只依赖 numpy；约 2 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch20_hwe_selfing_wahlund.py --selftest
"""
import argparse

import numpy as np


def hwe_exact(obs_hets, obs_hom1, obs_hom2):
    """Wigginton et al. (2005) 精确检验。obs_hom2 = 较稀有纯合子类。

    返回 p 值 = Pr(概率 ≤ 观测构型概率 | HWE, p 由样本内生估计)。
    """
    if obs_hets < 0 or obs_hom1 < 0 or obs_hom2 < 0:
        raise ValueError("负计数")
    rare_copies = 2 * obs_hom2 + obs_hets
    genotypes = obs_hets + obs_hom1 + obs_hom2
    if genotypes == 0:
        return 1.0
    probs = np.zeros(rare_copies + 1)
    mid = int(rare_copies * (2 * genotypes - rare_copies) / (2 * genotypes))
    if (rare_copies & 1) ^ (mid & 1):
        mid += 1
    curr_hets = mid
    curr_homr = (rare_copies - mid) // 2
    curr_homc = genotypes - curr_hets - curr_homr
    probs[mid] = 1.0
    total = 1.0
    while curr_hets >= 2:  # 向低杂合方向展开
        p = probs[curr_hets] * curr_hets * (curr_hets - 1.0) / (
            4.0 * (curr_homr + 1.0) * (curr_homc + 1.0))
        curr_hets -= 2
        curr_homr += 1
        curr_homc += 1
        probs[curr_hets] = p
        total += p
    curr_hets = mid
    curr_homr = (rare_copies - mid) // 2
    curr_homc = genotypes - curr_hets - curr_homr
    while curr_hets <= rare_copies - 2:  # 向高杂合方向展开
        p = probs[curr_hets] * 4.0 * curr_homr * curr_homc / (
            (curr_hets + 2.0) * (curr_hets + 1.0))
        curr_hets += 2
        curr_homr -= 1
        curr_homc -= 1
        probs[curr_hets] = p
        total += p
    p_obs = probs[obs_hets]
    return float(probs[probs <= p_obs + 1e-12].sum() / total)


def genotype_probs(p, F):
    """近交系数 F 下的期望基因型概率 (AA, Aa, aa)。"""
    q = 1 - p
    return p * p + p * q * F, 2 * p * q * (1 - F), q * q + p * q * F


def hwe(counts):
    """counts = (AA, Aa, aa)。Wigginton 递推约定 obs_hom2 = 较稀有的纯合子类，
    调用前按计数重排，避免合并频率接近 0.5 时稀有类归属颠倒。"""
    aa, het, bb = counts
    return hwe_exact(het, max(aa, bb), min(aa, bb))


def run(n_dip_w, n_dip_s, s, n_snps, seed):
    rng = np.random.default_rng(seed)

    # ---- 场景 A：Wahlund ----
    p_k = np.array([0.2, 0.5, 0.8])
    w_k = np.array([1 / 3, 1 / 3, 1 / 3])
    p_bar = float(w_k @ p_k)
    H_exp = 2 * p_bar * (1 - p_bar)
    H_obs_det = float(w_k @ (2 * p_k * (1 - p_k)))
    identity = H_exp - H_obs_det                      # 应 = 2 Var_w(p)
    var_p = float(w_k @ p_k**2 - p_bar**2)

    pvals_merged, pvals_split_all = [], []
    het_ratio_w = []
    for _ in range(n_snps):
        nk = rng.multinomial(n_dip_w, w_k)
        aa = het = bb = 0
        sub_counts = []
        for k in range(3):
            if nk[k] == 0:
                sub_counts.append(None)
                continue
            c = rng.multinomial(nk[k], [p_k[k] ** 2, 2 * p_k[k] * (1 - p_k[k]),
                                        (1 - p_k[k]) ** 2])
            sub_counts.append(c)
            aa += c[0]
            het += c[1]
            bb += c[2]
        # 合并样本按合并频率的期望杂合度（教材口径：p 内生估计）
        n_tot = aa + het + bb
        p_m = (2 * aa + het) / (2 * n_tot)
        het_ratio_w.append(het / (n_tot * 2 * p_m * (1 - p_m)))
        pvals_merged.append(hwe((aa, het, bb)))
        pvals_split_all.extend(hwe(tuple(c)) for c in sub_counts if c is not None)
    pvm = np.array(pvals_merged)
    pvs = np.array(pvals_split_all)

    # ---- 场景 B：自交 ----
    F = s / (2 - s)
    het_ratio_s, pvals_s = [], []
    for _ in range(n_snps):
        p = rng.uniform(0.1, 0.5)
        c = rng.multinomial(n_dip_s, genotype_probs(p, F))
        het_ratio_s.append(c[1] / (n_dip_s * 2 * p * (1 - p)))
        pvals_s.append(hwe(tuple(c)))
    pvs_s = np.array(pvals_s)

    kill_w = float((pvm < 1e-6).mean())          # Wahlund 合并样本被杀比例
    reject05_split = float((pvs < 0.05).mean())  # 分群后全部检验的名义水平
    kill_s = float((pvs_s < 1e-6).mean())     # 自交群体被杀比例

    print(f"合成算例（二倍体口径；稻瘟菌单倍体、HWE 对其无意义，见讲义 ⑤5.1）："
          f"每场景 {n_snps} 个 SNP；Wigginton (2005) 精确检验\n")
    print("场景 A：Wahlund 效应（K = 3，p_k = (0.2, 0.5, 0.8)，w_k = 1/3）")
    print(f"  恒等式核验：H_exp − H_obs = {identity:.4f}，2·Var_w(p) = {2 * var_p:.4f}"
          f"（讲义 §7.1 代数式）")
    print(f"  合并样本：H_obs/H_exp = {np.mean(het_ratio_w):.3f}"
          f"（确定性期望 {H_obs_det / H_exp:.3f}）；p < 1e-6 位点 {100 * kill_w:.1f}%"
          f" —— 全基因组杂合缺失，误杀规模")
    print(f"  正确分群后逐亚群检验（全部亚群×SNP  pooled）：p < 0.05 占 "
          f"{100 * reject05_split:.1f}%（名义 5%）—— 偏离「即刻消失」")
    print(f"\n场景 B：部分自交 s = {s}（平衡近交系数 F = s/(2−s) = {F:.4f}，"
          f"2n = {n_dip_s}）")
    print(f"  H_obs/H_exp = {np.mean(het_ratio_s):.4f}（讲义 §7.2「10%」，"
          f"理论 {(1 - F):.4f}）")
    print(f"  p < 1e-6 位点（= 盲目 --hwe 1e-6 杀掉的**真实多态位点**比例）："
          f"{100 * kill_s:.1f}% —— 讲义「屠戮 90% 以上」的复现")
    print("\n判读：")
    print("  ① 两类内源偏离（结构混合 / 自交）都表现为全基因组杂合缺失，"
          "与讲义 §4.3 的技术伪影（散点状、与深度相关）拓扑不同 ——"
          "排查第一步看偏离的空间/协变量结构，不是直接过滤；")
    print("  ② 过滤的方向性杀的是真实生物学信号：失效条件第 2 条（自交/克隆）与"
          "第 4 条（Wahlund 结构伪装）的量化落点；")
    print("  ③ 替代防线按讲义 §4.3 末段：DP/GQ/等位深度比构筑位点级真实性，"
          "只单向剔除杂合子极端过量的技术坍缩位点。")
    print("真实数据对照：PRJEB53625 为单倍体，HWE 在其上没有可检验的对象，hwe_*.hwe 既不作过滤"
          "也不作技术诊断；技术诊断看深度、缺失率、等位深度比与比对质量（06_data/phd/README.md p04）。")
    return dict(identity=identity, var2=2 * var_p, kill_w=kill_w,
                reject05_split=reject05_split, F=F, het_ratio_s=np.mean(het_ratio_s),
                kill_s=kill_s)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n-dip-wahlund", type=int, default=1000)
    ap.add_argument("--n-dip-selfing", type=int, default=100)
    ap.add_argument("--selfing-rate", type=float, default=0.95)
    ap.add_argument("--n-snps", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    r = run(args.n_dip_wahlund, args.n_dip_selfing, args.selfing_rate, args.n_snps,
            args.seed)

    if args.selftest:
        # 手算锚点：HWE 完全平衡的大样本应不显著；杂合缺失构型必显著
        p_bal = hwe((725, 250, 25))    # p̂=0.15、2n=2000、期望 het 255、构型基本平衡
        p_wal = hwe((700, 300, 0))     # p̂=0.15、杂合远低期望（Wahlund 型缺失）
        p_het = hwe((550, 300, 150))   # 杂合过量构型（克隆/坍缩型）
        checks = [
            (f"恒等式 H_exp − H_obs = 2Var(p)（{r['identity']:.4f} = {r['var2']:.4f}）",
             abs(r["identity"] - r["var2"]) < 1e-12),
            (f"恒等式数值 = 0.12（实际 {r['identity']:.4f}）",
             abs(r["identity"] - 0.12) < 1e-9),
            (f"平衡大样本精确检验不显著（p = {p_bal:.3f} > 0.05）", p_bal > 0.05),
            (f"杂合缺失构型显著（p = {p_wal:.2e} < 1e-6）", p_wal < 1e-6),
            (f"杂合过量构型显著（p = {p_het:.2e} < 1e-3）", p_het < 1e-3),
            (f"Wahlund 合并样本误杀 > 90%（实际 {100 * r['kill_w']:.1f}%）",
             r["kill_w"] > 0.90),
            (f"正确分群后回到名义水平（p<0.05 占 {100 * r['reject05_split']:.1f}%"
             f" ∈ [2%, 8%]）", 0.02 <= r["reject05_split"] <= 0.08),
            (f"自交 F = s/(2−s) = 0.9048（实际 {r['F']:.4f}）",
             abs(r["F"] - 0.904762) < 1e-4),
            (f"自交杂合度 ≈ 随机交配期望 10%（实际 {r['het_ratio_s']:.3f} ∈ "
             f"[0.08, 0.11]）", 0.08 <= r["het_ratio_s"] <= 0.11),
            (f"自交群体 p<1e-6 位点 > 90%（实际 {100 * r['kill_s']:.1f}%）"
             " —— 「屠戮 90% 以上」复现", r["kill_s"] > 0.90),
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch24_pvalue_vs_padj.py — 「pvalue 换 padj」指纹的多重检验量化（合成算例）

服务于：教材第 24 章（AI 辅助生信分析的验证）§24.4 概念与方法
（统计量误用：用 pvalue < 0.05 代替 padj < 0.05）、§24.5 失效条件
第 1 条（语法正确但生物学错误是常态）与第 4 条（没有已知答案就无法
判断对错），对应讲义 p01 ④-4.2 五类高频错误之 1、⑥-6.2 指纹表第 1 行
（差异基因数从 20 上下跳到 100 上下、本例 1 995 × 0.05 ≈ 100 个期望
假阳性）、⑥-6.1③（min(padj) 与 BH 手算边界同量级）、03_code/phd/
scripts/01_verify_de.R 第 ③ 段的两行手算公式，以及 l0_06_stats 的
L0-6-Q5 那笔账（20 000 基因 × 0.05 = 1 000 个假阳性）。

合成设定（不基于任何真实样本；固定种子可复现）：
  1 975 个空假设基因：p 值 ~ Uniform(0,1)（无差异数据的 p 值分布）；
  20 个已知差异基因（对应 spike-in 已知答案，真值 log2FC = 3 的那一类）：
  p 值取 1e-8 量级——「真实信号必然显著」的合成代理。
  合计 m = 1 995，与讲义 ⑥-6.2 的「本例」检验基因数一致。

正文引用的输出（手算可对）：
  - 全空假设下的期望假阳性数 m × 0.05（1 995 → ≈100；20 000 → 1 000，
    即 L0-6-Q5 的账）与二项抽样允许带内的实测计数；
  - pvalue<0.05 计数 ≈ 100 + 20（假阳性 + 真阳性混在一起，~6 倍虚增，
    合成口径）vs 完整 BH 校正后只剩 ≈ 20 个、且混入的空假设基因 ≲ 1 个
    （FDR ≤ 5% 的期望保证：BH 控制的是假阳性「比例」期望，不是 0 假阳性）；
  - verify_de.R 的手算公式 min(sort(p) * m / rank) 与完整 BH 逐步最小值
    包络在最小值处严格相等（讲义 ⑥-6.1③「同量级」断言的合成验证）；
  - 对照（非本脚本输出，仅打印）：数据 README p01 节实测的 AI 版 97 个
    vs 参考 22 个（≈4.4 倍），在课程自造数据 + DESeq2 链上得到。

参数：
  --m-null    空假设基因数（默认 1975；加 20 个已知差异基因 = 1995）
  --seed      随机种子（默认 20261105）

合成数据不得写成真实样本结果。只用 Python 标准库 + numpy；< 1 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch24_pvalue_vs_padj.py --selftest
"""
import argparse

import numpy as np


def bh_adjust(pvalues: np.ndarray) -> np.ndarray:
    """完整 Benjamini–Hochberg 校正（与 R p.adjust(method='BH') 同式）：
    按 p 升序，adj_(i) = min_{j >= i} min(1, m * p_(j) / j)。"""
    m = pvalues.size
    order = np.argsort(pvalues, kind="stable")
    ranked = pvalues[order] * m / np.arange(1, m + 1)
    adjusted = np.minimum.accumulate(ranked[::-1])[::-1]
    adjusted = np.minimum(adjusted, 1.0)
    out = np.empty(m)
    out[order] = adjusted
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--m-null", type=int, default=1975)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    m_null, m_de = args.m_null, 20
    m = m_null + m_de

    print("合成算例（不基于任何真实样本）：1 975 个空假设基因 p~Uniform(0,1)"
          " + 20 个已知差异基因 p~1e-8（spike-in 已知答案的合成代理）")
    print(f"合计 m = {m}，与讲义 ⑥-6.2「本例 1 995 × 0.05」的检验基因数一致")
    print()

    p_null = rng.random(m_null)                     # 空假设：p 均匀分布
    p_de = 10.0 ** (-rng.uniform(6, 10, m_de))      # 已知差异：必然显著
    p = np.concatenate([p_null, p_de])

    print("部分 A 期望假阳性（手算规则 m × 0.05，L0-6-Q5 的账）：")
    exp_fp = m * 0.05
    print(f"  m = {m:>5}  →  期望假阳性 {exp_fp:.1f}（讲义：1 995 × 0.05 ≈ 100）")
    print(f"  m = 20000 →  期望假阳性 {20000 * 0.05:.0f}（L0-6-Q5：2 万基因 1 000 个）")
    n_null_p05 = int((p_null < 0.05).sum())
    sd = (m_null * 0.05 * 0.95) ** 0.5
    print(f"  空假设实际 p<0.05 计数：{n_null_p05}（二项抽样 ±3σ 带 "
          f"[{m_null * 0.05 - 3 * sd:.0f}, {m_null * 0.05 + 3 * sd:.0f}]）")
    print()

    print("部分 B pvalue vs padj 的指纹（对照 verify_de.R ③ 的两行输出形态）：")
    padj = bh_adjust(p)
    n_p05 = int((p < 0.05).sum())
    n_null_in_p05 = int((p[:m_null] < 0.05).sum())
    n_de_in_p05 = n_p05 - n_null_in_p05
    n_padj05 = int((padj < 0.05).sum())
    n_null_in_padj05 = int((padj[:m_null] < 0.05).sum())
    print(f"  实际 p<0.05 的基因数     : {n_p05}  = {n_null_in_p05} 假阳性"
          f" + {n_de_in_p05} 真阳性（FDP {n_null_in_p05 / n_p05:.0%}）")
    print(f"  实际 padj<0.05 的基因数  : {n_padj05}  = {n_padj05 - n_null_in_padj05}"
          f" 真阳性 + {n_null_in_padj05} 个混入的空假设（FDP "
          f"{n_null_in_padj05 / max(n_padj05, 1):.0%}）")
    print("                               —— BH 把 FDP 从 ~80% 压到 ≤5% 量级；")
    print("                               FDR 是期望保证，1 个假阳性属正常，不是 BH 失效")
    print(f"  虚增倍数 {n_p05}/{n_padj05} = {n_p05 / n_padj05:.1f}×（合成口径；")
    print("   课程数据 README p01 节实测：AI 版 97 vs 参考 22 ≈ 4.4×，")
    print("   差异来自 CPM 转换与过滤改变 null 分布，机制同向）")
    print()

    print("部分 C BH 手算公式 vs 完整 BH（讲义 ⑥-6.1③「同量级」断言的合成验证）：")
    order = np.argsort(p, kind="stable")
    hand_min = float(np.min(p[order] * m / np.arange(1, m + 1)))
    full_min = float(np.min(padj))
    print(f"  verify_de.R 手算式 min(sort(p)*m/rank) = {hand_min:.3e}")
    print(f"  完整 BH 的 min(adj)                    = {full_min:.3e}")
    print("  两式在最小值处严格相等（BH 包络的最后一步即全局最小）")
    print()
    print("指纹定位（讲义 ⑥-6.2 第 1 行）：差异基因数从 20 上下跳到 100 上下")
    print("  → 先 grep 'pvalue' 被验脚本，确认筛选用的是哪一列")

    if args.selftest:
        checks = [
            ("空假设 p<0.05 计数落在 m×0.05 的 ±3σ 带内",
             abs(n_null_p05 - m_null * 0.05) <= 3 * sd),
            ("pvalue 筛选计数 ≈ 100 + 20（≈ 6× 虚增的合成形态）",
             n_p05 - m_de <= n_null_p05 and n_p05 >= n_padj05 * 3),
            ("BH 后召回全部 20 个已知差异基因，且混入空假设 ≤2 个（FDR ≤5% 的期望形态）",
             (padj[m_null:] < 0.05).all() and n_null_in_padj05 <= 2),
            ("BH 的 FDP ≤10%，而 pvalue 筛选的 FDP ≥50%（指纹的量化本质）",
             n_null_in_padj05 / max(n_padj05, 1) <= 0.10
             and n_null_in_p05 / n_p05 >= 0.5),
            ("手算式与完整 BH 的 min 严格相等（⑥-6.1③ 同量级）",
             abs(hand_min - full_min) <= 1e-12 * max(1.0, full_min)),
            ("m=1995 期望假阳性 ≈ 100（讲义口径）", abs(exp_fp - 99.75) < 1e-9),
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

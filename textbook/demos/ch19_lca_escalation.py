#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch19_lca_escalation.py — LCA 分类上浮：参考库逐步删去近缘种时，同一批合成 read 的
分类阶元分布怎样从「种（正确）」滑向「属（上浮）」「种（错误）」「未分类」（合成算例）

服务于：教材第 19 章（宏基因组：物种组成、组装分箱与功能）§19.5 失效条件第 2 条
「LCA 在近缘参考缺失时把分类上浮到高阶，看起来『分类正确』但信息丢失」，
对应讲义 m07 §4.2（LCA 拓扑上浮）与 ⑥-6.2（分类报告解读）。

合成设定（不基于任何真实样本；固定种子可复现）：
  - 样本只含一个真实物种 T（属 G）。T 的 read 分两类：
    ① 特有 read（占比 --unique-frac，默认 0.35）：k-mer 全部只命中 T 的物种特异区；
    ② 保守 read（其余 65%）：k-mer 全部落在属内共有的看家区域 —— 库里每多一个
       同属成员，这批 read 就多一个候选命中，LCA 就被顶到属节点。
  - 参考库按阶梯删除：D0 = {T,S1..S4}（属齐全）→ D1 = {S1..S4}（目标种缺失，
    「近缘参考缺失」的第一阶）→ 逐个删到只剩 1 个姐妹种 → 全删。
  - 判定规则（Kraken2 LCA 的简化）：一条 read 的命中集合 = 库中拥有其 k-mer 的
    物种集合；|命中|=0 → 未分类；|命中|=1 → 该物种（唯一命中即直下）；|命中|≥2
    → 共同祖先 = 属 G（上浮）。省略置信度门槛（--confidence）与 k-mer 计数细节，
    只保留阶元归属逻辑。

正文引用的输出（手算可对）：
  - D0：种（正确）≈ 特有 read 占比 f_u，其余 1−f_u 停在属 —— 即使库最全，
    保守区 read 也到不了种水平（讲义 ④-4.2「海量 reads 停滞在属层」）；
  - D1（目标种缺失、≥2 姐妹种仍在）：种（正确）归零，保守 read 全部上浮到属 ——
    「看起来分类正确（属确实对）但种级信息丢失」；
  - D4（只剩 1 个姐妹种 S4）：保守 read 被唯一命中直下给 S4 —— 种水平报告
    「分辨率恢复了」，但 100% 张冠李戴（比上浮更糟的假精确）；
  - D5（全删）：100% 未分类 —— 库里没有就看不见（讲义 ④-4.7）。

参数：
  --n-reads     每个库状态抽样的合成 read 数（默认 200000）
  --unique-frac T 的特有 read 占比 f_u（默认 0.35）
  --n-sisters   姐妹种个数（默认 4，即属内共 5 个种）
  --seed        随机种子（默认 20261104）

合成数据不得写成真实样本结果；真实 Kraken2 行为受 k-mer 长度、置信度门槛与
库构建细节影响，本演示只复现「阶元归属逻辑」这一层（unverified 的细粒度差异见讲义）。
只依赖 numpy；约 1 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch19_lca_escalation.py --selftest
"""
import argparse

import numpy as np

GENUS = "Genus_G"  # 合成属名（非真实分类单元）


def classify(read_kind, db):
    """read_kind: 'unique' 或 'conserved'；db: 库内物种名列表。返回 (rank, 是否正确)。"""
    if read_kind == "unique":
        if "T" in db:
            return ("种(正确)", True)
        return ("未分类", False)
    # conserved：命中集合 = 库内全部属 G 成员（保守 k-mer 属内共有）
    hits = [s for s in db if s != ""]  # 库内每个成员都共有
    n = len(hits)
    if n == 0:
        return ("未分类", False)
    if n == 1:
        return ("种(错误)", False)  # 唯一命中直下 → 张冠李戴
    return ("属(上浮)", True)  # ≥2 个命中 → LCA 顶到属；属对但种级信息丢失


def run(n_reads, unique_frac, n_sisters, seed):
    sisters = [f"S{i}" for i in range(1, n_sisters + 1)]
    ladder = [("D0 属齐全", ["T"] + sisters)]
    ladder.append((f"D1 删目标种T", list(sisters)))
    for k in range(1, n_sisters - 1):
        ladder.append((f"D{k+1} 剩{len(sisters[k:])}姐妹", list(sisters[k:])))
    ladder.append((f"D{n_sisters} 剩1姐妹", list(sisters[-1:])))
    ladder.append((f"D{n_sisters+1} 全删", []))

    print(f"合成算例：样本只含真实物种 T（属 {GENUS}，虚构）；特有 read 占比 "
          f"f_u = {unique_frac}，其余 read 的 k-mer 属内共有")
    print(f"参考库删除阶梯：{' → '.join(name for name, _ in ladder)}")
    print(f"LCA 简化规则：唯一命中→直下该种；≥2 命中→上浮到属；0 命中→未分类；"
          f"每状态 {n_reads} 条合成 read，seed = {seed}\n")
    header = (f"{'库状态':<14} | {'库内成员':<18} | {'种(正确)%':>9} | {'种(错误)%':>9} | "
              f"{'属(上浮)%':>9} | {'未分类%':>8}")
    print(header)
    print("-" * len(header))

    results = {}
    for step, (name, db) in enumerate(ladder):
        rng = np.random.default_rng(seed + 97 * step)
        kinds = rng.choice(["unique", "conserved"], size=n_reads,
                           p=[unique_frac, 1 - unique_frac])
        counts = {"种(正确)": 0, "种(错误)": 0, "属(上浮)": 0, "未分类": 0}
        for k in kinds:
            rank, _ = classify(k, db)
            counts[rank] += 1
        member = "+".join(db) if db else "（空库）"
        frac = {r: counts[r] / n_reads for r in counts}
        results[name] = dict(db=list(db), **frac)
        print(f"{name:<14} | {member:<18} | {100*frac['种(正确)']:>8.1f}% | "
              f"{100*frac['种(错误)']:>8.1f}% | {100*frac['属(上浮)']:>8.1f}% | "
              f"{100*frac['未分类']:>7.1f}%")

    d0 = results["D0 属齐全"]
    d1 = results["D1 删目标种T"]
    d_last = results[f"D{n_sisters} 剩1姐妹"]
    d_empty = results[f"D{n_sisters+1} 全删"]
    print("\n判读：")
    print(f"  D0→D1（目标种从库里消失、≥2 姐妹仍在）：种(正确) "
          f"{100*d0['种(正确)']:.1f}% → {100*d1['种(正确)']:.1f}%，保守 read 全部"
          f"上浮到属（{100*d1['属(上浮)']:.1f}%）——「属是对的，但种级信息整批丢失」，"
          "报告里物种数骤降而属层丰度几乎不动，正是失效条件第 2 条的形态；")
    print(f"  只剩 1 个姐妹种时：{100*d_last['种(错误)']:.1f}% 的 read 被唯一命中"
          "「直下」给姐妹种 —— 种水平分辨率在纸面上恢复，实则张冠李戴"
          "（比上浮更危险的假精确）；")
    print(f"  全删：未分类 {100*d_empty['未分类']:.1f}% —— 库里没有就看不见"
          "（讲义 ④-4.7 的哈希表盲区）。")
    print("真实数据对照（PRJDB12800，Kraken2 Standard-8 分类率预期 30–60%，"
          "即未分类 40–70% 为常态：06_data/master/README.md m07 自查判据，unverified）。")
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n-reads", type=int, default=200000)
    ap.add_argument("--unique-frac", type=float, default=0.35)
    ap.add_argument("--n-sisters", type=int, default=4)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    r = run(args.n_reads, args.unique_frac, args.n_sisters, args.seed)

    if args.selftest:
        d0 = r["D0 属齐全"]
        d1 = r["D1 删目标种T"]
        names = list(r)
        d_last = r[names[-2]]
        d_empty = r[names[-1]]
        mid = r[names[2]]  # 剩 2 个姐妹种的状态
        checks = [
            (f"D0 种(正确) ≈ f_u = {args.unique_frac}（实际 {100*d0['种(正确)']:.1f}%）",
             abs(d0["种(正确)"] - args.unique_frac) < 0.02),
            (f"D0 属(上浮) ≈ 1−f_u（实际 {100*d0['属(上浮)']:.1f}%）",
             abs(d0["属(上浮)"] - (1 - args.unique_frac)) < 0.02),
            (f"D1 目标种删除后种(正确) = 0（实际 {100*d1['种(正确)']:.1f}%）",
             d1["种(正确)"] < 0.005),
            (f"D1 保守 read 全部上浮到属（实际 {100*d1['属(上浮)']:.1f}% > 55%）",
             d1["属(上浮)"] > 0.55),
            (f"D1 无张冠李戴（种(错误) < 1%，实际 {100*d1['种(错误)']:.1f}%）",
             d1["种(错误)"] < 0.01),
            (f"剩 2 姐妹时仍上浮到属（实际 {100*mid['属(上浮)']:.1f}% > 55%）",
             mid["属(上浮)"] > 0.55),
            (f"剩 1 姐妹时种(错误) ≈ 1−f_u（实际 {100*d_last['种(错误)']:.1f}% > 55%）"
             " —— 假精确",
             d_last["种(错误)"] > 0.55),
            (f"剩 1 姐妹时种(正确) = 0（实际 {100*d_last['种(正确)']:.1f}%）",
             d_last["种(正确)"] < 0.005),
            (f"全删后 100% 未分类（实际 {100*d_empty['未分类']:.1f}%）",
             d_empty["未分类"] > 0.99),
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

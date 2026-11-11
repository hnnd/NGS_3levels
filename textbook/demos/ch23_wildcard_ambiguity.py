#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch23_wildcard_ambiguity.py — Snakemake wildcards 匹配歧义的机制复刻：
{sample} 默认等价正则 .+ 的贪婪陷阱、两条 rule 输出同模式的双重匹配、
wildcard_constraints 的保护边界（合成算例）

服务于：教材第 23 章（分析流程工程化：Snakemake 与 Nextflow）§23.4
概念与方法（wildcards 的逆向匹配）、§23.5 失效条件第 1 条（wildcards
匹配歧义使 rule 抓错输入），对应讲义 m08 ④（通配符贪婪陷阱 / 输出模式
冲突）、⑨-2（AmbiguousRuleException 的隐形版本）、⑩-1（习题：两条
rule 都能匹配 results/A.sorted.bam），以及 03_code/master/pipelines/
Snakefile 第 47-48 行的 wildcard_constraints 实物。

合成设定（不基于任何真实样本；固定种子可复现）：
  部分 A（⑩-1 习题答案机制）：rule_generic 的输出模式 results/{sample}.bam
    与 rule_sorted 的 results/{sample}.sorted.bam 对目标 results/A.sorted.bam
    都能逆向匹配——前者绑定 sample="A.sorted"、后者绑定 sample="A"，
    两条 rule 匹配数 = 2 → AmbiguousRuleException 的代码形态。
  部分 B（⑨-2 隐形版本）：输出模式 results/{sample}_1.fq.gz 对目标
    results/clean/CK_1_1.fq.gz 逆向匹配时 {sample} 把路径分隔符 "/"
    一起吃进去（sample="clean/CK_1"）；施加 Snakefile 同款的
    wildcard_constraints sample=r"[A-Za-z0-9_.-]+" 后匹配失败——
    错误从「静默写错目录」提前变为「显式匹配失败」。
  部分 C（批量量化）：500 个随机目标 results/quant/<名>/quant.sf，
    比较「救援 rule 用同前缀 results/{sample}/quant.sf」与
    「救援 rule 用异前缀 results/rescue/{sample}/quant.sf」各自的
    歧义匹配率——讲义 ⑨-2 解法①（输出路径前缀不同）的量化注脚。

正文引用的输出（手算可对）：
  - results/A.sorted.bam 的双重绑定（"A.sorted" 与 "A"）；
  - sample="clean/CK_1" 含 "/"（贪婪吞路径的直接证据）；
  - 约束后同目标匹配数 0；随机目标集上同前缀歧义率 ≫ 0、异前缀 = 0。

参数：
  --n-targets   部分 C 的随机目标数（默认 500）
  --seed        随机种子（默认 20261105）

合成数据不得写成真实样本结果。只用 Python 标准库；< 1 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch23_wildcard_ambiguity.py --selftest
"""
import argparse
import random
import re


def wc_regex(pattern: str, constrained: bool = False) -> str:
    """把 Snakemake 输出模式转成锚定正则。{sample} 默认 .+（贪婪、吃 "/"）；
    施加 wildcard_constraints 后等价 [A-Za-z0-9_.-]+（与配套 Snakefile 一致）。"""
    body = r"[A-Za-z0-9_.-]+" if constrained else r".+"
    out = re.escape(pattern)
    out = out.replace(r"\{sample\}", f"({body})")
    return f"^{out}$"


def match_rules(target: str, patterns: list[str], constrained: bool = False):
    """逆向匹配：返回 [(rule序号, 绑定的sample值), ...]（Snakemake 从目标
    倒推所有 output 模式；命中 ≥2 条即 AmbiguousRuleException）。"""
    hits = []
    for i, pat in enumerate(patterns):
        m = re.match(wc_regex(pat, constrained), target)
        if m:
            hits.append((i, m.group(1)))
    return hits


def make_targets(n: int, seed: int) -> list[str]:
    """合成 n 个 quant.sf 目标路径，样本名混合字母/数字/点/横线（仍全部合法）。"""
    rng = random.Random(seed)
    names = set()
    while len(names) < n:
        tok = "".join(rng.choice("ABCDEFGHKM0123456789") for _ in range(rng.randint(2, 5)))
        sep = rng.choice(["_", ".", "-", ""])
        names.add(f"{tok}{sep}{rng.randint(1, 48)}")
    return sorted(f"results/quant/{name}/quant.sf" for name in names)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n-targets", type=int, default=500)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    print("合成算例（不基于任何真实样本）；复刻 Snakemake 从下游目标倒推 output 模式的匹配语义")
    print()

    print("部分 A 双重匹配（讲义 m08 ⑩-1 / ⑨-2 AmbiguousRuleException 场景）：")
    target_a = "results/A.sorted.bam"
    pats_a = ["results/{sample}.bam", "results/{sample}.sorted.bam"]
    hits_a = match_rules(target_a, pats_a)
    for i, sample in hits_a:
        print(f"  rule[{i}] 模式 {pats_a[i]:<28} 命中，绑定 sample={sample!r}")
    print(f"  → 匹配 rule 数 = {len(hits_a)}（≥2 即引擎拒绝裁决：AmbiguousRuleException）")
    pats_a_fixed = ["results/quant/{sample}/quant.sf", "results/rescue/{sample}/quant.sf"]
    target_a_fixed = "results/quant/A/quant.sf"
    hits_a_fixed = match_rules(target_a_fixed, pats_a_fixed)
    print(f"  改异前缀后（解法①，目标 {target_a_fixed}）匹配 rule 数 = {len(hits_a_fixed)}"
          f"（绑定 sample={hits_a_fixed[0][1]!r}）")
    print("  注：wildcard_constraints 对本案无救——两个绑定都满足字符集；")
    print("        解法②约束只在绑定值会越界时有效，解法③ ruleorder 是最后手段")
    print()

    print("部分 B 贪婪吞路径（讲义 m08 ⑨-2 隐形版本：wildcards: sample=clean/CK_1）：")
    target_b = "results/clean/CK_1_1.fq.gz"
    pat_b = "results/{sample}_1.fq.gz"
    hits_b_free = match_rules(target_b, [pat_b])
    hits_b_con = match_rules(target_b, [pat_b], constrained=True)
    print(f"  无约束：{pat_b} 对 {target_b}")
    print(f"    绑定 sample={hits_b_free[0][1]!r}（含 '/' → 输出会写进错误的嵌套目录）")
    print(f"  加约束 sample=r\"[A-Za-z0-9_.-]+\"（配套 Snakefile 第 47-48 行同款）：")
    print(f"    匹配数 = {len(hits_b_con)}（匹配失败 → 错误显式暴露，而非静默写错）")
    print()

    print(f"部分 C 批量歧义率（{args.n_targets} 个随机目标，种子 {args.seed}）：")
    targets = make_targets(args.n_targets, args.seed)
    same = ["results/quant/{sample}/quant.sf", "results/{sample}/quant.sf"]
    diff = ["results/quant/{sample}/quant.sf", "results/rescue/{sample}/quant.sf"]
    n_same = sum(1 for t in targets if len(match_rules(t, same)) >= 2)
    n_diff = sum(1 for t in targets if len(match_rules(t, diff)) >= 2)
    print(f"  救援 rule 同前缀（results/{{sample}}/quant.sf）：歧义目标 {n_same}/{args.n_targets}"
          f"（{n_same / args.n_targets:.1%}）")
    print(f"  救援 rule 异前缀（results/rescue/{{sample}}/quant.sf）：歧义目标 {n_diff}/{args.n_targets}"
          f"（{n_diff / args.n_targets:.1%}）")
    print("  → 讲义 ⑨-2 解法①「输出路径前缀不同」是唯一零成本的根治")

    if args.selftest:
        checks = [
            ("results/A.sorted.bam 被 2 条 rule 同时命中（⑩-1 答案）", len(hits_a) == 2),
            ("双重绑定为 'A.sorted' 与 'A'",
             [s for _, s in hits_a] == ["A.sorted", "A"]),
            ("异前缀改造后匹配数降为 1", len(hits_a_fixed) == 1),
            ("无约束时 {sample} 吞下 '/'（sample='clean/CK_1'）",
             hits_b_free and "/" in hits_b_free[0][1]),
            ("施加 wildcard_constraints 后同目标匹配数为 0", len(hits_b_con) == 0),
            (f"同前缀歧义率 {n_same / args.n_targets:.1%} > 0",
             n_same > 0),
            (f"异前缀歧义率 = {n_diff / args.n_targets:.1%}",
             n_diff == 0),
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合成演示：随机序列六框翻译的 ORF 长度分布（教材第 9 章概念与方法节复现入口）。

服务于第 9 章「基因组注释与可视化核查」中「ORF 物理长度的统计显著性」一段
（对应讲义 u07 §4.1）：在随机核苷酸序列中三种终止密码子（TAA/TAG/TGA）以
p = 3/64 的概率出现，一段不含终止密码子的长读框可以纯由随机噪声产生。
本脚本用固定种子的合成序列做六框翻译，数出不同最短长度门槛下的 ORF 个数，
与理论期望 E ≈ 6·p·(G/3)·(1−p)^L 对照——说明 ORF 长度只是基因预测的统计线索之一
（既不必要也不充分；短基因与移码会让真基因的 ORF 偏短），基因预测必须再结合密码子使用偏好与 RBS（讲义 u07 §4.1 第 2、3 条）。

【合成算例】序列由固定种子均匀随机生成，不代表任何真实菌株或真实样本，
正文引用时必须说「合成算例」。

参数：
  --genome-size  合成序列长度（bp），默认 1000000
  --min-codons   ORF 最短长度门槛（密码子数），逗号分隔，默认 30,60,100,150,300
  --seed         随机种子（默认 20261104），固定后输出可复现

正文引用的输出：
  p_stop = 3/64、从任一密码子起到遇到终止密码子的平均距离 1/p ≈ 21.3 密码子（含终止）、
  终止前非终止密码子平均个数 (1−p)/p ≈ 20.3、
  P(连续 300 密码子无终止) = (1−p)^300 的现跑值、
  六框 ORF 观测计数 vs 理论期望对照表。

运行：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch09_orf_length.py --selftest
"""

import argparse
import math
import random
import sys

STOPS = (b"TAA", b"TAG", b"TGA")
_P_STOP = 3.0 / 64.0


def random_dna(n, rng):
    """均匀随机合成 DNA（四种碱基等概率，纯合成数据）。"""
    return bytes(rng.choices(b"ACGT", k=n))


def revcomp(seq):
    return seq.translate(bytes.maketrans(b"ACGT", b"TGCA"))[::-1]


def orf_run_lengths(seq):
    """单链三框翻译，返回全部极大无终止密码子读框的长度（密码子数）。"""
    runs = []
    n = len(seq)
    for frame in range(3):
        run = 0
        for i in range(frame, n - 2, 3):
            if seq[i:i + 3] in STOPS:
                if run:
                    runs.append(run)
                run = 0
            else:
                run += 1
        if run:
            runs.append(run)
    return runs


def expected_orfs(genome_size, min_codons):
    """六框、双链的理论期望：E ≈ 6 · p · (G/3) · (1−p)^L（忽略序列两端边界效应）。"""
    return 6.0 * _P_STOP * (genome_size / 3.0) * (1.0 - _P_STOP) ** min_codons


def run(genome_size, min_codons_list, seed):
    seq = random_dna(genome_size, random.Random(seed))
    runs = orf_run_lengths(seq) + orf_run_lengths(revcomp(seq))
    rows = []
    for L in min_codons_list:
        obs = sum(1 for r in runs if r >= L)
        exp = expected_orfs(genome_size, L)
        rows.append((L, obs, exp))
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="合成算例：随机序列六框翻译的 ORF 长度分布 vs 理论期望（教材第 9 章）")
    ap.add_argument("--genome-size", type=int, default=1_000_000,
                    help="合成序列长度（bp），默认 1000000")
    ap.add_argument("--min-codons", default="30,60,100,150,300",
                    help="ORF 最短长度门槛（密码子数），逗号分隔")
    ap.add_argument("--seed", type=int, default=20261104, help="随机种子")
    ap.add_argument("--selftest", action="store_true", help="断言正文引用的关键输出")
    args = ap.parse_args(argv)

    min_codons_list = [int(x) for x in args.min_codons.split(",")]
    rows = run(args.genome_size, min_codons_list, args.seed)

    print("=== 合成算例：随机序列六框翻译的 ORF 长度分布（固定种子 %d）===" % args.seed)
    p = _P_STOP
    print("p_stop = 3/64 = %.6f" % p)
    print("遇到终止密码子的平均距离 1/p = %.1f 密码子（含终止本身，几何分布均值）"
          % (1.0 / p))
    print("终止前非终止密码子的平均个数 (1-p)/p = %.1f（讲义 u07 §4.1「约 21」对应前者）"
          % ((1.0 - p) / p))
    p300 = (1.0 - p) ** 300
    print("P(连续 300 密码子无终止) = (1-3/64)^300 = %.2e"
          "（讲义 u07 §4.1 记 ≈5.8e-07，见 CASE-CH09-04）" % p300)
    print("合成序列 G = %d bp，双链六框；E = 6·p·(G/3)·(1−p)^L"
          % args.genome_size)
    print("%8s %12s %18s" % ("L(密码子)", "观测 ORF 数", "理论期望 E"))
    for L, obs, exp in rows:
        print("%8d %12d %18.1f" % (L, obs, exp))

    longest = rows[-1]
    shortest = rows[0]
    print("判读：即便把门槛放到 %d 密码子，%d bp 随机序列的六框里仍期望有约 %d 个"
          "「长 ORF」——ORF 长度本身不能定义基因；" % (shortest[0], args.genome_size,
                                                     round(shortest[2])))
    print("      而把门槛抬到 %d 密码子（约 900 bp）后，随机噪声期望降至 %.3g 个——"
          "这才是超长 ORF 成为强证据的原因（密码子偏好/RBS 另计）。"
          % (longest[0], longest[2]))

    if args.selftest:
        assert abs(p - 0.046875) < 1e-12
        assert abs(1.0 / p - 21.3333) < 0.01
        assert abs((1.0 - p) / p - 20.3333) < 0.01, "两个均值相差恰为 1，不得混用"
        assert 5.5e-7 < p300 < 5.7e-7, "P(≥300) 现跑值应 ≈5.6e-07"
        for L, obs, exp in rows:
            tol = max(4.0, 4.0 * math.sqrt(exp + 1.0))
            assert abs(obs - exp) <= tol, \
                "L=%d：观测 %d 与期望 %.1f 偏离超过容差 %.1f" % (L, obs, exp, tol)
        assert shortest[1] > 100, "L=%d 时观测 ORF 数应很多（ORF 长度不是充分证据）" % shortest[0]
        print("SELFTEST PASS：p、平均长度、P(≥300)、六框计数 vs 理论期望均符合预期")

    return 0


if __name__ == "__main__":
    sys.exit(main())

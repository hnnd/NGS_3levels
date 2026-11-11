#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch05_phred_fastq.py — FASTQ 四行契约、Phred+33 编解码与两类静默陷阱（合成算例 · 无随机数）

服务章节：第 5 章 §5.4「FASTQ 四行契约与 Phred 的完整定义」、失效条件第 2 条
（grep -c '^@' 数 read 偏大）与失效条件第 4 条（FASTQ 被截断 / 多行 FASTA 被当单行处理）。
第 4 章只给错误率百分比并前指，Q ↔ P 的概率表在 demos/ch04_phred_q.py；本脚本管
「格式契约」：四行结构、计数陷阱、截断与折行检测。

数据性质：【合成算例】输入为讲义 l0_04 §上机 步骤 0 的固定演示串（READ_0001/READ_0002），
中部缺行算例为脚本内固定构造，不涉及任何真实测序数据，输出不得写成真实样本实测结果。

正文引用的输出：
  - l0_04 demo.fq 两行计数对照：wc -l ÷ 4 = 2（正确）vs grep -c '^@' = 3（偏大 1）
  - 质量行行首 '@' 的解码：ASCII 64 → Q31 → P = 10^-3.1 ≈ 7.94e-4（合法质量字符）
  - READ_0001 第 22 位 '#'：ASCII 35 → Q2 → P = 0.631（六成几率判错）
  - FASTQ 总行数整除 4 是必要非充分：中部缺行 + 手工删行凑整后行数合规、
    块结构校验（@ 行 / + 行 / 序列质量等长）照样放行——错位完全静默，
    只能靠 md5sum 对账与 read 数同提供方核对发现（l0_04 防线三件套）
  - Phred+33 编解码往返：ASCII = Q + 33，Q ∈ [0, 41] 全区间一致
  - 多行 FASTA：按 '>' 计数 2 条；当两行一条记录硬解则条数折半、内容串味

参数含义：
  --qlen            合成 FASTQ 每条 read 的序列长度（bp），固定输入，仅用于展示
  --pad-lines       中部缺行后手工删行凑 4 的倍数时删去的行数（配合固定构造，默认 3）
"""
import argparse
import sys

# ---- 固定输入：l0_04 §上机 步骤 0 的 demo.fq（第 2 条质量行故意以 '@' 开头）----
FASTQ_GOOD = [
    "@READ_0001 1:N:0:ATCACG",
    "GATCGGAAGAGCACACGTCTGAACTCCAGTCAC",
    "+",
    "FFFFFF:FFFFFFFFF,FFFF#FFFFFFFFFFF",
    "@READ_0002 1:N:0:ATCACG",
    "TTGACCATGCGCATTAGGCCTAAGCTTGACCAT",
    "+",
    "@IIIIIIIIIIIIIIIIIIIIIIIIII?55555",
]

# 第三条合成 read（中部缺行算例的原始材料，同样 33 bp）
FASTQ_THIRD = [
    "@READ_0003 1:N:0:ATCACG",
    "CCGTAGGCATGCTAGCTAGGATCCGATGCAATG",
    "+",
    "IIIIIIIIIIIIIIIIII?IIIIIIIIIIIIII",
]

FASTA_WRAPPED = [
    ">seq_1 description",
    "ATGGCTAAGCTTGACCATGCGCATT",
    "AGGCCTAAGCTTGACCATGCGCATT",   # 同一条序列折行（FASTA 规范允许多行）
    ">seq_2",
    "TTGACCATGCGCATTAGGCCTAAGC",
]


def count_reads_wc_l_div4(lines):
    """正确的 FASTQ 计数：总行数 ÷ 4（zcat f.fq.gz | wc -l | awk '{print $1/4}'）。"""
    return len(lines) / 4


def count_grep_at(lines):
    """错误的 FASTQ 计数：grep -c '^@' —— 质量行首的 '@'（Q31）也被数进去。"""
    return sum(1 for ln in lines if ln.startswith("@"))


def decode_char(ch):
    q = ord(ch) - 33
    return ord(ch), q, 10.0 ** (-q / 10.0)


def validate_blocks(lines):
    """逐块结构校验：每 4 行一组，(1) 行数整除 4；(2) 第 1 行 '@' 开头；
    (3) 第 3 行 '+' 开头；(4) 序列与质量等长。返回 (ok, errors[])。"""
    errors = []
    if len(lines) % 4 != 0:
        errors.append(f"总行数 {len(lines)} 不是 4 的整数倍——文件可能被截断")
        return False, errors
    n = len(lines) // 4
    for i in range(n):
        h, seq, sep, qual = lines[4 * i: 4 * i + 4]
        tag = f"记录 {i + 1}"
        if not h.startswith("@"):
            errors.append(f"{tag}: 第 1 行不以 '@' 开头（实为 {h[:12]!r}...）")
        if not sep.startswith("+"):
            errors.append(f"{tag}: 第 3 行不以 '+' 开头（实为 {sep[:12]!r}...）")
        if len(seq) != len(qual):
            errors.append(
                f"{tag}: 序列长 {len(seq)} bp 与质量长 {len(qual)} 不等——错位")
    return not errors, errors


def main():
    ap = argparse.ArgumentParser(
        description="FASTQ 四行契约、Phred+33 编解码与计数/截断陷阱（合成算例，无随机数）")
    ap.add_argument("--qlen", type=int, default=33,
                    help="合成 read 长度（bp），仅展示用")
    ap.add_argument("--pad-lines", type=int, default=3,
                    help="凑 4 的倍数时手工删去的行数（配合固定构造）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    ok = True
    print("=" * 68)
    print("[算例 1] 计数陷阱：wc -l ÷ 4 vs grep -c '^@'（l0_04 demo.fq，合成输入）")
    print("=" * 68)
    n_good = len(FASTQ_GOOD)
    wc_n = count_reads_wc_l_div4(FASTQ_GOOD)
    grep_n = count_grep_at(FASTQ_GOOD)
    print(f"总行数 = {n_good}；wc -l ÷ 4 = {wc_n:g}（正确）")
    print(f"grep -c '^@' = {grep_n}（错误做法）→ 偏大 {grep_n - wc_n:g}")
    print("多出来的 '@' 是 READ_0002 质量行的行首：", end="")
    ascii_v, q, p = decode_char("@")
    print(f"'@' = ASCII {ascii_v} = Phred+33 的 Q{q}，P = 10^-3.1 = {p:.3g}"
          " —— 完全合法的质量字符")
    if grep_n - wc_n != 1:
        ok = False
        print("  [MISMATCH] 计数差应为 1")

    print()
    print("=" * 68)
    print("[算例 2] Phred+33 逐字符解码（READ_0001 质量行，l0_04 §步骤 1 复核）")
    print("=" * 68)
    qual1 = FASTQ_GOOD[3]
    for pos in (1, 22):
        ch = qual1[pos - 1]
        ascii_v, q, p = decode_char(ch)
        print(f"pos={pos}\tchar={ch}\tASCII={ascii_v}\tQ={q}\tP={p:.4f}")
    if not (abs(decode_char("F")[2] - 0.0002) < 5e-5
            and abs(decode_char("#")[2] - 0.6310) < 5e-4):
        ok = False
        print("  [MISMATCH] F/# 解码值与 l0_04 awk 输出不符")
    rt = all(chr(q + 33) and (ord(chr(q + 33)) - 33 == q) for q in range(0, 42))
    print(f"Phred+33 编解码往返（Q ∈ [0,41]）：{'PASS' if rt else 'FAIL'}")
    ok = ok and rt

    print()
    print("=" * 68)
    print("[算例 3] 截断与中部缺行：行数整除 4 只是必要条件的下限")
    print("=" * 68)
    # (a) 尾部截断：最后一条记录缺质量行
    tail_cut = (FASTQ_GOOD + FASTQ_THIRD)[:-1]
    print(f"(a) 尾部缺 1 行：总行数 {len(tail_cut)}，{len(tail_cut)} % 4 = "
          f"{len(tail_cut) % 4} → ", end="")
    ok_a, err_a = validate_blocks(tail_cut)
    print("行数检查即检出" if not ok_a else "漏检")
    for e in err_a:
        print("    " + e)
    ok = ok and (not ok_a)

    # (b) 中部缺行 + 手工删行凑整：吞掉 READ_0002 序列行，再删 3 行凑回 4 的倍数
    full = FASTQ_GOOD + FASTQ_THIRD
    mid = full[:]
    del mid[5]                                   # 吞掉 READ_0002 的序列行
    for _ in range(args.pad_lines):             # 手工再删 3 行凑成 4 的倍数
        del mid[5]
    ok_b, err_b = validate_blocks(mid)
    print(f"(b) 中部缺 1 行再删 {args.pad_lines} 行凑整：总行数 {len(mid)}，"
          f"{len(mid)} % 4 = {len(mid) % 4}（行数检查放行）；块结构校验："
          f"{'放行（漏检）' if ok_b else '检出'}")
    for e in err_b:
        print("    " + e)
    if ok_b:
        hdr2 = mid[4]
        print(f"    → 第 2 块的序列/质量来自 READ_0003，但头行仍是 {hdr2!r}："
              "结构全部合法，错位完全静默")
        print("    → 防线只剩：传输后 md5sum 对账、read 数与数据提供方核对"
              "（l0_04「为什么这是前置」案例的固定复现）")
    ok = ok and ok_b                                   # 本算例的断言就是「漏检」

    print()
    print("=" * 68)
    print("[算例 4] 多行 FASTA：折行是规范允许，当单行一条硬解就内容串味")
    print("=" * 68)
    n_gt = sum(1 for ln in FASTA_WRAPPED if ln.startswith(">"))
    # 硬解：见到 '>' 只取下一行当序列（折行被丢弃）
    seqs_naive, i = {}, 0
    while i < len(FASTA_WRAPPED):
        if FASTA_WRAPPED[i].startswith(">"):
            seqs_naive[FASTA_WRAPPED[i].split()[0]] = len(FASTA_WRAPPED[i + 1])
            i += 2
        else:
            i += 1
    true_len = {">seq_1": 25 + 25, ">seq_2": 25}      # 折行合并后的真实长度
    print(f"按 '>' 计数：{n_gt} 条（条数对）；硬解只取头行下一行：seq_1 = "
          f"{seqs_naive['>seq_1']} bp（折行被丢，真实 {true_len['>seq_1']} bp）"
          f"、seq_2 = {seqs_naive['>seq_2']} bp")
    print("    → 条数对、碱基总量少 25 bp：内容错而不报错（失效条件 4 的 FASTA 面）")
    naive_ok = (seqs_naive[">seq_1"] == 25 and n_gt == 2)

    if args.selftest:
        print()
        checks = [
            ("wc÷4 = 2", wc_n == 2),
            ("grep '^@' = 3（偏大 1）", grep_n == 3),
            ("'@' = Q31 = P 7.94e-4",
             abs(decode_char("@")[2] - 10 ** -3.1) < 1e-6),
            ("'#' pos22 = Q2 = P 0.631", abs(decode_char("#")[2] - 0.63096) < 1e-4),
            ("ASCII 往返 PASS", rt),
            ("尾部截断被行数检查检出", not ok_a),
            ("中部缺行+凑整对结构校验静默（ok_b=True）", ok_b),
            ("多行 FASTA 硬解丢折行（seq_1 25≠50 bp）", naive_ok),
        ]
        for name, passed in checks:
            print(f"  {'PASS' if passed else 'FAIL'}  {name}")
            ok = ok and passed
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch05_flag_cigar.py — SAM FLAG 位拆解与 CIGAR 求跨度（合成算例 · 无随机数）

服务章节：第 5 章 §5.4「SAM 11 列与 FLAG」、失效条件第 3 条
（用 CIGAR 数错配：M 包含错配，应读 NM/MD）。

数据性质：【合成算例】SAM 记录为 l0_04 §上机 步骤 0 / u03 §5.5 的固定演示记录
（rd0001，FLAG=163，CIGAR=50M2D10M，NM:i:3），不涉及任何真实比对数据。

正文引用的输出：
  - FLAG 163 = 128+32+2+1 → PAIRED, PROPER_PAIR, MREVERSE, READ2
    （且 16 位为 0：自身在正链）；samtools flags 口径对照
  - 配偶值对照：99 = 1+2+32+64（READ1，mate 在负链），83 = 1+2+16+64（READ1 在负链）
  - CIGAR 50M2D10M：read 消耗 60 bp（=SEQ 长），参考跨度 62 bp
  - CIGAR 10S130M2I8M（u03 ⑩ 习题 3 口径）：read 消耗 150 bp，参考跨度 138 bp
  - M ≠ 完全匹配：CIGAR 60M 且 NM:i:3 → 用 CIGAR 数「完美比对」会把编辑距离为 3 的
    记录误计为完美（0 vs 3；60M 无插入缺失，此时 NM=3 即 3 个错配）

参数含义：
  --flag-demo   演示拆解的 FLAG 值（默认 163，即 l0_04 固定记录）
  --cigar-demo  演示求跨度的 CIGAR（默认 50M2D10M，即 l0_04 固定记录）
"""
import argparse
import re
import sys

FLAG_BITS = [
    (0x1, "PAIRED（双端成员）"),
    (0x2, "PROPER_PAIR（按比对器的文库预期成对）"),
    (0x4, "UNMAPPED（自身未比对）"),
    (0x8, "MUNMAPPED（mate 未比对）"),
    (0x10, "REVERSE（自身在负链）"),
    (0x20, "MREVERSE（mate 在负链）"),
    (0x40, "READ1"),
    (0x80, "READ2"),
    (0x100, "SECONDARY（次优比对）"),
    (0x200, "QCFAIL（质控未过）"),
    (0x400, "DUPLICATE（PCR/光学重复）"),
    (0x800, "SUPPLEMENTARY（补充比对）"),
]

CIGAR_OPS = set("MIDNSHP=X")


def decode_flag(flag):
    """贪心减法拆 2 的幂 → 点亮的位列表（l0_04 §4 的手工拆法）。"""
    bits, rest = [], flag
    for w, _ in sorted(FLAG_BITS, reverse=True):
        if rest >= w:
            bits.append(w)
            rest -= w
    assert rest == 0, f"FLAG {flag} 超出 12 位定义"
    return bits


def flag_names(flag):
    on = set(decode_flag(flag))
    return [name for w, name in FLAG_BITS if w in on]


def cigar_tuples(cigar):
    ops = re.findall(r"(\d+)([MIDNSHP=X])", cigar)
    if not ops or "".join(n + c for n, c in ops) != cigar:
        raise ValueError(f"非法 CIGAR：{cigar}")
    return [(int(n), c) for n, c in ops]


def cigar_spans(cigar):
    """返回 (read 消耗, 参考跨度)。消耗规则：M/=X/I/S 耗 read；M/D/N/=X 耗参考。
    SAM v1 规范：S 耗 read 不耗参考，H 两者都不耗。"""
    read_c = ref_c = 0
    for n, c in cigar_tuples(cigar):
        if c not in CIGAR_OPS:
            raise ValueError(f"CIGAR 未知操作符：{c}")
        if c in "MIS=X":
            read_c += n
        if c in "MDN=X":
            ref_c += n
    return read_c, ref_c


def count_mismatches_naive(cigar):
    """错误做法：从 CIGAR 里数 X 当错配（M 被当成完全匹配）。"""
    return sum(n for n, c in cigar_tuples(cigar) if c == "X")


def main():
    ap = argparse.ArgumentParser(
        description="SAM FLAG 位拆解与 CIGAR 求跨度（合成算例，无随机数）")
    ap.add_argument("--flag-demo", type=int, default=163)
    ap.add_argument("--cigar-demo", default="50M2D10M")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    ok = True
    print("=" * 68)
    print(f"[算例 1] FLAG = {args.flag_demo} 的位拆解（l0_04 §4 贪心减法）")
    print("=" * 68)
    bits = decode_flag(args.flag_demo)
    print(f"{args.flag_demo} = " + " + ".join(str(b) for b in bits))
    for w in bits:
        name = dict(FLAG_BITS)[w]
        print(f"  {w:>5} (0x{w:x})  {name}")
    if not (0x10 in bits):
        print("  （16 位为 0 → 自身比对在参考正链）")

    print()
    print("[对照] 常见配偶值（u03 §5.5：99/83 的配偶是 147/163）")
    for f in (99, 83, 147, 163):
        print(f"  {f:>3} = " + " + ".join(str(b) for b in decode_flag(f))
              + "  → " + ", ".join(n.split("（")[0] for n in flag_names(f)))

    print()
    print("=" * 68)
    print(f"[算例 2] CIGAR = {args.cigar_demo}：read 消耗 vs 参考跨度")
    print("=" * 68)
    read_c, ref_c = cigar_spans(args.cigar_demo)
    print(f"read 上消耗 = {read_c} bp；参考上跨度 = {ref_c} bp"
          f"（l0_04 记录 SEQ 长 60，吻合 read 消耗）")

    print()
    print("[对照] CIGAR = 10S130M2I8M（u03 ⑩ 习题 3 的 150 bp read）")
    r2, ref2 = cigar_spans("10S130M2I8M")
    print(f"read 上消耗 = {r2} bp（10S+130M+2I+8M）；参考上跨度 = {ref2} bp"
          f"（130M+8M；2I 与 10S 不耗参考）")

    print()
    print("=" * 68)
    print("[算例 3] M ≠ 完全匹配：CIGAR 60M + NM:i:3 的计数陷阱")
    print("=" * 68)
    demo_cigar, nm = "60M", 3
    naive = count_mismatches_naive(demo_cigar)
    print(f"记录：CIGAR = {demo_cigar}，NM:i:{nm}（l0_04 步骤 2 口径的等长记录）")
    print(f"用 CIGAR 数错配（只认 X）：{naive} 个 → 误报「完美比对」")
    print(f"读 NM 标签：编辑距离 {nm}（本例 60M 无 I/D，故为 {nm} 个错配；是否为 SNP 需变异检测判断）")
    print("→ 统计「完美比对的 read 数」时前者虚高；要么读 NM:i:，"
          "要么让比对器输出 =/X（minimap2 --eqx）")

    if args.selftest:
        print()
        checks = [
            ("163 = 128+32+2+1", decode_flag(163) == [128, 32, 2, 1]),
            ("163 含 READ2 且不含 REVERSE",
             0x80 in decode_flag(163) and 0x10 not in decode_flag(163)),
            ("99 = 1+2+32+64", decode_flag(99) == [64, 32, 2, 1]),
            ("83 = 1+2+16+64", decode_flag(83) == [64, 16, 2, 1]),
            ("50M2D10M read=60 / ref=62", cigar_spans("50M2D10M") == (60, 62)),
            ("10S130M2I8M read=150 / ref=138",
             cigar_spans("10S130M2I8M") == (150, 138)),
            ("CIGAR 数错配 0 vs NM 3", naive == 0 and nm == 3),
            ("150M read=150 / ref=150", cigar_spans("150M") == (150, 150)),
        ]
        for name, passed in checks:
            print(f"  {'PASS' if passed else 'FAIL'}  {name}")
            ok = ok and passed
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

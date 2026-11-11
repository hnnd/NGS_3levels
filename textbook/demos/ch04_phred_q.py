#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch04_phred_q.py — Phred Q 值、判错概率与 ASCII+33 编码的换算表（合成算例 · 无随机数）

服务章节：第 4 章 §4.4「质量分数 Q 值」概念小节、失效条件第 1 条
（Illumina 3' 端质量衰退是化学问题不是样本问题）的定量基础。

数据性质：【合成算例】本脚本只做纯算术换算与固定输入的解码演示，
不涉及任何真实测序数据，所有输出不得写成真实样本的实测结果。

正文引用的输出：
  - 讲义 u03 §4.7 高频质量字符表（!, #, 5, ?, I, J 的 Q 值与判错概率）逐格复核
  - u03 §4.7「150 bp 全 Q30 读段平均含 0.15 个错误碱基 → 约每 6–7 条出现 1 个」
  - u03 §4.7「15 kb 读段单点错误率 10% → 每条平均含约 1500 个错误碱基（上千个）」
  - Phred+33 编解码往返一致性（ASCII = Q + 33）

参数含义：
  --read-len-short  短读长长度（bp），用于「每条期望错误数」算例
  --read-len-long   长读长长度（bp），用于 CLR 高错误率算例
  --q-short         短读长算例的单碱基 Q 值（假设全读段均匀为此 Q，属设例口径）
  --p-long          长读长算例的单碱基错误率（CLR 口径设例）
"""
import argparse
import sys

TABLE_CHARS = ["!", "#", "5", "?", "I", "J"]  # 讲义 u03 §4.7 高频质量字符表


def q_to_p(q):
    return 10.0 ** (-q / 10.0)


def encode_ascii(q):
    return chr(q + 33)


def decode_ascii(ch):
    return ord(ch) - 33


def main():
    ap = argparse.ArgumentParser(
        description="Phred Q ↔ 判错概率 ↔ ASCII+33 换算表（合成算例，无随机数）")
    ap.add_argument("--read-len-short", type=int, default=150)
    ap.add_argument("--read-len-long", type=int, default=15000)
    ap.add_argument("--q-short", type=int, default=30)
    ap.add_argument("--p-long", type=float, default=0.10)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    print("=" * 64)
    print("[表 1] Phred+33 高频质量字符解码（合成算例 · 纯算术复核）")
    print("=" * 64)
    print(f"{'字符':<6}{'ASCII':<8}{'Q 值':<8}{'判错概率 P':<18}{'%'}")
    ok = True
    expected = {"!": 0, "#": 2, "5": 20, "?": 30, "I": 40, "J": 41}
    for ch in TABLE_CHARS:
        q = decode_ascii(ch)
        p = q_to_p(q)
        print(f"{ch:<6}{ord(ch):<8}{q:<8}{p:<18.6g}{p * 100:.4g}")
        if q != expected[ch]:
            ok = False
            print(f"  [MISMATCH] {ch} 期望 Q={expected[ch]} 实得 {q}")

    print()
    print("[往返] ASCII = Q + 33 编解码一致性：", end="")
    roundtrip = all(decode_ascii(encode_ascii(q)) == q for q in range(0, 42))
    print("PASS" if roundtrip else "FAIL")
    ok = ok and roundtrip

    print()
    print("=" * 64)
    print("[算例 A] 短读长每条期望错误数（讲义 u03 §4.7 第 1 步跨越）")
    print("=" * 64)
    p_s = q_to_p(args.q_short)
    exp_err = args.read_len_short * p_s
    reads_per_err = 1.0 / exp_err
    print(f"设例：{args.read_len_short} bp 读段、全读段均匀 Q{args.q_short}"
          f"（P={p_s:.4g}）")
    print(f"每条期望错误数 = {args.read_len_short} × {p_s:.4g} = {exp_err:.3f}")
    print(f"平均约每 {reads_per_err:.2f} 条读段出现 1 个错误碱基")
    print("→ 复核讲义表述『平均每 6–7 条才可能出现 1 个错误碱基』："
          f"{'一致' if 6 <= reads_per_err <= 7 else '不一致'}")

    print()
    print("=" * 64)
    print("[算例 B] 长读长（CLR 口径）每条期望错误数（u03 §4.7 同段）")
    print("=" * 64)
    exp_err_l = args.read_len_long * args.p_long
    print(f"设例：{args.read_len_long} bp 读段、单点错误率 {args.p_long:.0%}")
    print(f"每条期望错误数 = {args.read_len_long} × {args.p_long:.2f} = "
          f"{exp_err_l:.0f}")
    print(f"→ 复核讲义表述『每条 Read 内部均匀混杂上千个错误碱基』："
          f"{'一致（≥1000）' if exp_err_l >= 1000 else '不一致'}")

    if args.selftest:
        print()
        checks = [
            ("! → Q0 → P=1.0", abs(q_to_p(decode_ascii("!")) - 1.0) < 1e-12),
            ("? → Q30 → P=0.001", abs(q_to_p(decode_ascii("?")) - 1e-3) < 1e-12),
            ("I → Q40 → P=1e-4", abs(q_to_p(decode_ascii("I")) - 1e-4) < 1e-15),
            ("Q20 及格线 P=0.01", abs(q_to_p(20) - 0.01) < 1e-12),
            ("150 bp × Q30 = 0.15 错/条", abs(args.read_len_short * q_to_p(args.q_short) - 0.15) < 1e-9),
            ("约 6–7 条 1 错（6.67）", abs(reads_per_err - 6.6667) < 0.01),
            ("15 kb × 10% = 1500 错/条", abs(exp_err_l - 1500) < 1e-9),
            ("ASCII 编解码往返 PASS", roundtrip),
        ]
        for name, passed in checks:
            print(f"  {'PASS' if passed else 'FAIL'}  {name}")
            ok = ok and passed
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

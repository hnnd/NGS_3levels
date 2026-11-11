#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch05_bed_gff_coords.py — BED 0-based 半开 vs GFF 1-based 闭区间的 off-by-one 对照（合成算例 · 无随机数）

服务章节：第 5 章 §5.4「区间格式与坐标系」（硕士深入块）、失效条件第 1 条
（BED 0-based 半开与 GFF/VCF 1-based 闭混用，坐标差一位而不报错）。
坐标系口径以 TERMINOLOGY.md §2-3 为准：BED 0-based 半开；SAM/VCF/GFF 1-based 闭。

数据性质：【合成算例】序列为讲义 u03 §5.7 的五碱基 ATGCA 与 u03 ⑩ 习题 5 的
捕获区间设例，不涉及任何真实基因组坐标。

正文引用的输出：
  - 五碱基 ATGCA 圈定 TGC：GFF(1-based 闭) [2,4]，长度 4−2+1=3；
    BED(0-based 半开) [1,4)，长度 4−1=3——两种写法覆盖同一物理区间
  - 转换黄金法则：BED_start = GFF_start − 1，BED_end = GFF_end
  - u03 ⑩ 习题 5：GFF chr1 1000 1200 直接抄进 BED 写成 chr1 1000 1200，
    BED [1000,1200) 实际覆盖 1-based 的 1001..1200 = GFF [1001,1200]：
    左边界漏掉第 1000 号碱基，且区间长度从 201 bp 变 200 bp——全程无报错
  - 相邻区间无歧义相接：外显子 [0,100) + [100,250) 在切点 100 天然重合

参数含义：
  --gff-start / --gff-end   习题 5 的 GFF 捕获区间（默认 1000/1200）
"""
import argparse
import sys


def gff_to_bed(start1, end1):
    """GFF(1-based 闭) → BED(0-based 半开)：唯一被允许的平移。"""
    return start1 - 1, end1


def bed_to_gff(start0, end0):
    """BED(0-based 半开) → GFF(1-based 闭)。"""
    return start0 + 1, end0


def len_gff(start1, end1):
    return end1 - start1 + 1


def len_bed(start0, end0):
    return end0 - start0


def main():
    ap = argparse.ArgumentParser(
        description="BED 0-based 半开 vs GFF 1-based 闭区间的 off-by-one 对照"
                    "（合成算例，无随机数）")
    ap.add_argument("--gff-start", type=int, default=1000)
    ap.add_argument("--gff-end", type=int, default=1200)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    ok = True
    print("=" * 68)
    print("[算例 1] 同一物理区间的两种写法（u03 §5.7 五碱基 ATGCA，圈定 TGC）")
    print("=" * 68)
    seq = "ATGCA"
    g_s, g_e = 2, 4                       # GFF 1-based 闭：第 2..4 号碱基 = TGC
    b_s, b_e = gff_to_bed(g_s, g_e)       # BED 0-based 半开
    print(f"序列（1-based 编号）：1:{seq[0]} 2:{seq[1]} 3:{seq[2]} 4:{seq[3]} "
          f"5:{seq[4]}")
    print(f"GFF(1-based 闭)  [{g_s}, {g_e}]   长度 = {g_e} − {g_s} + 1 = "
          f"{len_gff(g_s, g_e)}")
    print(f"BED(0-based 半开) [{b_s}, {b_e})   长度 = {b_e} − {b_s} = "
          f"{len_bed(b_s, b_e)}")
    print(f"两式覆盖的都是 {seq[g_s-1:g_e]}（第 {g_s}..{g_e} 号碱基）")
    if not (seq[g_s - 1:g_e] == "TGC" and len_gff(g_s, g_e) == len_bed(b_s, b_e) == 3):
        ok = False
        print("  [MISMATCH] 区间或长度与讲义口径不符")

    print()
    print("=" * 68)
    print("[算例 2] 不转换直接抄：u03 ⑩ 习题 5 的探针捕获（合成设例）")
    print("=" * 68)
    gs, ge = args.gff_start, args.gff_end
    correct_bed = gff_to_bed(gs, ge)
    wrong_bed = (gs, ge)                  # 把 GFF 数字原封抄进 BED 列
    print(f"GFF 注释外显子：chr1 {gs} {ge}（1-based 闭，"
          f"{len_gff(gs, ge)} bp：第 {gs}..{ge} 号碱基）")
    print(f"正确 BED：chr1 {correct_bed[0]} {correct_bed[1]}"
          f"（start = {gs} − 1）")
    print(f"错误 BED：chr1 {wrong_bed[0]} {wrong_bed[1]}（照抄）→ 实际覆盖 "
          f"1-based 第 {bed_to_gff(*wrong_bed)[0]}..{bed_to_gff(*wrong_bed)[1]} 号"
          f" = GFF [{bed_to_gff(*wrong_bed)[0]}, {bed_to_gff(*wrong_bed)[1]}]，"
          f"{len_bed(*wrong_bed)} bp")
    lost = gs                             # 漏掉的左端碱基编号
    print(f"→ 左边界漏掉第 {lost} 号碱基（外显子第一个碱基），"
          f"右端第 {ge} 号仍被覆盖；长度差 1 bp。全程没有任何报错。")

    print()
    print("=" * 68)
    print("[算例 3] 半开区间为什么存在：相邻外显子在切点天然重合")
    print("=" * 68)
    e1, e2 = (0, 100), (100, 250)
    print(f"外显子 1 BED [{e1[0]}, {e1[1]})（{len_bed(*e1)} bp）+ "
          f"外显子 2 BED [{e2[0]}, {e2[1]})（{len_bed(*e2)} bp）")
    print(f"切点 = {e1[1]} = {e2[0]}：无重叠无缺口，merge/区间树零边界歧义"
          f"（l0_04 §5 的设计理由）")

    if args.selftest:
        print()
        checks = [
            ("[2,4] ↔ [1,4) 同覆盖 TGC",
             gff_to_bed(2, 4) == (1, 4) and bed_to_gff(1, 4) == (2, 4)),
            ("GFF 长 = end−start+1 = 3", len_gff(2, 4) == 3),
            ("BED 长 = end−start = 3", len_bed(1, 4) == 3),
            ("习题5 正确 BED = [999, 1200)",
             gff_to_bed(args.gff_start, args.gff_end) == (999, 1200)),
            ("照抄 BED [1000,1200) 实际 = GFF [1001,1200]",
             bed_to_gff(1000, 1200) == (1001, 1200)),
            ("照抄丢左端第 1000 号碱基、长差 1",
             bed_to_gff(1000, 1200)[0] == 1001
             and len_gff(1000, 1200) - len_bed(1000, 1200) == 1),
            ("相邻半开区间切点重合", (0, 100)[1] == (100, 250)[0]),
        ]
        for name, passed in checks:
            print(f"  {'PASS' if passed else 'FAIL'}  {name}")
            ok = ok and passed
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

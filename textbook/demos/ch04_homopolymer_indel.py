#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch04_homopolymer_indel.py — 纳米孔同聚物长度误判：随机误差可投票、系统偏差不可（合成算例）

服务章节：第 4 章 §4.4「Oxford Nanopore」概念小节（同聚物盲区）、
§4.4 平台比较表「均聚物定量易失准」、失效条件第 2 条
（纳米孔在同聚物区以插入缺失为主，投票纠错对系统性偏差无效）。

数据性质：【合成算例】孔道电流与马达步进均为固定种子的简化数学模型，
与任何真实 run / basecaller 版本无关；所有输出不得写成真实样本的实测结果。
模型口径（显式简化的教学模型，非 basecaller 复刻）：
  - 同聚物真实长度 L 的「观测时长」 d = L + N(0, σ·√L)（随机成分，泊松式计数噪声）
  - L ≥ --bias-onset 时模型加入系统性少判 --bias-len 个碱基（电流平台期造成的
    固定方向误判，与噪声无关、逐次调用恒定同向）
  - 单次调用 = round(d) - bias；「投票」= 对 --votes 次独立调用取均值再 round

正文引用的输出：
  - 单次调用 indel 率随 L 上升（同聚物越长越不准，u03 §4.3 / l0_04 §1 机制）
  - 投票使纯随机区（L < bias-onset）的错误率下降约一个数量级
  - 系统偏差区（L ≥ bias-onset）投票后错误率仍 ≈ 100%（失效条件 2 的定量演示）

参数含义：
  --lens          同聚物真实长度列表，逗号分隔
  --sigma         时长噪声强度 σ（噪声 = N(0, σ·√L)）
  --bias-onset    系统性少判的起始长度（默认 7，对应讲义「连续 7 个 A」量级）
  --bias-len      系统性少判的碱基数（恒定方向、与噪声无关）
  --votes         投票所用的独立调用次数（默认 51，奇数避免均值恰在
                  半整数处徘徊；独立噪声按 1/√votes 收窄）
  --trials        每个 (L, 档) 的重复次数
  --seed          随机种子（固定，保证可复现）
"""
import argparse
import sys

import numpy as np


def call_lengths(true_l, sigma, bias_onset, bias_len, n, rng):
    """n 次独立调用的判定长度（合成模型，见文件头）。"""
    dwell = true_l + rng.normal(0.0, sigma * np.sqrt(true_l), n)
    called = np.round(dwell)
    if true_l >= bias_onset:
        called = called - bias_len
    return np.maximum(called, 1)


def main():
    ap = argparse.ArgumentParser(
        description="同聚物长度误判：随机误差可投票稀释、系统偏差不可（合成算例）")
    ap.add_argument("--lens", default="1,2,3,4,5,6,7,8,10,12")
    ap.add_argument("--sigma", type=float, default=0.7)
    ap.add_argument("--bias-onset", type=int, default=7)
    ap.add_argument("--bias-len", type=int, default=1)
    ap.add_argument("--votes", type=int, default=51)
    ap.add_argument("--trials", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20261103)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    lens = [int(x) for x in args.lens.split(",")]

    print("=" * 78)
    print(f"[合成算例] 同聚物长度判定模型：σ={args.sigma}、系统少判起点 "
          f"L≥{args.bias_onset}（-{args.bias_len} bp）、投票 {args.votes} 次、"
          f"每档 {args.trials} 次重复、seed={args.seed}")
    print("=" * 78)
    hdr = (f"{'真实 L':<8}{'单次 indel 率':<14}{'单次偏移(bp)':<14}"
           f"{'投票 indel 率':<14}{'投票偏移(bp)'}")
    print(hdr)
    stats = {}
    for l in lens:
        single = call_lengths(l, args.sigma, args.bias_onset, args.bias_len,
                              args.trials, rng)
        single_err = float((single != l).mean())
        single_shift = float((single - l).mean())
        # 投票：trials 组、每组 votes 次独立调用的均值再 round
        votes_mat = call_lengths(l, args.sigma, args.bias_onset, args.bias_len,
                                 args.trials * args.votes, rng)
        vote = np.round(votes_mat.reshape(args.trials, args.votes).mean(axis=1))
        vote_err = float((vote != l).mean())
        vote_shift = float((vote - l).mean())
        stats[l] = (single_err, vote_err, single_shift, vote_shift)
        print(f"{l:<8}{single_err:<14.3f}{single_shift:<+14.2f}"
              f"{vote_err:<14.3f}{vote_shift:<+14.2f}")

    print()
    print("[观察 1] L 越大单次调用越不准：随机噪声 ∝√L，长度判定的绝对误差窗口不变")
    print("[观察 2] 纯随机区（L < 系统偏差起点）：投票错误率较单次下降约一个数量级"
          "（独立噪声被平均）")
    print("[观察 3] 系统偏差区（L ≥ 起点）：每次调用同向少判，投票均值仍是 L-"
          f"{args.bias_len}，错误率不降——失效条件第 2 条的定量演示")

    if args.selftest:
        print()
        ok = True
        s_short = stats[args.bias_onset - 1]  # 纯随机区代表
        s_long = stats[args.bias_onset]       # 系统偏差区代表
        checks = [
            ("随机区：投票错误率 < 单次错误率的 1/5",
             s_short[1] < s_short[0] / 5),
            ("随机区：投票后平均偏移 ≈ 0（|shift| < 0.1 bp）",
             abs(s_short[3]) < 0.1),
            ("偏差区：单次平均偏移 = -bias_len",
             abs(s_long[2] + args.bias_len) < 0.15),
            ("偏差区：投票后平均偏移仍 = -bias_len（投票无效）",
             abs(s_long[3] + args.bias_len) < 0.1),
            ("偏差区：投票错误率仍 > 90%",
             s_long[1] > 0.9),
            ("单次 indel 率随 L 总体上升（首末档对比）",
             stats[lens[-1]][0] > stats[lens[0]][0]),
        ]
        for name, passed in checks:
            print(f"  {'PASS' if passed else 'FAIL'}  {name}")
            ok = ok and passed
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

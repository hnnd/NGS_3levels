#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch15_atac_fragment_model.py — ATAC 片段长度阶梯与「为什么必须 --nomodel」（合成算例）

服务章节：第 15 章 §15.4 概念与方法（MACS2 双峰位移模型、ATAC 的 Tn5 切割几何）、
§15.5 失效条件第 1 条「ATAC 用 MACS2 默认双峰模型，peak 过碎」。
源讲义：m05 §4.3 末段、⑤ 步骤 1/2、⑥ 6.1、⑨ 错误 1。

物理事实（两条都有原始文献支撑，见讲义 ⑪：Buenrostro 2013；MACS 模型 Zhang 2008）：
  * ChIP-seq 单端读段：仪器只测片段 5' 端。正链 reads 富集在真实结合位点上游 d/2 处、
    负链 reads 富集在下游 d/2 处（d = 片段长度）→ 正负链 5' 密度互相关在滞后 = d 处
    出现主峰 → MACS2 PeakModel 用成对正负峰估 d，再把 reads 平移 d/2 对齐。
  * ATAC：Tn5 双亚基在两条单链上留下的交错切口只隔 9 bp，开放位点中心直接同时被切，
    没有「先打断、两端分开 d」的结构 → 互相关主峰在滞后 = 9 bp（Tn5 stagger），
    在 MACS2 扫描的成对峰区间（几十–几百 bp）里找不到成对峰 →
    PeakModel 报 "Fewer paired peaks (N) than 1000! Model may not be build well!"
    （MACS2 v2.2.9.1 PeakModel.pyx L145 原文），建模失败。
  * MACS2 v2.2.9.1 OptValidator.py L226-228：-f BAMPE/BEDPE 时 options.shift 被清零
    （paired-end 模式 shift 无操作）、L71 强制 nomodel=True；PE 模式下 --extsize 也不参与
    pileup（PeakDetect.pyx L309 PE 时 d=0）。→ 课程数据是双端：脚本里
    --shift -100 --extsize 200 实际无操作，真正起作用的是 -f BAMPE（片段两端定界）
    与 --keep-dup all；这两个参数只对**单端** ATAC 有意义（见 CASE-CH15-02）。

模型（合成，非 PRJDB36269 或任何真实样本）：
  Part 1：片段长度分布。正常 ATAC = 核小体阶梯混合分布
    （NFR ~ N(80,15) 占 0.50；单核 ~ N(200,20) 占 0.30；双核 ~ N(400,25) 占 0.15；
    三核 ~ N(600,30) 占 0.05）；消化过度对照 = 单峰 N(130,20)（讲义 ⑥6.1「不对的样子」）。
    检验阶梯：三个模式 bin 各出现局部极大，且相邻模式间距 ≈ 180–200 bp。
  Part 2：链移位互相关。1 500 个开放位点撒进 60 kb 合成区：
    ChIP-SE 口径：每片段 [c−d/2, c+d/2]，+5' 在 c−d/2、−5' 在 c+d/2（d~N(220,25)）；
    ATAC-SE 口径：+5' 在切口 p、−5' 在 p+9（9 bp 交错），片段长度按 Part 1 阶梯抽。
    对 +/− 5' 密度做滞后 0–500 bp 互相关，找峰。
  Part 3：强行错误建模的后果（设例）：若按默认模型用 d=200 bp 平移对齐，
    估计的峰中心偏离真实 Tn5 切口 d/2 = 100 bp（定量陈述，标设例）。

参数（--help 可见）：
  --n-sites     合成开放位点数（默认 1500）
  --region-bp   合成区长度 bp（默认 60000）
  --read-len    读长（仅打印上下文，默认 100）
  --seed        随机种子（默认 20260829）

正文引用的输出：
  - Part 1：阶梯分布 vs 消化过度的模式 bin 判定（核小体周期 ≈ 190 bp）；
  - Part 2：ChIP 互相关峰位 ≈ 片段长度（~220 bp）、ATAC 互相关峰位 = 9 bp 且
    50–500 bp 区间无峰 → 「MACS2 默认模型对 ATAC 建不出模型」的定量演示；
  - Part 3：错误建模的中心偏移量 = 100 bp（设例数）。

依赖：Python 标准库 + numpy + scipy（scipy 仅用于找直方图局部极大）。
合成算例：所有位点/片段长度均为随机数生成器产物，与任何真实样本无关。
"""
import argparse
import sys

import numpy as np
from scipy.signal import argrelextrema

SEED = 20260829


def atac_ladder_lognorm_mix(rng, n):
    """ATAC 片段长度：核小体阶梯混合（NFR/单/双/三核小体）。"""
    comp = rng.choice(4, size=n, p=[0.50, 0.30, 0.15, 0.05])
    out = np.empty(n)
    for i, c in enumerate(comp):
        if c == 0:
            out[i] = rng.normal(80, 15)
        elif c == 1:
            out[i] = rng.normal(200, 20)
        elif c == 2:
            out[i] = rng.normal(400, 25)
        else:
            out[i] = rng.normal(600, 30)
    return np.clip(np.round(out), 20, 1000).astype(int)


def xcorr_peak(plus, minus, max_lag):
    """+ 与 − 链 5' 密度（1 bp bin）的互相关峰（朴素实现，滞后 0..max_lag）。"""
    best_lag, best_val = 0, -1.0
    vals = np.empty(max_lag + 1)
    for lag in range(max_lag + 1):
        v = float(np.dot(plus[:len(plus) - lag], minus[lag:])) if lag else float(np.dot(plus, minus))
        vals[lag] = v
        if v > best_val:
            best_val, best_lag = v, lag
    return best_lag, best_val, vals


def main():
    ap = argparse.ArgumentParser(
        description="ATAC 片段长度阶梯与 --nomodel 必要性（合成算例；服务第 15 章"
                    "失效条件 1，对齐讲义 m05 ⑨ 错误 1 / §4.3）")
    ap.add_argument("--n-sites", type=int, default=1500)
    ap.add_argument("--region-bp", type=int, default=60000)
    ap.add_argument("--read-len", type=int, default=100)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    # ---------------- Part 1：片段长度阶梯 ----------------
    print("=" * 78)
    print("[Part 1 · 合成算例] 片段长度分布：核小体阶梯 vs 消化过度单峰")
    print("=" * 78)
    frag_atac = atac_ladder_lognorm_mix(rng, args.n_sites)
    frag_over = np.clip(np.round(rng.normal(130, 20, args.n_sites)), 20, 1000).astype(int)
    bins = np.arange(20, 1021, 40)
    labels = [f"{int(b)}–{int(b+39)}" for b in bins[:-1]]
    hist_atac, _ = np.histogram(frag_atac, bins=bins)
    hist_over, _ = np.histogram(frag_over, bins=bins)

    def ladder_modes(hist):
        """核小体阶梯判定：NFR bin、单核 bin、双核 bin 均有局部极大。"""
        ext = argrelextrema(hist, np.greater)[0]
        nfr = any(hist[i] == max(hist[max(0, i - 2):i + 3]) and bins[i] < 140 for i in ext)
        mono = any(bins[i] >= 140 and bins[i] < 280 for i in ext)
        di = any(bins[i] >= 280 and bins[i] < 520 for i in ext)
        return nfr and mono and di, ext

    lad_ok, ext_a = ladder_modes(hist_atac)
    over_ok, ext_o = ladder_modes(hist_over)
    # 相邻模式间距（手算规则：核小体周期 ≈ 组蛋白八聚体占地 ~147 bp + 连接 DNA）
    mono_bin = [i for i in ext_a if 140 <= bins[i] < 280]
    di_bin = [i for i in ext_a if 280 <= bins[i] < 520]
    period = (bins[di_bin[0]] - bins[mono_bin[0]]) if (mono_bin and di_bin) else float("nan")
    print("  直方图 bin（bp）   " + " ".join(f"{l:>7}" for l in labels[:12]))
    print("  正常 ATAC（阶梯）  " + " ".join(f"{h:>7}" for h in hist_atac[:12]))
    print("  消化过度（单峰）  " + " ".join(f"{h:>7}" for h in hist_over[:12]))
    print(f"  正常 ATAC：NFR/单核/双核三模式齐备 = {lad_ok}；"
          f"单核→双核间距 = {period:.0f} bp（核小体周期量级）")
    print(f"  消化过度：三模式齐备 = {over_ok}（只有 ~130 bp 单峰，周期信息已丢失）")
    print("  判读：fraglen.txt 画出来应见 <100 / ~200 / ~400 bp 阶梯（讲义 ⑥6.1）；")
    print("        只剩单峰 = Tn5 量过大/时间过长，这类数据 peak 质量无从谈起。")

    # ---------------- Part 2：链移位互相关 ----------------
    print()
    print("=" * 78)
    print("[Part 2 · 合成算例] 正负链 5' 密度互相关：ChIP 有峰、ATAC 没有")
    print("=" * 78)
    centers = np.sort(rng.choice(args.region_bp - 1000, size=args.n_sites,
                                 replace=False) + 500)
    plus_chip = np.zeros(args.region_bp)
    minus_chip = np.zeros(args.region_bp)
    plus_atac = np.zeros(args.region_bp)
    minus_atac = np.zeros(args.region_bp)
    noise_p = rng.poisson(0.005, args.region_bp)       # 均匀背景读段（正负链独立）
    noise_m = rng.poisson(0.005, args.region_bp)
    plus_chip += noise_p
    minus_chip += noise_m
    plus_atac += rng.poisson(0.005, args.region_bp)
    minus_atac += rng.poisson(0.005, args.region_bp)
    for c in centers:
        d = int(rng.normal(220, 25))                   # ChIP 片段长度
        plus_chip[c - d // 2] += 1                     # +链 5' 在结合位点上游 d/2
        minus_chip[c + d // 2] += 1                    # −链 5' 在下游 d/2
        p = int(c + rng.normal(0, 2))                  # Tn5 切口（两条链 9 bp 交错）
        plus_atac[p] += 1                              # +链 5' 在切口
        minus_atac[p + 9] += 1                         # −链 5' 在切口 +9 bp
    lag_c, val_c, vals_c = xcorr_peak(plus_chip, minus_chip, 500)
    lag_a, val_a, vals_a = xcorr_peak(plus_atac, minus_atac, 500)
    band_a = vals_a[50:501].max()
    print(f"  合成区 {args.region_bp/1000:.0f} kb，{args.n_sites} 个开放位点 + 均匀背景噪声")
    print(f"  ChIP-SE 口径：互相关峰在滞后 {lag_c} bp（≈ 片段长度均值 220）")
    print(f"  ATAC-SE 口径：互相关峰在滞后 {lag_a} bp（Tn5 9 bp 交错切口）；"
          f"50–500 bp 区间最大值/全局峰 = {band_a/val_a:.3f}")
    print("  判读：MACS2 PeakModel 要在几十–几百 bp 里找成对正负峰估片段长度；")
    print("        ATAC 的主峰在 9 bp，扫描区间里没有成对峰 → 建模失败报")
    print('        "Fewer paired peaks (N) than 1000! Model may not be build well!"')
    print("        （PeakModel.pyx L145 原文）→ 必须 --nomodel。")

    # ---------------- Part 3：错误建模的后果（设例） ----------------
    print()
    print("=" * 78)
    print("[Part 3 · 设例] 若强行按默认模型平移：峰中心偏离 Tn5 切口 100 bp")
    print("=" * 78)
    d_forced = 200
    shift = d_forced // 2
    print(f"  设例：MACS2 --fix-bimodal 时用默认 d={d_forced} bp 继续（讲义 ⑨ 错误 1），")
    print(f"  把 reads 平移 d/2 = {shift} bp 对齐 → 估计的峰中心系统性偏离真实")
    print(f"  Tn5 切口 {shift} bp；summit 偏移 → 下游 -size 200 取 summit ±100 bp 时")
    print(f"  motif 窗口整体错位（合成演示：偏差 = |d_forced/2| = {shift} bp，设例数）。")
    print("  MACS2 行为备注（OptValidator.py）：-f BAMPE 时 shift 被清零、nomodel 被")
    print("  强制 True → 双端数据下 --shift/--extsize 是无操作，单端 ATAC 才需要它们。")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        check("Part 1：正常 ATAC 分布检出 NFR/单核/双核三模式（核小体阶梯）", lad_ok)
        check("Part 1：核小体周期在 140–280 bp 区间（单核→双核间距 "
              f"{period:.0f} bp ∈ [140, 280]）", 140 <= period <= 280)
        check("Part 1：消化过度分布检不出三模式（周期信息丢失）", not over_ok)
        check(f"Part 2：ChIP 互相关峰在片段长度处（{lag_c} ∈ [190, 260]）",
              190 <= lag_c <= 260)
        check(f"Part 2：ATAC 互相关全局峰 = Tn5 交错（{lag_a} ≤ 12 bp）", lag_a <= 12)
        check(f"Part 2：ATAC 在 MACS2 建模区间（50–500 bp）无峰"
              f"（比值 {band_a/val_a:.3f} < 0.2）", band_a / val_a < 0.2)
        check("Part 3：错误建模中心偏移 = 100 bp（设例数）", shift == 100)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

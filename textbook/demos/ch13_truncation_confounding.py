#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch13_truncation_confounding.py — 数据准备环节的静默截断：文库大小与分组混杂（合成算例）

服务章节：第 13 章 §13.5 失效条件 4「数据准备环节的静默截断使文库大小与分组混杂」
（真实案例锚点：根 CLAUDE.md「🔴 最贵的一个坑：--max-time 掐断前缀下载」；
下载脚本 06_data/master/download_master.sh 的三处修复，只读、不在本任务复跑）。
为「静默截断如何制造假差异 / 验收为什么必须是产物计数对得上而不是退出码」提供复现入口。

真实案例记录（根 CLAUDE.md 实测记录，2026-08-30 修复；非本脚本模拟）：
  m04/m05 前缀下载产物 29 个文件里 14 个被截断（48%），最少只有目标 3,000,000 条里的
  399,491 条（13%），跨度 13%–84%；脚本不报错、不校验，rc=0。
  根因：curl --max-time 900 配 1125 MB 前缀，在 0.5–1 MB/s 竞争带宽下 900 秒传不完，
  curl 被掐断即少 read。修复：按 ENA 元数据真实压缩比取 540 MB 前缀 + --max-time 3600
  + 产出 read 数校验（不足告警并幂等重下）。

模型（合成算例，非任何真实样本结果）：
  * 基因相对丰度：前 10% 基因携带 70% reads（对齐讲义 m01 §4.5 的叙述量级，合成取值），
    其余基因丰度取对数正态；计数用独立泊松近似多项式抽样（合成算例的常规近似）。
  * 截断 = 只拿到文件前缀：等价为该样本总 reads 按比例 f 缩小（对基因内容近似随机）；
    分组 A 全部 f=1.0，分组 B 的 f ~ U(0.13, 0.84)（对齐真实案例的截断跨度，合成取值）。
  * 分析对照：Welch t 检验作用于 log2(count+1)（不校正文库大小，「把技术差异当生物学」）
    vs log2(CPM+1)（按文库大小归一）；BH q < 0.05。

参数（--help 可见）：
  --genes/--samples   合成基因数 / 每组样本数（默认 4000 / 6）
  --target-reads      目标每样本 read 数（默认 3,000,000，与真实案例一致）
  --de-genes/--fold   功效场景的真差异基因数 / 倍数（默认 900 / 1.5）
  --seed              随机种子

正文引用的输出：
  - Part 0 真实案例数字锚点表（29/14/399,491/13%–84%/rc=0 → 根 CLAUDE.md 记录）
  - Part 1 验收演示：read 数校验（actual == 3,000,000）恰好标记出全部截断文件；
    不校验则脚本「完成」、rc=0 —— 退出码不构成完成判据
  - Part 2a 假差异（全部零假设、截断跨度 13%–84%）：不校正时假阳性率冲到 60.7%
    （高表达层 87.6%），归一后整体与各层都回落 ≈5% —— 「图看起来一切正常」正是这个情形
  - Part 2b 更深截断（f ~ U(0.13, 0.45)，仍在真实跨度内）：低表达层因「检出地板
    零膨胀 + 伪计数不对称」假阳性重新明显高于 5% —— 归一化修得好全局偏移，
    修不了检出地板（失效条件 4 的定量注脚）
  - Part 3 真差异基因的检出率（功效场景）：低表达层检出率在截断组系统性坍塌 ——
    「图看起来一切正常」的另一面：真信号被静默吃掉
"""
import argparse
import math
import sys

import numpy as np
from scipy import stats

SEED = 20261104
TARGET = 3_000_000

# 根 CLAUDE.md「--max-time 掐断前缀下载」的实测记录（教材引用入口，勿改）
REAL_CASE = {
    "files": 29, "truncated": 14,
    "min_reads": 399_491, "target": 3_000_000,
    "range": (0.13, 0.84),
}


def make_weights(g, rng):
    """前 10% 基因携带 70% reads，其余对数正态分 30%（合成形状）。"""
    top_n = g // 10
    w = np.empty(g)
    w[:top_n] = 0.7 / top_n
    rest = np.exp(rng.normal(0.0, 2.0, size=g - top_n))
    w[top_n:] = 0.3 * rest / rest.sum()
    return w


def simulate(w, libs, fold, rng):
    """counts[g, i] ~ Poisson(libs[i] * w[g] * fold[g])。返回整数矩阵。

    fold 只作用于第二组（B 组，后一半样本）；A 组（前一半）恒用 fold=1。"""
    mu = np.outer(w, libs)
    mu[:, libs.shape[0] // 2:] *= fold[:, None]
    return rng.poisson(mu)


def welch_log(counts, libs, normalized):
    """逐基因 Welch t 检验（log2(count+1) 或 log2(CPM+1)），返回 p 值数组。"""
    if normalized:
        x = np.log2(counts / libs * 1e6 + 1.0)
    else:
        x = np.log2(counts + 1.0)
    a, b = x[:, : counts.shape[1] // 2], x[:, counts.shape[1] // 2:]
    na, nb = a.shape[1], b.shape[1]
    ma, mb = a.mean(axis=1), b.mean(axis=1)
    va, vb = a.var(axis=1, ddof=1), b.var(axis=1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (ma - mb) / np.sqrt(va / na + vb / nb)
        df = (va / na + vb / nb) ** 2 / \
            ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    p = 2.0 * stats.t.sf(np.abs(t), df)
    return np.where(np.isfinite(p), p, 1.0)


def strata(mu_full, edges=(-math.inf, 5.0, 50.0, math.inf)):
    """按全深度期望计数分层：低 / 中 / 高。"""
    idx = np.digitize(mu_full, edges[1:-1])
    return [np.where(idx == k)[0] for k in range(len(edges) - 1)]


def summarize(p, q, is_de, labels=("低", "中", "高")):
    """返回 (整体假阳性率, 分层假阳性率列表)；is_de 为真差异基因布尔向量。"""
    null = ~is_de
    fp_overall = float((p[null] < 0.05).mean())
    fp_bh = float((q[null] < 0.05).mean())
    return fp_overall, fp_bh


def main():
    ap = argparse.ArgumentParser(
        description="静默截断 → 文库大小与分组混杂的假差异（合成算例；真实锚点根 CLAUDE.md「--max-time 掐断前缀下载」）")
    ap.add_argument("--genes", type=int, default=4000, help="合成基因数（默认 4000）")
    ap.add_argument("--samples", type=int, default=6, help="每组样本数（默认 6）")
    ap.add_argument("--target-reads", type=int, default=TARGET, help="目标每样本 read 数（默认 3,000,000）")
    ap.add_argument("--de-genes", type=int, default=900, help="功效场景真差异基因数（默认 900）")
    ap.add_argument("--fold", type=float, default=1.5, help="真差异倍数（默认 1.5）")
    ap.add_argument("--seed", type=int, default=SEED, help="随机种子")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    g, ns, target = args.genes, args.samples, args.target_reads
    assert g % 10 == 0 and args.de_genes % 3 == 0

    print("=" * 78)
    print("[Part 0] 真实案例锚点（根 CLAUDE.md 实测记录，非本脚本模拟）")
    print("=" * 78)
    print(f"  m04/m05 前缀下载：{REAL_CASE['files']} 个文件里 {REAL_CASE['truncated']} 个被截断"
          f"（{100 * REAL_CASE['truncated'] / REAL_CASE['files']:.0f}%），"
          f"最少 {REAL_CASE['min_reads']:,}/{REAL_CASE['target']:,} 条（"
          f"{100 * REAL_CASE['min_reads'] / REAL_CASE['target']:.1f}%），"
          f"跨度 {REAL_CASE['range'][0]:.0%}–{REAL_CASE['range'][1]:.0%}；脚本不报错、不校验，rc=0")
    print("  根因：curl --max-time 900 配 1125 MB 前缀，0.5–1 MB/s 下 900 秒传不完即被掐断；"
          "修复：ENA 元数据压缩比取 540 MB 前缀 + --max-time 3600 + 产出 read 数校验")
    print("  → 本课程数据准备中曾出现（教材正文口径，数字以根 CLAUDE.md 为准）")

    print()
    print("=" * 78)
    print(f"[Part 1] 验收演示：{REAL_CASE['files']} 个合成文件、{REAL_CASE['truncated']} 个被截断"
          f"（合成算例，分布对齐真实跨度）")
    print("=" * 78)
    rng = np.random.default_rng(args.seed)
    frac = np.concatenate([rng.uniform(*REAL_CASE["range"], size=REAL_CASE["truncated"]),
                           np.ones(REAL_CASE["files"] - REAL_CASE["truncated"])])
    rng.shuffle(frac)
    actual = np.round(target * frac).astype(int)
    flagged = actual != target
    print(f"  read 数校验（actual == {target:,}）：标记 {flagged.sum()}/{len(actual)} 个文件"
          f"（合成截断文件恰好全部被抓出：{flagged.sum() == REAL_CASE['truncated']}）")
    print(f"  最小实际 read 数：{actual.min():,}（{100 * actual.min() / target:.1f}%，"
          f"合成值；真实记录的最小值 399,491 = 13.3%）")
    print("  对照：不校验直接「完成」→ 退出码 rc=0 —— 完成判据必须是产物计数对得上目标，"
          "不是退出码（根 CLAUDE.md 同节通则）")

    print()
    print("=" * 78)
    print(f"[Part 2a] 假差异（全部零假设）：{g} 基因 × 2 组 × {ns} 样本，"
          f"A 组文库 {target/1e6:.0f} M、B 组截断至 13%–84%（合成算例）")
    print("=" * 78)
    w = make_weights(g, rng)
    mu_full = w * target
    lib_b = target * rng.uniform(*REAL_CASE["range"], size=ns)
    libs = np.concatenate([np.full(ns, target), lib_b])
    counts = simulate(w, libs, np.ones(g), rng)
    strata_idx = strata(mu_full)
    print(f"  B 组文库大小：min {lib_b.min()/1e6:.2f} M / mean {lib_b.mean()/1e6:.2f} M"
          f" / max {lib_b.max()/1e6:.2f} M")
    results = {}
    for mode, normalized in (("不校正 log2(count+1)", False),
                             ("归一 log2(CPM+1)", True)):
        p = welch_log(counts, libs, normalized)
        q = stats.false_discovery_control(p)  # BH，返回值与输入同序
        fp, fp_bh = summarize(p, q, np.zeros(g, dtype=bool))
        by = []
        for si in strata_idx:
            by.append(100 * float((p[si] < 0.05).mean()))
        results[mode] = (fp, fp_bh, by)
        print(f"  {mode:>18}：原始 p<0.05 假阳性率 = {100 * fp:5.1f}%"
              f"（BH 后 {100 * fp_bh:4.1f}%）；分层（低/中/高）原始假阳性率 = "
              f"{by[0]:5.1f}% / {by[1]:5.1f}% / {by[2]:5.1f}%")
    print("  → 不校正：文库大小差被当成组间差异，中/高表达层假阳性冲顶（BH 能把全局单因子压回 0，"
          "但低表达层的偏差以别的形态残留，见 2b）；")
    print("    归一后（2a，截断跨度 13%–84%）整体与各层都回落 ≈5% —— 「图看起来一切正常」"
          "正是这个情形；")
    print()
    print("-" * 78)
    print("[Part 2b] 更深截断（B 组 f ~ U(0.13, 0.45)，仍在真实跨度内）：检出地板伪影显形")
    print("-" * 78)
    lib_b_deep = target * rng.uniform(0.13, 0.45, size=ns)
    libs_deep = np.concatenate([np.full(ns, target), lib_b_deep])
    counts_deep = simulate(w, libs_deep, np.ones(g), rng)
    results_deep = {}
    for mode, normalized in (("不校正 log2(count+1)", False),
                             ("归一 log2(CPM+1)", True)):
        p = welch_log(counts_deep, libs_deep, normalized)
        q = stats.false_discovery_control(p)  # BH，返回值与输入同序
        fp, fp_bh = summarize(p, q, np.zeros(g, dtype=bool))
        by = [100 * float((p[si] < 0.05).mean()) for si in strata_idx]
        results_deep[mode] = (fp, fp_bh, by)
        print(f"  {mode:>18}：原始 p<0.05 假阳性率 = {100 * fp:5.1f}%"
              f"（BH 后 {100 * fp_bh:4.1f}%）；分层（低/中/高）原始假阳性率 = "
              f"{by[0]:5.1f}% / {by[1]:5.1f}% / {by[2]:5.1f}%")
    print("  → 深截断下低表达基因在 B 组近全零，log(CPM+伪计数) 不对称 → 归一分析在低表达层"
          "假阳性仍明显高于 5% —— 归一化修得好全局偏移，修不了检出地板")
    print("    （若截断与基因内容相关——如 GC 偏倚区系统性丢失——归一化同样失效；"
          "本合成取前缀截断 ≈ 对内容随机，已是最仁慈情形）")

    print()
    print("=" * 78)
    print(f"[Part 3] 功效场景：{args.de_genes} 个真差异基因（{args.fold}×，三层各 "
          f"{args.de_genes // 3}），对照「全深度」vs「B 组截断」")
    print("=" * 78)
    de_idx = np.array([], dtype=int)
    for si in strata_idx:
        de_idx = np.concatenate([de_idx, rng.choice(si, args.de_genes // 3, replace=False)])
    is_de = np.zeros(g, dtype=bool)
    is_de[de_idx] = True
    sens = {}
    for scen, lib_b2 in (("全深度", np.full(ns, target)),
                         ("B 组截断", target * rng.uniform(*REAL_CASE["range"], size=ns))):
        libs2 = np.concatenate([np.full(ns, target), lib_b2])
        fold = np.ones(g)
        fold[de_idx] = args.fold
        c2 = simulate(w, libs2, fold, rng)
        p2 = welch_log(c2, libs2, True)
        q2 = stats.false_discovery_control(p2)  # BH，返回值与输入同序
        hit = q2 < 0.05
        by_sens = [100 * float(hit[si][is_de[si]].mean()) for si in strata_idx]
        fp2 = float((p2[~is_de] < 0.05).mean())
        sens[scen] = by_sens
        print(f"  {scen}（B 组 min {lib_b2.min()/1e6:.2f} M）：低/中/高表达层检出率 = "
              f"{by_sens[0]:5.1f}% / {by_sens[1]:5.1f}% / {by_sens[2]:5.1f}%"
              f"（零假设假阳性率 {100 * fp2:4.1f}%，归一分析）")
    print("  → 同一批真差异基因：截断把低表达层的检出率压塌，高表达层几乎不受影响 —— "
          "差异基因列表被系统性偏向高表达基因（失效条件 4「结论完全不可信」的机制侧）")

    if args.selftest:
        print()
        ok = True

        def check(name, cond):
            nonlocal ok
            print(f"  {'PASS' if cond else 'FAIL'}  {name}")
            ok = ok and cond

        # Part 0/1：真实记录一致 + 验收逻辑
        check("真实案例记录自洽：14/29、399,491/3,000,000 = 13.3%",
              REAL_CASE["truncated"] == 14 and REAL_CASE["files"] == 29
              and abs(REAL_CASE["min_reads"] / REAL_CASE["target"] - 0.133) < 0.001)
        check("read 数校验恰好标记全部 14 个截断文件",
              int(flagged.sum()) == REAL_CASE["truncated"])
        check("合成最小 read 数落在真实跨度内（13%–84%）",
              0.10 <= actual.min() / target <= REAL_CASE["range"][1])
        # Part 2a：不校正 → 假阳性爆炸；归一 → 回落 ≈5%（「图看起来一切正常」）
        fp_raw, fp_raw_bh, by_raw = results["不校正 log2(count+1)"]
        fp_nor, fp_nor_bh, by_nor = results["归一 log2(CPM+1)"]
        check("不校正时整体假阳性率 > 50%", fp_raw > 0.5)
        # 分层值 by_* 是百分数（×100），整体 fp_* 是比例——阈值单位须分别对应（CNT-CH13-14）
        check("不校正时高表达层假阳性率 > 80%", by_raw[2] > 80.0)
        check("归一后整体假阳性率 < 不校正的 1/4", fp_nor < fp_raw / 4)
        check("归一后整体假阳性率 ≈ 5%（3%–8%）", 0.03 <= fp_nor <= 0.08)
        # Part 2b：深截断下检出地板伪影显形
        by_nor_deep = results_deep["归一 log2(CPM+1)"][2]
        check("检出地板伪影：深截断归一后低表达层假阳性仍 > 5%",
              by_nor_deep[0] > 5.0)
        # Part 3：截断压塌低表达层检出
        check("截断使低表达层检出率低于全深度场景",
              sens["B 组截断"][0] < sens["全深度"][0])
        check("高表达层检出率对截断稳健（两场景差 < 10 个百分点）",
              abs(sens["B 组截断"][2] - sens["全深度"][2]) < 10.0)
        print("SELFTEST", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch19_host_depletion_tradeoff.py — 去宿主阈值严/松的权衡：同源微生物 read 误伤与
宿主残留此消彼长；以及组间宿主占比偏移对有效微生物通量的污染（合成算例）

服务于：教材第 19 章（宏基因组：物种组成、组装分箱与功能）§19.5 失效条件第 1 条
「去宿主时同源序列误伤微生物读段，过滤过严与过松各有代价」，
对应讲义 m07 §4.1（同源误删陷阱）与 ⑥-6.1（宿主占比组间偏移 → 有效通量偏倚）。

合成设定（不基于任何真实样本；固定种子可复现）：
  - 文库中宿主 read 占比 h（两档：0.70 ≈ 讲义 4.1 的根际/组织样本量级；
    0.05 ≈ 06_data/master/README.md m07 的土壤样本「宿主污染本来就低」）。
  - 每条 read 对宿主参考的「最优比对强度」s ∈ [0,1] 为合成潜变量，三类分布：
    ① 宿主 read：s ~ Beta(14, 2.2)（整体高）；
    ② 保守同源微生物 read（占微生物的 --conserved-frac，默认 0.10 —— 线粒体/
       叶绿体基因骨架、与宿主局部同源的共生菌，讲义 4.1）：s ~ Beta(6, 4)（中段，
       与宿主分布重叠）；
    ③ 典型微生物 read：s ~ Beta(1.8, 8)（整体低）。
  - 过滤规则：s ≥ τ 判为宿主并剔除。τ 低 = 严（对齐奥义上接近
    --very-sensitive：不放过任何可疑命中），τ 高 = 松（默认灵敏度：只有像样的
    全局比对才算数）。Bowtie2 灵敏度预设并不真的是一个标量阈值，本演示的 τ 是
    其合成替身（该映射本身 unverified，只看权衡形态）。

正文引用的输出（手算/解析可对，Beta 分布用 scipy.stats.beta.cdf 精确算）：
  - 严阈值：宿主残留 ↓、但保守同源微生物误伤 ↑（选择性误伤 —— 误伤集中在
    与宿主同源的类群，不是均匀噪声）；松阈值反之（讲义 4.1 的两难）；
  - 土壤档（h = 5%）：两档阈值下整库保留率都应 > 90% —— README m07 判据
    「去宿主后保留率应 > 90%」的合成版；若土壤样本保留率大跌，先怀疑宿主
    参考选错（README 同句），而不是调严参数；
  - 组间偏移（讲义 ⑥-6.1 手算）：A 组宿主占比 85%、B 组 40% → 有效微生物
    通量比 (1−0.85)/(1−0.40) = 0.25，即 4 倍技术鸿沟 —— 不报错，但摧毁丰度比较。

参数：
  --n           蒙特卡洛交叉验证抽样数（默认 400000）
  --conserved-frac  微生物 read 中保守同源类的占比（默认 0.10）
  --seed        随机种子（默认 20261104）

合成数据不得写成真实样本结果；真实样本的宿主占比与同源比例须实测（unverified）。
依赖 numpy + scipy；约 1 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch19_host_depletion_tradeoff.py --selftest
"""
import argparse

import numpy as np
from scipy import stats

TAU_LOOSE = 0.80   # 松 ≈ Bowtie2 默认灵敏度（讲义 ⑤5.1 口径）
TAU_STRICT = 0.63  # 严 ≈ --very-sensitive（03_code 脚本实际使用的口径）
SCENARIOS = [("根际/组织型 h=70%", 0.70), ("土壤型 h=5%（README m07）", 0.05)]

DIST = {
    "host": (14.0, 2.2),
    "conserved": (6.0, 4.0),
    "typical": (1.8, 8.0),
}


def rates(h, tau, conserved_frac):
    """解析求三类 read 的 (残留/误伤) 率：返回 dict。"""
    p_host_survive = stats.beta.cdf(tau, *DIST["host"])          # 宿主残留
    p_cons_killed = 1.0 - stats.beta.cdf(tau, *DIST["conserved"])  # 保守微生物误伤
    p_typ_killed = 1.0 - stats.beta.cdf(tau, *DIST["typical"])     # 典型微生物误伤
    mic_killed = conserved_frac * p_cons_killed + (1 - conserved_frac) * p_typ_killed
    retention = 1.0 - h * (1.0 - p_host_survive) - (1 - h) * mic_killed
    return dict(host_residue=p_host_survive, cons_kill=p_cons_killed,
                typ_kill=p_typ_killed, mic_kill=mic_killed, retention=retention)


def run(n, conserved_frac, seed):
    print(f"合成算例：三类 read 对宿主参考的比对强度 s ~ Beta —— 宿主(14,2.2)、"
          f"保守同源微生物(6,4)、典型微生物(1.8,8)；微生物中保守类占比 "
          f"{conserved_frac}；规则：s ≥ τ 判宿主剔除")
    print(f"阈值两档：松 τ = {TAU_LOOSE}（≈默认灵敏度）／严 τ = {TAU_STRICT}"
          f"（≈--very-sensitive）；蒙特卡洛 n = {n}（seed = {seed}）交叉验证\n")
    header = (f"{'场景':<22} | {'阈值':<10} | {'宿主残留%(原宿主)':>16} | "
              f"{'微生物误伤%(总)':>14} | {'误伤:保守/典型%':>16} | {'整库保留率%':>10}")
    print(header)
    print("-" * len(header))

    out = {}
    rng = np.random.default_rng(seed)
    for name, h in SCENARIOS:
        for preset, tau in (("松", TAU_LOOSE), ("严", TAU_STRICT)):
            a = rates(h, tau, conserved_frac)
            # 蒙特卡洛交叉验证
            draws = {
                "host": rng.beta(*DIST["host"], int(n * h)),
                "cons": rng.beta(*DIST["conserved"], int(n * (1 - h) * conserved_frac)),
                "typ": rng.beta(*DIST["typical"],
                                n - int(n * h) - int(n * (1 - h) * conserved_frac)),
            }
            mc_res = float((draws["host"] < tau).mean())
            mc_kill = (float((draws["cons"] >= tau).mean()) * int(n * (1 - h) * conserved_frac)
                       + float((draws["typ"] >= tau).mean())
                       * (n - int(n * h) - int(n * (1 - h) * conserved_frac))) / (n - int(n * h))
            out[(name, preset)] = dict(**a, mc_res=mc_res, mc_kill=mc_kill, tau=tau, h=h)
            print(f"{name:<22} | {preset}(τ={tau:.2f}) | {100*a['host_residue']:>15.2f}% | "
                  f"{100*a['mic_kill']:>13.2f}% | "
                  f"{100*a['cons_kill']:>7.2f}/{100*a['typ_kill']:>6.3f}% | "
                  f"{100*a['retention']:>9.2f}%")

    print("\n判读：")
    for name, h in SCENARIOS:
        lo = out[(name, "松")]
        st = out[(name, "严")]
        print(f"  {name}：严 vs 松 —— 宿主残留 {100*st['host_residue']:.2f}% vs "
              f"{100*lo['host_residue']:.2f}%（严↓），微生物误伤 {100*st['mic_kill']:.2f}% vs "
              f"{100*lo['mic_kill']:.2f}%（严↑）；误伤高度选择性：严档被杀的微生物里"
              f"保守同源类 {100*st['cons_kill']:.1f}% vs 典型类 {100*st['typ_kill']:.2f}%"
              " —— 被误伤的不是随机噪声，而是与宿主同源的类群（讲义 4.1）")
    print(f"  组间偏移（手算，讲义 ⑥-6.1）：A 组宿主占比 85%、B 组 40% → 有效微生物"
          f"通量比 (1−0.85)/(1−0.40) = {(1-0.85)/(1-0.40):.2f} —— 4 倍技术鸿沟，"
          "不报错，但必须下采样到等通量再比丰度。")
    print("真实数据对照（PRJDB12800 为土壤样本，宿主占比低，README m07 判据「去宿主后"
          "保留率应 > 90%」；本数据实测宿主占比 unverified）。")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n", type=int, default=400000)
    ap.add_argument("--conserved-frac", type=float, default=0.10)
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    r = run(args.n, args.conserved_frac, args.seed)

    if args.selftest:
        checks = []
        for name, _ in SCENARIOS:
            lo = r[(name, "松")]
            st = r[(name, "严")]
            checks += [
                (f"{name} 严宿主残留 < 松（{100*st['host_residue']:.2f}% < "
                 f"{100*lo['host_residue']:.2f}%）",
                 st["host_residue"] < lo["host_residue"]),
                (f"{name} 严微生物误伤 > 松（{100*st['mic_kill']:.2f}% > "
                 f"{100*lo['mic_kill']:.2f}%）",
                 st["mic_kill"] > lo["mic_kill"]),
                (f"{name} 蒙特卡洛贴解析（残留 |Δ|={abs(st['mc_res']-st['host_residue']):.4f}"
                 f"、误伤 |Δ|={abs(st['mc_kill']-st['mic_kill']):.4f}，均 < 0.01）",
                 abs(st["mc_res"] - st["host_residue"]) < 0.01 and
                 abs(st["mc_kill"] - st["mic_kill"]) < 0.01),
            ]
        riz = r[("根际/组织型 h=70%", "严")]
        soil_lo = r[("土壤型 h=5%（README m07）", "松")]
        soil_st = r[("土壤型 h=5%（README m07）", "严")]
        checks += [
            (f"严档误伤高度选择性：保守同源误伤 {100*riz['cons_kill']:.1f}% > 5× 典型 "
             f"{100*riz['typ_kill']:.2f}%（实际比 {riz['cons_kill']/max(riz['typ_kill'],1e-9):.0f}×）",
             riz["cons_kill"] > 5 * riz["typ_kill"]),
            (f"严档微生物误伤有实际量级（h=70% 时 > 1%，实际 {100*riz['mic_kill']:.2f}%）",
             riz["mic_kill"] > 0.01),
            (f"土壤档两档保留率均 > 90%（松 {100*soil_lo['retention']:.1f}%、"
             f"严 {100*soil_st['retention']:.1f}%）—— README m07 判据的合成对照",
             soil_lo["retention"] > 0.90 and soil_st["retention"] > 0.90),
            (f"组间 4× 算术：(1−0.85)/(1−0.40) = {(1-0.85)/(1-0.40):.2f} ≈ 0.25",
             abs((1 - 0.85) / (1 - 0.40) - 0.25) < 1e-9),
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

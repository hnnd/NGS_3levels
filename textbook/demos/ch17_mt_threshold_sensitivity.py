#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch17_mt_threshold_sensitivity.py — percent.mt 阈值敏感性：不同阈值下各细胞类型保留比例的不均匀丢失（合成算例）

服务于：教材第 17 章 §17.5 失效条件第 2 条「照搬人类 PBMC 的 percent.mt 阈值到植物或其他
组织」，对应讲义 p02 §4.3 / §6.2 首行（percent.mt 全为 0 的静默错误）与
../06_data/phd/README.md p02 节「植物没有线粒体比例这个通用指标，叶绿体基因才是」。

合成设定：
  - 3 个虚拟细胞类型，各自有不同的线粒体转录本占比本底（percent.mt，对数正态分布）：
      mesophyll 型（叶肉样）   中位 ≈ 3% —— 与人类 PBMC 教程阈值兼容；
      vascular  型（维管束样） 中位 ≈ 6% —— 在 5% 阈值下已开始被误杀；
      guard     型（保卫细胞样）中位 ≈ 14% —— 讲义 §4.3：天生富集线粒体的细胞，
                                     机械执行 percent.mt < 5% 会被「彻底抹杀」。
    （「中位」指分布的几何中心，分布本身有细胞间生物学波动 σ_within。）
  - 依次施加阈值 t ∈ {3, 5, 8, 10, 15, 20, 25}%，报告每个细胞类型的保留比例。
  - 同时生成叶绿体占比 percent.cp（植物数据必查的另一列；叶肉型叶绿体转录本高），
    提醒 percent.cp 与 percent.mt 是两条独立的过滤维度（讲义 §4.3 第一点）。

正文引用的输出：
  - 「阈值 × 细胞类型」保留比例矩阵：展示不均匀丢失 —— 阈值 5% 时 guard 型
    保留比例塌缩到接近 0，而 mesophyll 型几乎无损；
  - 阈值从「人类经验值 5%」放宽到数据驱动分位数的必要性（讲义 §4.3 末段）。

参数：
  --cells        每个细胞类型的合成细胞数（默认 4000）
  --thresholds   逗号分隔的 percent.mt 阈值列表（%）（默认 3,5,8,10,15,20,25）
  --seed         随机种子（默认 20261104）

合成数据不得写成真实样本结果；真实数据的阈值须按该文库的经验分布划定（讲义 §4.3）。
只依赖 numpy；约 1 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch17_mt_threshold_sensitivity.py --selftest
"""
import argparse

import numpy as np

# (名称, mt 中位 %, mt 细胞间 σ, cp 中位 %, cp σ) —— 虚拟类型，非任何真实样本
TYPES = (
    ("mesophyll（叶肉样，mt 本底低）", 3.0, 0.35, 28.0, 0.30),
    ("vascular（维管束样，mt 本底中）", 6.0, 0.35, 12.0, 0.35),
    ("guard（保卫细胞样，mt 本底高）", 14.0, 0.35, 6.0, 0.40),
)


def simulate(cells_per_type, seed):
    """返回 {类型名: (percent_mt, percent_cp)}，percent 为单位向量（非分数）。"""
    rng = np.random.default_rng(seed)
    out = {}
    for name, mt_med, mt_sig, cp_med, cp_sig in TYPES:
        mt = np.exp(rng.normal(np.log(mt_med), mt_sig, cells_per_type))
        cp = np.exp(rng.normal(np.log(cp_med), cp_sig, cells_per_type))
        out[name] = (mt, cp)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--cells", type=int, default=4000)
    ap.add_argument("--thresholds", default="3,5,8,10,15,20,25")
    ap.add_argument("--seed", type=int, default=20261104)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    thresholds = [float(x) for x in args.thresholds.split(",")]
    data = simulate(args.cells, args.seed)

    print("合成算例：3 个虚拟细胞类型的 percent.mt 本底不同（对数正态，几何中位见首列）")
    print(f"每类型 {args.cells} 个细胞；seed = {args.seed}\n")
    header = f"{'细胞类型（mt 几何中位）':<26}" + "".join(f" | t={t:<4.0f}%" for t in thresholds)
    print(header)
    print("-" * len(header))
    retention = {}
    for name, (mt, _) in data.items():
        row = f"{name:<26}"
        for t in thresholds:
            r = float((mt < t).mean())
            retention[(name, t)] = r
            row += f" | {r:>7.3f}"
        print(row)

    guard = [n for n, *_ in TYPES if n.startswith("guard")][0]
    mes = [n for n, *_ in TYPES if n.startswith("mesophyll")][0]
    r5_guard = retention[(guard, 5.0)]
    r5_mes = retention[(mes, 5.0)]
    print(f"\n判读：人类 PBMC 经验阈值 t = 5% 下，{guard} 保留 {r5_guard:.1%}，"
          f"{mes} 保留 {r5_mes:.1%} —— 同一阈值对不同细胞类型的杀伤相差约 "
          f"{r5_mes / max(r5_guard, 1e-9):.0f} 倍，丢失是系统性的、不均匀的。")
    print("这就是讲义 §4.3 说的「机械执行 5% 阈值会把活性最旺盛的目标细胞彻底抹杀」的定量版。")
    print("对照提醒：植物数据还须单独检查叶绿体占比 percent.cp（合成算例中叶肉型 cp 中位 28%）；")
    print("阈值一律按【当前文库】的经验分布定（分位数截断），见 02_seurat_pipeline.R 第 3 步（默认 95% 分位）。")

    if args.selftest:
        checks = [
            (f"t=5% 时 guard 型保留 < 30%（实际 {r5_guard:.3f}）", r5_guard < 0.30),
            (f"t=5% 时 mesophyll 型保留 > 90%（实际 {r5_mes:.3f}）", r5_mes > 0.90),
            ("每个类型的保留比例随阈值单调不减",
             all(retention[(n, a)] <= retention[(n, b)] + 1e-9
                 for n, *_ in TYPES for a, b in zip(thresholds, thresholds[1:]))),
            ("t=25% 时全体保留 > 80%（分布未被阈值摧毁）",
             all(retention[(n, 25.0)] > 0.80 for n, *_ in TYPES)),
            ("不均匀丢失成立：t=5% 下两类型保留差 > 3 倍",
             r5_mes / max(r5_guard, 1e-9) > 3.0),
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch25_dual_axis_illusion.py — 双 Y 轴伪相关：自由缩放 + 择优呈现能「制造」多高的假相关（合成算例）

服务于：教材第 25 章（课题设计与图表叙事）§25.4 图表叙事·单图层面，
对应讲义 p08 §4.3 反模式 2（双 Y 轴共绘图：左右轴的缩放与平移纯属人为任意，
可调节轴范围恶意制造两条曲线「高度吻合」的伪相关幻觉）与 §4.5 审稿人点 6
（视觉欺诈式坐标轴修饰、选择性呈现）。

合成设定：
  - 两条独立的随机游走（长度 T，增量 iid N(0,1)，互相独立 ⇒ 真实耦合强度
    用一阶差分相关 |r_inc| 度量，期望 ≈ 0）；
  - 双 Y 轴的两个自由参数（缩放 + 平移）≡ 对右轴序列做一次线性变换，
    最佳贴合的相关恰好就是两条序列水平的 Pearson |r| —— 即经典的
    「趋势序列伪回归」（spurious regression of integrated series）：
    随机游走的水平相关可以很高，而增量完全不相关；
  - 择优呈现：作者从 --group 对候选序列里挑「最像」的一对画进论文
    （max |r|），量化选择性呈现如何把偶发的伪相关变成正文主图。

正文引用的输出：
  - 真实（一阶差分）|r_inc| 中位数 ≈ 0 vs 双轴自由拟合 |r_vis| 中位数与尾部
    P(|r_vis| > 0.8 / 0.9)——两条独立曲线被画成「高度吻合」的概率有多大；
  - 择优呈现（best-of-5）把 P(>0.8) 放大多少倍；
  - 修复对照：共享横轴拆上下 panel、各自锁定零基线轴后，读者应报告的
    相关就是 |r_inc| ≈ 0，幻觉消失。

参数：
  --length   每条序列长度（默认 60，约等于一篇论文时间序列图的长度）
  --pairs    模拟序列对数（默认 2000，须为 --group 的整数倍）
  --group    择优呈现的候选池大小（默认 5，「试画几组挑最像的」）
  --seed     随机种子（默认 20261105）

合成数据不得写成真实样本结果。只依赖 numpy + scipy；约 0.2 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch25_dual_axis_illusion.py --selftest
"""
import argparse

import numpy as np


def simulate(length, pairs, seed):
    """返回（增量矩阵 A/B，形状 (pairs, length)）。增量 iid N(0,1)、互相独立。"""
    rng = np.random.default_rng(seed)
    inc_a = rng.normal(0.0, 1.0, (pairs, length))
    inc_b = rng.normal(0.0, 1.0, (pairs, length))
    return inc_a, inc_b


def row_corr(x, y):
    """逐行 Pearson 相关（x、y 形状相同），全 0 安全（本演示无此情形）。"""
    xz = (x - x.mean(axis=1, keepdims=True)) / x.std(axis=1, ddof=1, keepdims=True)
    yz = (y - y.mean(axis=1, keepdims=True)) / y.std(axis=1, ddof=1, keepdims=True)
    return (xz * yz).mean(axis=1)


def run(length, pairs, group, seed):
    inc_a, inc_b = simulate(length, pairs, seed)
    walk_a, walk_b = np.cumsum(inc_a, axis=1), np.cumsum(inc_b, axis=1)
    r_vis = np.abs(row_corr(walk_a, walk_b))       # 双轴自由拟合 = 水平相关
    r_inc = np.abs(row_corr(inc_a, inc_b))         # 真实耦合 = 增量相关
    best = r_vis.reshape(-1, group).max(axis=1)    # 择优呈现：候选池里挑最像的
    print("合成算例：两条独立随机游走（增量 iid 且互相独立，真实耦合 ≈ 0）")
    print(f"T = {length}；序列对 {pairs}（择优候选池 {group}）；seed = {seed}\n")
    print(f"{'指标':<28} | {'中位数':>8} | {'P(>0.8)':>9} | {'P(>0.9)':>9}")
    print("-" * 62)
    for name, arr in [("真实耦合 |r_inc|（一阶差分）", r_inc),
                      ("双轴自由拟合 |r_vis|（每对一次）", r_vis),
                      ("择优呈现（best-of-5 取 max）", best)]:
        print(f"{name:<28} | {np.median(arr):>8.3f} | {(arr > 0.8).mean():>9.3f} "
              f"| {(arr > 0.9).mean():>9.3f}")
    return r_vis, r_inc, best


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--length", type=int, default=60)
    ap.add_argument("--pairs", type=int, default=2000)
    ap.add_argument("--group", type=int, default=5,
                    help="择优呈现候选池大小（--pairs 须为其整数倍）")
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    if args.pairs % args.group != 0:
        raise SystemExit("--pairs 必须是 --group 的整数倍")
    r_vis, r_inc, best = run(args.length, args.pairs, args.group, args.seed)
    p8_single = float((r_vis > 0.8).mean())
    p8_best = float((best > 0.8).mean())
    print("\n判读：双 Y 轴给作者两个自由参数，水平相关的分布尾巴被当成「拟合」呈现；"
          "再从候选池挑一对就又把概率翻数倍。修复：共享横轴拆上下 panel、"
          "锁定零基线轴，图内能支持的相关上限回到真实 |r_inc|。")

    if args.selftest:
        checks = [
            (f"真实耦合中位数 < 0.15（实际 {np.median(r_inc):.3f}）",
             float(np.median(r_inc)) < 0.15),
            (f"双轴自由拟合中位数 > 2× 真实耦合（实际 "
             f"{np.median(r_vis):.3f} vs {np.median(r_inc):.3f}）",
             float(np.median(r_vis)) > 2 * float(np.median(r_inc))),
            ("存在可呈现实例：max |r_vis| > 0.9（独立序列也能画出「高度吻合」）",
             float(r_vis.max()) > 0.9),
            (f"择优呈现 P(>0.8) > 2× 单次 P(>0.8)（实际 {p8_best:.3f} vs {p8_single:.3f}）",
             p8_best > 2 * p8_single),
        ]
        print("\n[selftest]")
        npass = sum(pass_ for _, pass_ in checks)
        for name, passed in checks:
            print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        print(f"{npass}/{len(checks)} PASS")
        if npass != len(checks):
            raise SystemExit(1)


if __name__ == "__main__":
    main()

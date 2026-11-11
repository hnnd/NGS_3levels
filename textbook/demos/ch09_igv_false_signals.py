#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合成演示：IGV 人工核查的三类假变异信号计数（教材第 9 章概念与方法节复现入口）。

服务于第 9 章「IGV 中三类需要复核的变异线索」一段
（对应讲义 u07 §4.4 与习题 5）。对单个合成位点的读段 pileup 计数三个量：

  ① 链偏（strand bias）：支持变异（alt）的读段中正链占比——真实变异应在
     正反链支持明显失衡是需要复核的线索（扩增/测序系统误差是候选解释之一，
     非唯一解释），不是真伪判据；
  ② 重复区（MAPQ=0）：支持 alt 的读段中 MAPQ=0 占比——MAPQ=0 表示多重比对，
     同源区塌缩会把不同拷贝的读段叠到同一坐标；
  ③ 末端伪影（end bias）：变异位点落在读段末端 --end-window bp 以内的
     alt 读段占比——错配集中在读段末端提示接头残留、末端质量下降或局部比对
     错位等候选解释，需补充证据。

四个固定种子场景：real（按合成规则生成的『无偏』位点，非真变异判据）/ strand（链偏）/ mapq0（多重比对）/
endbias（末端聚集）。本章只数计数、不下统计结论（链偏的显著性检验等
统计判据归第 10 章，见教材分层约定）。

【合成规则】下方 judge() 的三道阈值（正链占比 0.2–0.8、MAPQ=0 占比 >0.5、
末端窗口占比 >0.5）是为演示设定的场景规则，没有外部生物学判据，不得当作
IGV 或任何工具的标准阈值引用。

【合成算例】读段由固定种子合成，不代表任何真实样本的比对结果，
正文引用时必须说「合成算例」。

参数：
  --n-reads      覆盖该位点的读段总数（默认 45，对应讲义习题 5 的 45×）
  --n-alt        支持变异的读段数（默认 15，对应习题 5 的 15 条）
  --read-length  合成读段长度（bp，默认 150）
  --end-window   末端窗口（bp，默认 10，对应讲义「5–10 bp」上限）
  --seed         随机种子（默认 20261104）
  --scenario     只跑一个场景：real|strand|mapq0|endbias（默认 all）

正文引用的输出：四场景的三组计数（alt 正链占比 / alt 中 MAPQ=0 占比 /
alt 中末端窗口占比）与判读行。

运行：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch09_igv_false_signals.py --selftest
"""

import argparse
import random
import sys


def simulate(scenario, n_reads, n_alt, read_length, end_window, seed):
    """合成一个位点的读段 pileup，返回 read 字典列表。

    每条读段：strand '+'/'-'、mapq（0 或 60）、alt（是否支持变异）、
    pos（变异位点在读段内的 0-based 偏移，取较近一端的距离做末端计数）。
    """
    rng = random.Random(seed)
    reads = []
    for i in range(n_reads):
        alt = i < n_alt
        strand = "+" if rng.random() < 0.5 else "-"
        if scenario == "strand" and alt:
            strand = "+"  # 链偏场景：alt 读段全部压在正链（合成）
        mapq = 60
        if scenario == "mapq0":
            mapq = 0  # 重复区场景：所有读段多重比对（合成）
        if scenario == "endbias" and alt:
            # 末端伪影场景：alt 只出现在读段末端窗口内（合成）
            pos = rng.randrange(end_window)
            if rng.random() < 0.5:
                pos = read_length - 1 - pos
        else:
            pos = rng.randrange(read_length)
        reads.append({"strand": strand, "mapq": mapq, "alt": alt, "pos": pos})
    return reads


def counters(reads, read_length, end_window):
    """三道闸的计数：alt 正链占比、alt 中 MAPQ=0 占比、alt 中末端窗口占比。"""
    alt = [r for r in reads if r["alt"]]
    n_alt = len(alt)
    alt_fwd = sum(1 for r in alt if r["strand"] == "+") / n_alt
    mapq0_alt = sum(1 for r in alt if r["mapq"] == 0) / n_alt
    near_alt = sum(1 for r in alt
                   if min(r["pos"], read_length - 1 - r["pos"]) < end_window) / n_alt
    return alt_fwd, mapq0_alt, near_alt


def judge(name, alt_fwd, mapq0_alt, near_alt):
    flags = []
    if not (0.2 <= alt_fwd <= 0.8):
        flags.append("链偏线索（合成规则 0.2–0.8）：alt 正链占比 %.0f%%" % (100 * alt_fwd))
    if mapq0_alt > 0.5:
        flags.append("重复区线索（合成规则 >0.5）：alt 中 MAPQ=0 占比 %.0f%%" % (100 * mapq0_alt))
    if near_alt > 0.5:
        flags.append("末端线索（合成规则 >0.5）：alt 中 %.0f%% 变异位点落在读段末端窗口" % (100 * near_alt))
    if flags:
        return "  → " + "；".join(flags)
    return "  → 三条合成规则均未触发（仅示意，不证明为真变异；统计判定归第 10 章）"


SCENARIOS = ("real", "strand", "mapq0", "endbias")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="合成算例：IGV 三类假变异信号的 pileup 计数（教材第 9 章）")
    ap.add_argument("--n-reads", type=int, default=45, help="覆盖位点的读段总数")
    ap.add_argument("--n-alt", type=int, default=15, help="支持变异的读段数")
    ap.add_argument("--read-length", type=int, default=150, help="合成读段长度（bp）")
    ap.add_argument("--end-window", type=int, default=10, help="末端窗口（bp）")
    ap.add_argument("--seed", type=int, default=20261104, help="随机种子")
    ap.add_argument("--scenario", choices=list(SCENARIOS), default=None,
                    help="只跑一个场景（默认 all）")
    ap.add_argument("--selftest", action="store_true", help="断言正文引用的关键输出")
    args = ap.parse_args(argv)

    if args.n_alt > args.n_reads:
        print("[ERROR] --n-alt 不能大于 --n-reads", file=sys.stderr)
        return 2

    names = [args.scenario] if args.scenario else list(SCENARIOS)
    print("=== 合成算例：三类假变异信号的 pileup 计数（固定种子 %d；%d× 覆盖，%d 条 alt，读段 %d bp，末端窗口 %d bp）==="
          % (args.seed, args.n_reads, args.n_alt, args.read_length, args.end_window))
    results = {}
    for name in names:
        reads = simulate(name, args.n_reads, args.n_alt,
                         args.read_length, args.end_window, args.seed)
        alt_fwd, mapq0_alt, near_alt = counters(reads, args.read_length, args.end_window)
        results[name] = (alt_fwd, mapq0_alt, near_alt)
        print("[%s] alt 正链占比 %.2f ｜ alt 中 MAPQ=0 占比 %.2f ｜ alt 中末端窗口占比 %.2f"
              % (name, alt_fwd, mapq0_alt, near_alt))
        print(judge(name, alt_fwd, mapq0_alt, near_alt))

    if args.selftest:
        assert set(results) == set(SCENARIOS), "--selftest 需跑全部四个场景"
        alt_fwd, mapq0_alt, near_alt = results["real"]
        assert mapq0_alt == 0.0
        assert 0.25 <= alt_fwd <= 0.75
        assert near_alt <= 0.4
        alt_fwd, mapq0_alt, near_alt = results["strand"]
        assert alt_fwd == 1.0, "链偏场景 alt 应全部在正链"
        alt_fwd, mapq0_alt, near_alt = results["mapq0"]
        assert mapq0_alt == 1.0, "重复区场景 alt 应全部 MAPQ=0"
        alt_fwd, mapq0_alt, near_alt = results["endbias"]
        assert near_alt == 1.0, "末端伪影场景 alt 应全部落在末端窗口"
        print("SELFTEST PASS：real 三项计数在阈值内，strand/mapq0/endbias 三场景计数符合设计")

    return 0


if __name__ == "__main__":
    sys.exit(main())

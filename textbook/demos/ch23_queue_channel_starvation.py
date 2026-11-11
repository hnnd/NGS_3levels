#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch23_queue_channel_starvation.py — Queue Channel 单次消费被并发争抢的静默截断：
样本竞争参考索引的 race 模拟（合成算例）

服务于：教材第 23 章 §23.4 概念与方法（Queue vs Value Channel 的状态机
行为）、§23.5 失效条件第 4 条（-resume 缓存条目之后的「数据流静默错误」
家族），对应讲义 p07 ②-学习目标 2（通道误用的静默悬空与数据饥饿）、
④-4.2（queue 每个元素只能被下游单次消费；误传多个分支 → 率先就绪的分支
夺取，其余饥饿）、⑤-步骤 2（stub-run 期望 completed=10，「若出现
completed=7 或 4，说明发生了通道单次消费截断」）、⑥-3 判据 1（样本数量
非预期截断但终态标为 SUCCESS）。

合成设定（不基于任何真实样本；固定种子可复现）：
  4 个样本的 FASTP 输出 + 1 份 salmon 索引，汇入 SALMON_QUANT。
  场景 Q（误用）：索引走 Queue Channel（仅 1 个元素）。4 个 quant 任务
    并发就绪时间 ~ U(0,1)，先到先得——1 个样本夺走索引，其余 3 个永远
    等不到输入；流程不报错，终态 SUCCESS，只产出 1 份 quant.sf。
    200 次模拟：统计饥饿发生率、幸存样本的随机性（不同种子的幸存者可
    以是任意一个样本 → 结果不可复现）。
  场景 V（正确）：索引走 Value Channel（取之不尽）→ 200/200 次全部
    4 份 quant.sf，无饥饿。
  附带讲义 ⑤-步骤 2 的任务计数算术：正确接线 completed=10
    （4 FASTP + 1 INDEX + 4 QUANT + 1 MERGE）；索引误接 queue 后
    SALMON_QUANT 只派生 1 个任务 → completed=7。

正文引用的输出（手算可对）：
  - queue 误用：饥饿运行比例 = 100%（每次都只剩 1/4 个样本）；
  - 幸存样本在 4 个样本间随机漂移（200 次模拟集齐 4 个幸存者）；
  - value 通道：饥饿 = 0（200/200 全产出）；
  - 任务计数 10 vs 7 的判读（讲义 stub-run 验收数字的机器形态）。

参数：
  --n-samples   样本数（默认 4，与配套流程一致）
  --n-runs      模拟运行次数（默认 200）
  --seed        随机种子（默认 20261105）

合成数据不得写成真实样本结果。只依赖 numpy；< 1 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch23_queue_channel_starvation.py --selftest
"""
import argparse

import numpy as np


def run_once(rng: np.random.Generator, n_samples: int, value_channel: bool):
    """模拟一轮 SALMON_QUANT 派生：返回 (幸存样本下标列表, 饥饿样本下标列表)。

    queue channel：索引是 1 个元素，被就绪时间最早的样本夺走；
    value channel：每个样本都拿得到索引。"""
    ready = rng.uniform(0.0, 1.0, size=n_samples)   # 各任务的就绪时间
    if value_channel:
        return list(range(n_samples)), []
    winner = int(np.argmin(ready))                  # 先到先得，仅 1 个幸存
    return [winner], [i for i in range(n_samples) if i != winner]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n-samples", type=int, default=4)
    ap.add_argument("--n-runs", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    print("合成算例（不基于任何真实样本）；模拟 SALMON_QUANT 并发消费索引通道的 race")
    print()

    winners_q, starved_q_runs = set(), 0
    for _ in range(args.n_runs):
        won, starved = run_once(rng, args.n_samples, value_channel=False)
        winners_q.update(won)
        if starved:
            starved_q_runs += 1
    starv_frac = starved_q_runs / args.n_runs

    starved_v_runs = 0
    quant_counts_v = []
    for _ in range(args.n_runs):
        won, starved = run_once(rng, args.n_samples, value_channel=True)
        quant_counts_v.append(len(won))
        if starved:
            starved_v_runs += 1

    print(f"场景 Q（索引误走 Queue Channel，{args.n_runs} 次模拟，种子 {args.seed}）：")
    print(f"  发生样本饥饿的运行：{starved_q_runs}/{args.n_runs}（{starv_frac:.0%}）")
    print(f"  每次运行产出 quant.sf：1/{args.n_samples} 份（流程终态 SUCCESS、不报错）")
    print(f"  200 次模拟集齐的幸存样本数：{len(winners_q)}/{args.n_samples}"
          f" → 幸存者是随机的，重跑结果不可复现")
    print(f"场景 V（索引走 Value Channel，{args.n_runs} 次模拟）：")
    print(f"  发生样本饥饿的运行：{starved_v_runs}/{args.n_runs}")
    print(f"  每次运行产出 quant.sf：{min(quant_counts_v)}–{max(quant_counts_v)} 份"
          f"（本模拟全为 {args.n_samples} 份）")
    print()
    n_fastp = args.n_samples
    ok_total = n_fastp + 1 + n_fastp + 1          # FASTP+INDEX+QUANT+MERGE
    bad_total = n_fastp + 1 + 1 + 1               # QUANT 只派生 1 个任务
    print("讲义 p07 ⑤-步骤 2 的 stub-run 任务计数算术（本流程的验收数字）：")
    print(f"  正确接线：{n_fastp} FASTP + 1 INDEX + {n_fastp} QUANT + 1 MERGE"
          f" = completed {ok_total}（另含 rule all 的伪节点不计）")
    print(f"  索引误接 queue：SALMON_QUANT 只派生 1 个任务 → completed {bad_total}"
          f"（讲义：『若出现 completed=7 或 4，说明发生了通道单次消费截断』）")

    if args.selftest:
        checks = [
            (f"queue 误用饥饿率 =100%（实际 {starv_frac:.0%}）", starv_frac == 1.0),
            (f"幸存样本集齐 {args.n_samples} 个（随机漂移）",
             len(winners_q) == args.n_samples),
            (f"value 通道饥饿 =0（实际 {starved_v_runs}）", starved_v_runs == 0),
            (f"value 通道每次产出 {args.n_samples} 份",
             min(quant_counts_v) == args.n_samples == max(quant_counts_v)),
            (f"正确接线任务计数 ={ok_total}（=10）", ok_total == 10),
            (f"误接后任务计数 ={bad_total}（=7）", bad_total == 7),
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

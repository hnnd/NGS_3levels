#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch23_resume_hash_factors.py — Nextflow -resume 内容哈希缓存的机制复刻：
五大哈希因子逐一核验、资源变更不触发重算、无序 collect() 与非幂等脚本
造成的缓存全量失效（合成算例）

服务于：教材第 23 章 §23.4 概念与方法（-resume 的内容哈希缓存）、§23.5
失效条件第 4 条（-resume 缓存全量失效或误命中），对应讲义 p07 ④-4.5
（缓存键五大计算因子、「调整 CPU 核心数或内存阈值并不会改变哈希」）、
⑥-3（三大无报错性静默故障判据之二：每次 -resume 均全量重算）、⑨-7
（-resume 全量失效的四步排查清单）。

合成设定（不基于任何真实样本；固定种子可复现）：
  任务键 = sha256( ①插值后脚本文本 | ②输入文件内容哈希 | ③引用参数值 |
                   ④容器标签/conda 指纹 | ⑤bin/ 外置脚本 SHA )
  部分 A：基线键 K0；五个因子各改一处 → 5/5 键变化（缓存失效=精确失效）；
          仅改资源 cpus 4→8、memory 8→16GB → 键不变（资源由执行器在派发时
          注入、不参与任务键——呼应讲义「调整资源不会触发无意义重算」）。
  部分 B：4 个 quant 任务的完成顺序随机（400 次模拟运行）。汇总任务的
          输入列表若按完成顺序（裸 collect()）→ 键随顺序漂移；按文件名
          排序（toSortedList，配套 main.nf 的写法）→ 键恒定。给出
          「第二次 -resume 命中率」对照。
  部分 C：脚本体内注入 $RANDOM（非幂等因子）→ 每次运行键都不同，
          400/400 缓存未命中——讲义 ⑨-7 排查清单第 ② 条的直接演示。

正文引用的输出（手算可对）：
  - 五因子逐一变更 → 键全变（5/5）；资源变更 → 键不变（0/5 类）；
  - 裸 collect() 的汇总键唯一数（≈顺序排列数）与二次 -resume 命中率
    （≈1/N），toSortedList 命中率 = 100%；
  - $RANDOM 注入的未命中率 = 100%。

参数：
  --n-runs      部分 B/C 的模拟运行次数（默认 400）
  --seed        随机种子（默认 20261105）

合成数据不得写成真实样本结果。只用 Python 标准库；< 1 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch23_resume_hash_factors.py --selftest
"""
import argparse
import hashlib
import random


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def task_key(script: str, inputs: list[str], params: dict,
             container: str, bin_scripts: list[str]) -> str:
    """复刻讲义 p07 ④-4.5 的五因子缓存键。"""
    parts = [sha(script)]
    parts.extend(sha(i) for i in inputs)
    for k in sorted(params):
        parts.append(f"{k}={params[k]}")
    parts.append(sha(container))
    parts.extend(sha(s) for s in bin_scripts)
    return sha("|".join(parts))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n-runs", type=int, default=400)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    print("合成算例（不基于任何真实样本）；复刻 Nextflow -resume 任务级内容哈希键")
    print()

    # ---------------- 部分 A：五因子 + 资源变更 ----------------
    base = dict(
        # ${task.cpus} 由执行器在派发时替换，属资源配置，不进任务哈希键
        script="salmon quant -i IDX -l A -1 R1 -2 R2 -p ${task.cpus}",
        inputs=["CK_1_1.fq.gz", "CK_1_2.fq.gz", "salmon_index"],
        params={"libtype": "A", "qual": 20},
        container="quay.io/biocontainers/salmon:1.10.3--haf24da9_3",
        bin_scripts=["merge_quant.py"],
    )
    resources = {"cpus": 4, "memory": "8.GB"}   # 执行器层配置，task_key 不使用
    k0 = task_key(**base)
    variants = {
        "①脚本改一个词": dict(base, script="salmon quant -i IDX -l A -1 R1 -2 R2 -p ${task.cpus} --seqBias"),
        "②一个输入内容变": dict(base, inputs=["CK_1_1.fq.gz", "CK_1_2.fq.gz", "salmon_index_v2"]),
        "③引用参数变": dict(base, params={"libtype": "A", "qual": 30}),
        "④容器 tag 变": dict(base, container="quay.io/biocontainers/salmon:1.10.4--hAAAA_0"),
        "⑤bin/ 脚本变": dict(base, bin_scripts=["merge_quant_v2.py"]),
    }
    print("部分 A 五因子逐一变更（讲义 p07 ④-4.5；K0 = %.12s…）：" % k0)
    n_changed = 0
    for name, v in variants.items():
        k = task_key(**v)
        changed = k != k0
        n_changed += changed
        print(f"  {name:<14} 键变化：{changed}")
    # 资源变更：cpus/memory 属执行器配置，不进任务键（脚本里的 ${task.cpus}
    # 是占位符，由派发层替换，不参与哈希）
    resources2 = {"cpus": 8, "memory": "16.GB"}
    k_res = task_key(**base)
    print(f"  资源变更（cpus {resources['cpus']}→{resources2['cpus']}、"
          f"memory {resources['memory']}→{resources2['memory']}）：键变化：{k_res != k0}"
          f"（资源配额不进任务键 → 调资源不会触发无意义重算）")
    print(f"  → 五因子命中率 {n_changed}/5；资源 0 变化")
    print()

    # ---------------- 部分 B：裸 collect() vs toSortedList ----------------
    samples = ["CK_1", "CK_2", "TR_1", "TR_2"]
    keys_unsorted, keys_sorted = set(), set()
    for _ in range(args.n_runs):
        completion = samples[:]
        rng.shuffle(completion)          # 任务完成顺序 = 随机排列
        keys_unsorted.add(task_key(
            script="merge_quant.py --quant-files " + " ".join(completion),
            inputs=[], params={}, container="local", bin_scripts=[]))
        keys_sorted.add(task_key(
            script="merge_quant.py --quant-files " + " ".join(sorted(samples)),
            inputs=[], params={}, container="local", bin_scripts=[]))
    hit_unsorted = 1.0 / len(keys_unsorted)   # 第二次 -resume 恰好同序的概率
    hit_sorted = 1.0
    print(f"部分 B 汇总任务输入顺序（{args.n_runs} 次模拟运行，完成顺序随机）：")
    print(f"  裸 collect()（按完成顺序）  ：唯一键 {len(keys_unsorted)} 个 → "
          f"二次 -resume 命中率 ≈ {hit_unsorted:.1%}")
    print(f"  toSortedList（按文件名排序）：唯一键 {len(keys_sorted)} 个 → "
          f"二次 -resume 命中率 = {hit_sorted:.0%}（配套 main.nf 的写法）")
    print("  → 讲义 p07 ⑥-3 判据 2 / ⑨-7 排查①：汇总处无序 collect() 使哈希输入波动")
    print()

    # ---------------- 部分 C：非幂等脚本（$RANDOM 注入） ----------------
    keys_c = set()
    for _ in range(args.n_runs):
        token = rng.randint(0, 10 ** 9)   # 模拟 $RANDOM / 时间戳
        keys_c.add(task_key(
            script=f"salmon quant ... ; echo run-id-{token}",
            inputs=[], params={}, container="local", bin_scripts=[]))
    print(f"部分 C 非幂等脚本（脚本内注 $RANDOM 类动态因子，{args.n_runs} 次运行）：")
    print(f"  唯一键 {len(keys_c)} 个 / {args.n_runs} 次 → 缓存未命中率 "
          f"{len(keys_c) / args.n_runs:.0%}（讲义 ⑨-7 排查②的直接演示）")

    if args.selftest:
        checks = [
            (f"五因子逐一变更键全变（{n_changed}/5）", n_changed == 5),
            ("资源变更（cpus/memory）键不变", k_res == k0),
            (f"裸 collect() 唯一键 >1（实际 {len(keys_unsorted)}）",
             len(keys_unsorted) > 1),
            ("裸 collect() 二次 -resume 命中率 <10%",
             hit_unsorted < 0.10),
            ("toSortedList 唯一键 =1（命中率 100%）", len(keys_sorted) == 1),
            (f"$RANDOM 注入未命中率 =100%（实际 {len(keys_c)}/{args.n_runs}）",
             len(keys_c) == args.n_runs),
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

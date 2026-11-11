#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ch23_stale_output_mtime.py — 「改了参数但输出已存在，下游不重建」的两种调度
语义对照：Snakemake 式 mtime 调度（参数变化不可见 → 结果陈旧而不报错）
vs Nextflow 式内容哈希调度（参数参与任务键 → 精准级联重跑）（合成算例）

服务于：教材第 23 章 §23.4 概念与方法（增量计算与缓存判据）、§23.5
失效条件第 2 条（改了参数但输出已存在，下游不重建——结果陈旧而不报错）、
第 4 条（-resume 缓存的误命中面），对应讲义 m08 ⑥（「改了阈值不会自动
重跑」表）、⑨-6（salmon k-mer 改小后索引不重建）、⑩-5（习题：config
阈值 0.05→0.01 而 -n 说 Nothing to be done），以及 p07 ③（mtime 作为
拓扑刷新判据「状态脆弱易失」vs SHA 内容哈希缓存）。

合成设定（不基于任何真实样本；固定种子可复现）：
  一条三步玩具流程（复刻 m08 Snakefile 的结构）：
    filter   : raw_counts.tsv --(参数 qual)--> filtered.tsv（阈值置零，类比 fastp）
    index    : transcripts.txt --> index.txt（只依赖转录组名单、无参数，
               类比 salmon index——参数变了它也该命中缓存）
    summary  : filtered.tsv + index.txt --(参数 qual)--> summary.tsv
               （类比 merge_counts + 报告，文件内记录本次所用的 qual）
  调度器 A（Snakemake 式）：输出缺失或输入 mtime > 输出 mtime 才重跑；
    参数只出现在命令行里，不参与判据。
  调度器 B（Nextflow 式）：任务键 = sha256(插值后脚本源码 + 引用参数 +
    输入内容哈希 + 容器标签)，键未见过才重跑。
  场景：qual 20→30 后两种调度各跑一遍，再统计新旧 summary 的差异细胞数。

正文引用的输出（手算可对）：
  - 参数变更后调度器 A 计划作业数 = 0（Nothing to be done），summary 内容
    逐字节不变，且文件内记录的仍是旧参数 qual=20 → 「结果陈旧而不报错」；
  - 调度器 B 重跑 filter+summary、index 命中缓存（scheduled=2 / cached=1）；
  - 新旧 summary 差异细胞占比（陈旧结果错多少的量化）；
  - -R 强制重跑（讲义 ⑨-6 的解法）在调度器 A 下的作业数 = 2。

参数：
  --n-tx        玩具矩阵的转录本数（默认 40）
  --n-samples   玩具矩阵的样本数（默认 4）
  --qual-a/--qual-b  改参数前后的阈值（默认 20 / 30）
  --seed        随机种子（默认 20261105）

合成数据不得写成真实样本结果。只依赖 numpy；< 1 s。
用法：PYTHONDONTWRITEBYTECODE=1 python3 demos/ch23_stale_output_mtime.py --selftest
"""
import argparse
import hashlib
import inspect
import os
import tempfile
from pathlib import Path

import numpy as np

SCRIPT_A = "filter(step1)"
SCRIPT_INDEX = "index(step2)"
SCRIPT_SUMMARY = "summary(step3)"
CONTAINER = "quay.io/biocontainers/fastrack:1.0--h0_0"  # 合成镜像标签


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---- 玩具流程的三步（每个函数体即「脚本」，调度器 B 对其源码求哈希） --------

def step_filter(raw: Path, out: Path, qual: int) -> None:
    """阈值过滤：低于 qual 的计数置零（类比 fastp 的 --qualified_quality_phred）。"""
    mat = np.loadtxt(raw, delimiter="\t")
    mat[mat < qual] = 0
    np.savetxt(out, mat, delimiter="\t", fmt="%.0f")


def step_index(transcripts: Path, out: Path) -> None:
    """建索引：只依赖转录组名单，无阈值参数（类比 salmon index）。"""
    names = transcripts.read_text().splitlines()
    out.write_text("\n".join(sorted(names)) + "\n")


def step_summary(filtered: Path, index: Path, out: Path, qual: int) -> None:
    """汇总：列合计 + 检出数，并把本次所用参数写进文件（报告的阈值记录义务）。"""
    mat = np.loadtxt(filtered, delimiter="\t")
    detected = (mat > 0).sum(axis=0)
    lines = [f"# produced with qual={qual}"]
    for s in range(mat.shape[1]):
        lines.append(f"sample{s}\t{mat[:, s].sum():.0f}\t{detected[s]}")
    out.write_text("\n".join(lines) + "\n")


def src_of(fn) -> str:
    return inspect.getsource(fn)


# ---- 两种调度器 ----------------------------------------------------------------

class MtimeScheduler:
    """Snakemake 式：只认文件时间戳与存在性；参数不参与判据。"""

    name = "A-mtime(Snakemake 式)"

    def __init__(self) -> None:
        # 单调递增的时间戳计数器：保证重跑后的输出一定「新于」下游输入
        self._tick = 0

    def run(self, workdir: Path, qual: int, force: tuple[str, ...] = ()) -> dict:
        t = 1_600_000_000
        log = {"filter": "cached", "index": "cached", "summary": "cached"}

        def stamp(path: Path) -> None:
            self._tick += 1
            os.utime(path, (t + self._tick, t + self._tick))

        raw = workdir / "raw_counts.tsv"
        tx = workdir / "transcripts.txt"
        filt = workdir / "filtered.tsv"
        idx = workdir / "index.txt"
        summ = workdir / "summary.tsv"

        # filter：输入是原始数据（永不被流程改写），只需看输出是否存在/更旧
        if not filt.exists() or raw.stat().st_mtime > filt.stat().st_mtime \
                or "filter" in force:
            step_filter(raw, filt, qual)
            stamp(filt)
            log["filter"] = "ran"
        # index：无参数；输出在且新于输入即跳过
        if not idx.exists() or tx.stat().st_mtime > idx.stat().st_mtime \
                or "index" in force:
            step_index(tx, idx)
            stamp(idx)
            log["index"] = "ran"
        # summary：两个输入都在 filter/index 之后（stamp 1/2）即「最新」
        if not summ.exists() or filt.stat().st_mtime > summ.stat().st_mtime \
                or idx.stat().st_mtime > summ.stat().st_mtime \
                or "summary" in force:
            step_summary(filt, idx, summ, qual)
            stamp(summ)
            log["summary"] = "ran"
        return log


class HashScheduler:
    """Nextflow 式：任务键 = sha256(插值脚本 + 引用参数 + 输入内容哈希 + 容器)"""

    name = "B-hash(Nextflow 式)"

    def __init__(self) -> None:
        self.cache: dict[str, bytes] = {}

    def _key(self, script: str, params: dict, inputs: list[Path]) -> str:
        payload = [sha(src_of(script)), sha(CONTAINER)]
        for k in sorted(params):
            payload.append(f"{k}={params[k]}")
        payload.extend(file_sha(p) for p in inputs)
        return sha("|".join(payload))

    def run(self, workdir: Path, qual: int) -> dict:
        raw = workdir / "raw_counts.tsv"
        tx = workdir / "transcripts.txt"
        filt = workdir / "filtered.tsv"
        idx = workdir / "index.txt"
        summ = workdir / "summary.tsv"
        log = {"filter": "cached", "index": "cached", "summary": "cached"}

        k1 = self._key(step_filter, {"qual": qual}, [raw])
        if k1 not in self.cache:
            step_filter(raw, filt, qual)
            self.cache[k1] = filt.read_bytes()
            log["filter"] = "ran"
        else:
            filt.write_bytes(self.cache[k1])

        k2 = self._key(step_index, {}, [tx])
        if k2 not in self.cache:
            step_index(tx, idx)
            self.cache[k2] = idx.read_bytes()
            log["index"] = "ran"
        else:
            idx.write_bytes(self.cache[k2])

        k3 = self._key(step_summary, {"qual": qual}, [filt, idx])
        if k3 not in self.cache:
            step_summary(filt, idx, summ, qual)
            self.cache[k3] = summ.read_bytes()
            log["summary"] = "ran"
        else:
            summ.write_bytes(self.cache[k3])
        return log


def make_inputs(workdir: Path, n_tx: int, n_samples: int, seed: int) -> None:
    rng = np.random.default_rng(seed)
    mat = rng.poisson(lam=25.0, size=(n_tx, n_samples))
    np.savetxt(workdir / "raw_counts.tsv", mat, delimiter="\t", fmt="%.0f")
    (workdir / "transcripts.txt").write_text(
        "\n".join(f"tx{i:04d}" for i in range(1, n_tx + 1)) + "\n")


def diff_cells(path_a: Path, path_b: Path) -> tuple[int, int]:
    a = np.loadtxt(path_a, delimiter="\t")
    b = np.loadtxt(path_b, delimiter="\t")
    return int((a != b).sum()), a.size


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--n-tx", type=int, default=40)
    ap.add_argument("--n-samples", type=int, default=4)
    ap.add_argument("--qual-a", type=int, default=20)
    ap.add_argument("--qual-b", type=int, default=30)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    args = ap.parse_args()

    print("合成算例（不基于任何真实样本）；玩具流程 filter→index→summary 复刻 m08 Snakefile 结构")
    print()

    with tempfile.TemporaryDirectory() as tmp:
        wd = Path(tmp)
        make_inputs(wd, args.n_tx, args.n_samples, args.seed)
        raw = wd / "raw_counts.tsv"
        tx = wd / "transcripts.txt"
        t = 1_600_000_000
        os.utime(raw, (t, t))
        os.utime(tx, (t, t))

        # ---- 场景 1：Snakemake 式调度，基线 qual=20 ----
        sched_a = MtimeScheduler()
        base_a = sched_a.run(wd, args.qual_a)
        summ_a = wd / "summary.tsv"
        before = summ_a.read_bytes()
        print(f"场景 1  {sched_a.name} 基线运行 qual={args.qual_a}："
              f"{sum(v == 'ran' for v in base_a.values())} 作业执行")
        print(f"  summary 头部：{summ_a.read_text().splitlines()[0]}")

        # ---- 场景 2：研究者把阈值改成 30（config 变更），mtime 调度 ----
        after_a = sched_a.run(wd, args.qual_b)
        n_ran_a = sum(v == "ran" for v in after_a.values())
        stale = summ_a.read_bytes() == before
        header = summ_a.read_text().splitlines()[0]
        print(f"\n场景 2  参数 {args.qual_a}→{args.qual_b} 后 {sched_a.name} 再跑：")
        print(f"  计划作业数 = {n_ran_a}（Nothing to be done——参数不参与判据）")
        print(f"  summary 逐字节未变：{stale}；文件内参数记录：{header}"
              f"（配置已是 {args.qual_b} → 结果陈旧而不报错）")

        # 陈旧后果量化：此刻「正确的」qual=30 结果与磁盘上旧结果差多少
        filt_true = wd / "filtered_true.tsv"
        idx_tmp = wd / "index.txt"
        summ_true = wd / "summary_true.tsv"
        step_filter(raw, filt_true, args.qual_b)
        step_summary(filt_true, idx_tmp, summ_true, args.qual_b)
        filt_old = wd / "filtered.tsv"
        n_diff, n_total = diff_cells(filt_old, filt_true)
        print(f"  陈旧量化：filter 输出与正确的 qual={args.qual_b} 输出相比，"
              f"{n_diff}/{n_total} 个细胞不同（{n_diff / n_total:.1%} 的数字是错的）")

        # ---- 场景 3：-R 强制重跑（讲义 ⑨-6 解法），filter 及其下游 ----
        force = sched_a.run(wd, args.qual_b, force=("filter",))
        # -R filter 只会强制 filter；summary 的输入 mtime 刷新后自然重跑
        n_force = sum(v == "ran" for v in force.values())
        print(f"\n场景 3  {sched_a.name} 加 -R filter 强制重跑：执行 {n_force} 作业"
              f"（filter + 下游 summary；index 不受影响）")
        header_after = summ_a.read_text().splitlines()[0]
        print(f"  summary 参数记录变为：{header_after}")

        # ---- 场景 4：Nextflow 式调度，同样改参数 ----
        sched_b = HashScheduler()
        base_b = sched_b.run(wd, args.qual_a)
        n_base_b = sum(v == "ran" for v in base_b.values())
        after_b = sched_b.run(wd, args.qual_b)
        n_ran_b = sum(v == "ran" for v in after_b.values())
        n_cached_b = sum(v == "cached" for v in after_b.values())
        rerun_nochange = sched_b.run(wd, args.qual_b)
        n_rerun = sum(v == "ran" for v in rerun_nochange.values())
        header_b = (wd / "summary.tsv").read_text().splitlines()[0]
        print(f"\n场景 4  {sched_b.name}：")
        print(f"  基线 qual={args.qual_a}：执行 {n_base_b} 作业（三步全算）")
        print(f"  参数 {args.qual_a}→{args.qual_b}：执行 {n_ran_b}、命中缓存 {n_cached_b}"
              f"（filter/summary 重算，无参数的 index 命中缓存）")
        print(f"  无变更再跑：执行 {n_rerun}（-resume 全命中）")
        print(f"  summary 参数记录：{header_b}")

        if args.selftest:
            checks = [
                (f"场景 2 参数变更后 mtime 调度计划 {n_ran_a} 作业（=0，陈旧不报错）",
                 n_ran_a == 0 and stale),
                (f"summary 文件内仍记录 qual={args.qual_a}（与磁盘配置 {args.qual_b} 背离）",
                 f"qual={args.qual_a}" in header),
                (f"陈旧量化：差异细胞 {n_diff}/{n_total} 在 (0, 总细胞) 之间",
                 0 < n_diff < n_total),
                (f"-R 强制重跑执行 {n_force} 作业（filter+summary，index 不动）",
                 n_force == 2),
                ("强制重跑后 summary 已记录新参数",
                 f"qual={args.qual_b}" in header_after),
                (f"基线 hash 调度执行 {n_base_b} 作业（=3）", n_base_b == 3),
                (f"参数变更后 hash 调度执行 {n_ran_b}、缓存 {n_cached_b}（=2/1）",
                 n_ran_b == 2 and n_cached_b == 1),
                (f"无变更再跑执行 {n_rerun}（=0，全命中）", n_rerun == 0),
                ("hash 调度输出记录新参数",
                 f"qual={args.qual_b}" in header_b),
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

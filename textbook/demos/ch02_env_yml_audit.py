#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch02_env_yml_audit.py — 解析 ../07_envs/conda/*.yml：16 个环境的 pin 审计与
「环境名只由 yml 的 name: 决定」对照表

服务章节：第 2 章 §2.4「概念与方法」（课程 16 个环境的拆分与 pin 策略）、
§2.5 失效条件第 1 条（环境名 ≠ 文件名，教学点勿「修正」）与 §2.6 贯穿案例
（本章交付物形态）的复现入口。

数据性质：只读取课程真实定义文件 ../07_envs/conda/*.yml（16 个），不做任何修改；
输出为对这些文件的**确定性统计**（无随机性，固定种子不适用），不是测序数据，
也不是 conda solve 结果。

正文引用的输出（以 --selftest 断言锁定）：
  - 环境总数 = 16（本科 4 + 硕士 6 + 博士 6），与根 CLAUDE.md / 07_envs README 一致
  - 每个 yml 的 channels 首项均为 conda-forge（conda-forge ≻ bioconda ≻ defaults 的铁律
    在定义层已固化）；任意 yml 出现其它顺序即 FAIL
  - 全部 16 个 yml 都钉了 setuptools<81（根 CLAUDE.md：16 个环境 15 个曾中招后的统一修法）
  - 环境名 ≠ 文件名直推的恰好 2 个：env_ug_annotation.yml → ngs_ug_annot
    （课程教学点，l0_03/u01 反复引用）与 env_phd_singlecell.yml → ngs_phd_sc
    （同一现象的博士层实例，讲义未点名）
  - pin 统计：全部依赖条目中「带版本约束」与「裸包名」的数量（正文若引用须以
    本脚本现跑输出为准，因为 yml 会被总编修订）
  - env_master_transcriptome.yml 同时含 python=3.10 与 salmon=1.10.3
    （根 CLAUDE.md 两个 solve 案例的落点核对）

参数含义：
  --env-dir  yml 目录（默认 ../07_envs/conda，即仓库根的 07_envs/conda）
  --selftest 断言上述关键统计后退出（正文引用前必须保持通过）
"""
import argparse
import glob
import os
import re
import sys

# 文件名 → 环境名的直推规则（与课程命名约定一致）：
#   env_ug_<X>.yml      → ngs_ug_<X>
#   env_master_<X>.yml  → ngs_ms_<X>（master 层缩写为 ms）
#   env_phd_<X>.yml     → ngs_phd_<X>
DERIVE = (
    (re.compile(r"^env_ug_(.+)\.yml$"), "ngs_ug_{}"),
    (re.compile(r"^env_master_(.+)\.yml$"), "ngs_ms_{}"),
    (re.compile(r"^env_phd_(.+)\.yml$"), "ngs_phd_{}"),
)


def expected_name(fname):
    for pat, fmt in DERIVE:
        m = pat.match(fname)
        if m:
            return fmt.format(m.group(1))
    return None


def parse_yml(path):
    """最小解析器：只取本仓库 yml 实际用到的结构（顶层 name:/channels:/
    dependencies: 及其「- 条目」行）。依赖行剥离「 #」起的行内注释。
    返回 (name, channels, deps, python_pin, salmon_pin)。"""
    name, channels, deps = None, [], []
    section = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            if not line.startswith(" "):
                key = line.split(":", 1)[0].strip()
                section = key if line.rstrip().endswith(":") else None
                if key == "name":
                    name = line.split(":", 1)[1].strip()
                continue
            if section in ("channels", "dependencies"):
                item = line.strip()
                if item.startswith("- "):
                    val = item[2:].split(" #", 1)[0].strip()
                    if section == "channels":
                        channels.append(val)
                    else:
                        deps.append(val)
    python_pin = [d for d in deps if d == "python" or d.startswith("python") and
                  d[len("python")] in "<>="] or None
    salmon_pin = [d for d in deps if d.startswith("salmon")] or None
    return name, channels, deps, python_pin, salmon_pin


def is_pinned(dep):
    """裸包名（fastp、r-tidyverse）为未 pin；含 =<> 或 * 即为带约束。"""
    return any(ch in dep for ch in "<>=*")


def main():
    ap = argparse.ArgumentParser(
        description="审计 ../07_envs/conda/*.yml 的 name/channels/pin（只读，确定性统计）")
    ap.add_argument("--env-dir", default="../07_envs/conda",
                    help="yml 目录（默认 ../07_envs/conda）")
    ap.add_argument("--selftest", action="store_true", help="断言关键统计后退出")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.env_dir, "env_*.yml")))
    if not files:
        print(f"[FAIL] 目录里没有 env_*.yml: {args.env_dir}", file=sys.stderr)
        return 1

    rows, total_deps, total_pinned = [], 0, 0
    mismatches, no_conda_forge, missing_setuptools = [], [], []
    py310_envs, salmon_envs = [], []

    for path in files:
        fname = os.path.basename(path)
        name, channels, deps, python_pin, salmon_pin = parse_yml(path)
        pinned = sum(is_pinned(d) for d in deps)
        total_deps += len(deps)
        total_pinned += pinned
        exp = expected_name(fname)
        mismatch = (name != exp)
        if mismatch:
            mismatches.append((fname, name))
        if not channels or channels[0] != "conda-forge":
            no_conda_forge.append(fname)
        if not any(d.startswith("setuptools") and "<81" in d for d in deps):
            missing_setuptools.append(fname)
        if python_pin:
            py310_envs.append((fname, python_pin))
        if salmon_pin:
            salmon_envs.append((fname, salmon_pin))
        rows.append((fname, name, exp, mismatch, len(deps), pinned,
                     len(deps) - pinned, ">".join(channels)))

    print(f"目录：{os.path.abspath(args.env_dir)} ｜ 共 {len(files)} 个 yml")
    print(f"{'yml 文件':<34}{'name: 环境名':<22}{'直推名':<22}{'名≠直推':<8}"
          f"{'依赖':<5}{'pin':<5}{'未pin':<6}频道顺序")
    for r in rows:
        print(f"{r[0]:<34}{r[1]:<22}{r[2]:<22}{'是' if r[3] else '':<8}"
              f"{r[4]:<5}{r[5]:<5}{r[6]:<6}{r[7]}")

    print(f"\n合计：依赖条目 {total_deps}，带版本约束 {total_pinned}，"
          f"裸包名 {total_deps - total_pinned}")
    print(f"环境名 ≠ 文件名直推：{len(mismatches)} 个 → "
          + "；".join(f"{f} → {n}" for f, n in mismatches))
    print(f"channels 首项非 conda-forge：{len(no_conda_forge)} 个")
    print(f"缺 setuptools<81：{len(missing_setuptools)} 个")
    print(f"含 python pin：{'; '.join(f'{f} {p[0]}' for f, p in py310_envs) or '无'}")
    print(f"含 salmon pin：{'; '.join(f'{f} {p[0]}' for f, p in salmon_envs) or '无'}")

    ok = True

    def check(cond, msg):
        nonlocal ok
        if not cond:
            ok = False
            print(f"[FAIL] {msg}", file=sys.stderr)

    check(len(files) == 16, f"应恰好 16 个 yml，实得 {len(files)}")
    check(not no_conda_forge, f"这些 yml 频道顺序异常: {no_conda_forge}")
    check(not missing_setuptools, f"这些 yml 缺 setuptools<81: {missing_setuptools}")
    check({f for f, _ in mismatches} ==
          {"env_ug_annotation.yml", "env_phd_singlecell.yml"},
          f"名≠直推集合异常: {mismatches}")
    check(dict((f, p[0]) for f, p in py310_envs).get("env_master_transcriptome.yml")
          == "python=3.10", "env_master_transcriptome.yml 应钉 python=3.10")
    check(len(salmon_envs) == 2 and
          all(p[0] == "salmon=1.10.3" for _, p in salmon_envs),
          f"salmon 应恰好两个环境且均 =1.10.3: {salmon_envs}")

    if args.selftest:
        status = "PASS" if ok else "FAIL"
        print(f"SELFTEST {status}：16 个 yml；channels 首项全为 conda-forge；"
              f"16/16 含 setuptools<81；名≠直推恰为 annotation/annot 与 singlecell/sc；"
              f"env_master_transcriptome 含 python=3.10；"
              f"两个环境 salmon=1.10.3")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

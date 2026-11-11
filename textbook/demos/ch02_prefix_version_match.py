#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch02_prefix_version_match.py — conda 版本约束的前缀语义：=3.10 为什么命中 3.10.21

服务章节：第 2 章 §2.4「概念与方法」（版本 pin 的语法语义、批量预检包名与版本）、
§2.5 失效条件第 4 条（大环境不收敛时先加 python= pin 的依据）与根 CLAUDE.md §三
「conda 环境的坑」两条一手素材的复现入口：
  - 「版本匹配要按 conda 的前缀语义（=3.10 命中 3.10.21），否则全是假警报」；
  - setuptools<81 的钉法与 salmon=1.10.3 补丁级 pin 的理由。

数据性质：本脚本不联网、不查询 anaconda.org；内置的是**合成教学版版本目录**
（版本号取自根 CLAUDE.md 实查记录与 ../07_envs/conda/*.yml 的现行 pin，仅作教学
演示，不是任何时刻的渠道实时数据）。脚本无随机性（固定种子不适用），输出完全确定。

正文引用的输出：
  - `python=3.10` 在候选 [3.9.16, 3.10.13, 3.10.21, 3.11.4] 中命中 3.10.13 与
    3.10.21，求解器取最高 → 3.10.21（根 CLAUDE.md §三「批量预检」原文数字）
  - `python=3.1` 只命中 3.1.4、**不**命中 3.10.21：前缀是按「点分段」比的，
    不是字符串开头比对（预检脚本报假警报/假阴性的机理）
  - `python==3.10`（双等号）只认字面 3.10，对 3.10.21 判不满足
  - `setuptools<81` 取到 80.9.0；不钉则取到 84.0.0（失效条件 3「一跑就炸」的
    上游机制：新环境默认拿到 setuptools 84，15/16 个环境曾中招）
  - `salmon=1.10` 会放行 1.10.0/1.10.2/1.10.3 三个版本，其中 1.10.0/1.10.2 与
    r-base=4.3.1 因 icu 互斥 → 必须钉到补丁级 `salmon=1.10.3`（CLAUDE.md 实查结论）
  - 预检对照：把 `=3.10` 当精确等号查目录，2 个可用版本被误报「不满足」；
    按前缀语义 0 个误报 → 「否则全是假警报」的数量级演示

参数含义：
  --selftest  断言上述关键结果后退出（正文引用前必须保持通过）
  --quiet     只打印 selftest 结论（供管道调用）
"""
import argparse
import sys


def parse_version(v):
    """'3.10.21' -> (3, 10, 21)；'81' -> (81,)。只取每段的数字前缀（教学简化，
    不处理 conda 完整的 epoch/预发布规则，本演示集的版本号均不受影响）。"""
    parts = []
    for tok in v.split("."):
        num = ""
        for ch in tok:
            if ch.isdigit():
                num += ch
            else:
                break
        parts.append(int(num) if num else 0)
    return tuple(parts)


def cmp_version(a, b):
    ta, tb = parse_version(a), parse_version(b)
    n = max(len(ta), len(tb))
    ta += (0,) * (n - len(ta))
    tb += (0,) * (n - len(tb))
    return (ta > tb) - (ta < tb)


def match_constraint(version, op, ref):
    if op == "=":  # conda 单等号 = 前缀语义：ref 的每个点分段都相同即命中
        rv, sv = parse_version(ref), parse_version(version)
        return sv[: len(rv)] == rv
    if op == "==":  # conda == compares by version order: trailing zeros ignored (1.17 == 1.17.0)
        return cmp_version(version, ref) == 0
    c = cmp_version(version, ref)
    return {"<": c < 0, "<=": c <= 0, ">": c > 0, ">=": c >= 0}[op]


def split_spec(spec):
    """'setuptools<81' -> ('setuptools', [('<', '81')])；'python>=3.8,<3.12' 多约束。
    顺序扫描找第一个 <>=* 字符；裸包名（如 'fastp'）约束为空列表 = 任意版本。"""
    cut = len(spec)
    for i, ch in enumerate(spec):
        if ch in "<>=*":
            cut = i
            break
    pkg = spec[:cut]
    rest = spec[cut:]
    cons = []
    for piece in rest.split(","):
        piece = piece.strip()
        if not piece:
            continue
        if piece.startswith("=="):
            cons.append(("==", piece[2:]))
        elif piece[0] in "<>=":
            op = piece[0]
            ref = piece[1:]
            if ref.startswith("="):
                op += "="  # <= 或 >=
                ref = ref[1:]
            cons.append((op, ref))
        elif piece[0] == "*":
            cons.append(("=", piece[1:].rstrip(".*")))
    return pkg, cons


def match_spec(spec, version):
    _, cons = split_spec(spec)
    return all(match_constraint(version, op, ref) for op, ref in cons)


def solve_pick(spec, catalog):
    """合成求解器：从命中版本里取最高（conda 默认取向，演示用）。"""
    hits = [v for v in catalog if match_spec(spec, v)]
    if not hits:
        return None, []
    return max(hits, key=lambda v: parse_version(v)), hits


def demo_report(title, spec, catalog):
    """打印一行对照：spec × 候选目录 → 命中集与求解器选择。返回 (pick, hits)。"""
    pick, hits = solve_pick(spec, catalog)
    miss = [v for v in catalog if v not in hits]
    print(f"{title}")
    print(f"  约束 {spec:<18} 候选目录: {catalog}")
    print(f"  命中 {hits}；求解器取最高 → {pick}"
          + (f"；目录中其余 {miss} 被排除" if miss else ""))
    return pick, hits


def main():
    ap = argparse.ArgumentParser(
        description="conda 版本约束前缀语义教学演示（合成数据，不联网）")
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    ap.add_argument("--quiet", action="store_true", help="只打印 selftest 结论")
    args = ap.parse_args()
    quiet = args.quiet

    ok = True

    def check(cond, msg):
        nonlocal ok
        if not cond:
            ok = False
            print(f"  [FAIL] {msg}", file=sys.stderr)

    # --- 情形 1：根 CLAUDE.md 原文数字 =3.10 命中 3.10.21 ---------------------
    if not quiet:
        print("== 情形 1：单等号 = 是「点分段前缀」，不是精确等号 ==")
    pick, hits = demo_report("python 候选（合成目录）", "python=3.10",
                             ["3.9.16", "3.10.13", "3.10.21", "3.11.4"]) \
        if not quiet else solve_pick("python=3.10", ["3.9.16", "3.10.13", "3.10.21", "3.11.4"])
    check(pick == "3.10.21" and sorted(hits) == ["3.10.13", "3.10.21"],
          "=3.10 应命中 3.10.13/3.10.21 并取 3.10.21")

    # --- 情形 2：点分段 vs 字符串开头的陷阱 ----------------------------------
    if not quiet:
        print("\n== 情形 2：=3.1 不命中 3.10.21（点分段语义）==")
    pick2, hits2 = demo_report("python 候选（合成目录）", "python=3.1",
                               ["3.1.4", "3.10.21"]) \
        if not quiet else solve_pick("python=3.1", ["3.1.4", "3.10.21"])
    check(pick2 == "3.1.4" and hits2 == ["3.1.4"], "=3.1 应只命中 3.1.4")

    # --- 情形 3：双等号 == 才是精确字面 --------------------------------------
    if not quiet:
        print("\n== 情形 3：python==3.10 对 3.10.21 判不满足 ==")
    pick3, hits3 = demo_report("python 候选（合成目录）", "python==3.10",
                               ["3.10.13", "3.10.21"]) \
        if not quiet else solve_pick("python==3.10", ["3.10.13", "3.10.21"])
    check(pick3 is None and hits3 == [], "==3.10 对 3.10.x 应无解")
    # FIN-CH02-01: == is version-order equality, not string equality
    check(match_constraint("1.17.0", "==", "1.17") and not match_constraint("1.17.1", "==", "1.17"),
          "==1.17 应命中 1.17.0（尾零不影响相等）、不命中 1.17.1")

    # --- 情形 4：setuptools<81 与「不钉就拿 84」 ------------------------------
    if not quiet:
        print("\n== 情形 4：setuptools 的钉法（失效条件 3 的上游机制）==")
    pick4, hits4 = demo_report("setuptools 钉住", "setuptools<81",
                               ["80.9.0", "81.0.0", "84.0.0"]) \
        if not quiet else solve_pick("setuptools<81", ["80.9.0", "81.0.0", "84.0.0"])
    pick4b, _ = solve_pick("setuptools", ["80.9.0", "81.0.0", "84.0.0"])
    if not quiet:
        print(f"  对照：不钉（裸 setuptools）→ 求解器取最高 → {pick4b}"
              "（CLAUDE.md：新环境默认拿到 setuptools 84，16 个环境 15 个因此中招）")
    check(pick4 == "80.9.0" and hits4 == ["80.9.0"], "setuptools<81 应取 80.9.0")
    check(pick4b == "84.0.0", "不钉 setuptools 应取到 84.0.0")

    # --- 情形 5：salmon 补丁级 pin 的理由 ------------------------------------
    if not quiet:
        print("\n== 情形 5：salmon=1.10.3 为什么钉到补丁级（icu 互斥）==")
    pick5, hits5 = demo_report("salmon 只钉到次版本", "salmon=1.10",
                               ["1.10.0", "1.10.2", "1.10.3"]) \
        if not quiet else solve_pick("salmon=1.10", ["1.10.0", "1.10.2", "1.10.3"])
    pick5b, hits5b = demo_report("salmon 钉到补丁级", "salmon=1.10.3",
                                 ["1.10.0", "1.10.2", "1.10.3"]) \
        if not quiet else solve_pick("salmon=1.10.3", ["1.10.0", "1.10.2", "1.10.3"])
    if not quiet:
        print("  1.10.0/1.10.2 与 r-base=4.3.1 因 icu 区间互斥（CLAUDE.md 实查），"
              "故 yml 必须钉到补丁级，=1.10 不够")
    check(len(hits5) == 3, "salmon=1.10 应放行全部三个补丁版本")
    check(pick5b == "1.10.3" and hits5b == ["1.10.3"], "salmon=1.10.3 应只命中 1.10.3")

    # --- 情形 6：批量预检「否则全是假警报」的数量级 ---------------------------
    if not quiet:
        print("\n== 情形 6：预检脚本的两种匹配口径对照（合成目录）==")
    pin = "3.10"
    catalog = ["3.9.16", "3.10.13", "3.10.21", "3.11.4"]
    # 朴素口径 A：把 =pin 当精确等号 → 目录里凡 3.10.x（但非字面 3.10）都误报
    alarms_list = [v for v in catalog
                   if parse_version(v)[:2] == parse_version(pin) and v != pin]
    alarms_a = len(alarms_list)
    prefix_hits = [v for v in catalog if match_spec(f"python={pin}", v)]
    if not quiet:
        print(f"  课程 yml 里出现 pin `python={pin}`，预检查 anaconda.org 目录 {catalog}")
        print(f"  口径 A（把 ={pin} 当精确等号）：{alarms_a} 个可用版本 "
              f"（{alarms_list}）被误报『不满足』→ 假警报")
        print(f"  口径 B（conda 前缀语义）：命中 {prefix_hits}，0 个误报")
    check(alarms_a == 2, "口径 A 应对 3.10.13/3.10.21 产生 2 个假警报")
    check(prefix_hits == ["3.10.13", "3.10.21"], "口径 B 应精确命中两个 3.10.x")

    if args.selftest or quiet:
        status = "PASS" if ok else "FAIL"
        print(f"SELFTEST {status}：=3.10 命中 3.10.13/3.10.21 取 3.10.21；"
              "=3.1 只命中 3.1.4；==3.10 对 3.10.x 无解；"
              "setuptools<81→80.9.0（不钉→84.0.0）；"
              "salmon=1.10 放行 3 个补丁版、=1.10.3 只命中 1.10.3；"
              "预检口径 A 2 个假警报 / 口径 B 0 个")
        return 0 if ok else 1
    print("\n（以上版本目录为合成教学数据；正文引用请以根 CLAUDE.md 实查记录为准。）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

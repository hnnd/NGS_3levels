#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch01_symlink_checks.py — 软链接断链：「ls 看得见、cat 报不存在」的检测清单（本机行为复现）

服务章节：第 1 章 §1.4 正文（文件系统、路径与软链接）、§1.5 失效条件第 4 条
（复制大文件代替软链接耗尽配额；软链接指向的源被移动后静默断链）；
并对照仓库脚本 01_seq_stats.sh 开头的 [[ -f ]] 守门（其报错文本引用讲义 ⑥ 6.2）。

数据性质：本脚本不产生任何测序数据；在 ta 本机的临时目录（tempfile 自动清理，
不留产物）里创建、移动、删除真实文件与软链接，复现文件系统行为事实。

正文引用的输出：
  - 断链判定三件套（= bash 的 [[ -L ]] / [[ -e ]] / [[ -f ]]）：
    Path.is_symlink()=True 而 Path.exists()=False、Path.is_file()=False
    → 「ls 列表里看得见，但一切跟随式读取都失败」的机理（l0_01 §3）
  - ls -lL 跟随后断链返回非零；cat 断链 rc=1 且报 "No such file or directory"（l0_01 §3）
  - 软链接自身磁盘开销 = 目标路径字符串的字节数（lstat().st_size，几十 B）
    vs 复制文件占用真实文件大小 —— ln -s 与 cp 的配额差别（失效条件 4 上半）
  - 源被移动（os.rename）后原软链接即刻断链 —— 失效条件 4 下半的复现
  - 01_seq_stats.sh 守门等价物：[[ -f 断链 ]] 为假 → 脚本以「断链」提示退出 1
    （讲义 u01 ⑥ 6.2 ①的排错入口：ls -lL 探测 + ln -sf 覆盖修复）

参数含义：
  --selftest  断言上述关键事实后退出（正文引用前必须保持通过）
"""
import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def bash_test(path, bash="bash"):
    """等价 01_seq_stats.sh 的守门：[[ -f <路径> ]] 是否为真。"""
    p = subprocess.run(
        [bash, "-c", 'if [[ -f "$1" ]]; then echo ISFILE; else echo NOTFILE; fi',
         "_", str(path)],
        capture_output=True, text=True)
    return p.stdout.strip()


def build_workspace(root: Path):
    """搭一个最小项目目录：真实文件、活链接、断链接、会被移走的源。"""
    real = root / "reads.fa"
    real.write_text(">r1\nACGTACGTAC\n")
    good = root / "good.fa"
    good.symlink_to("reads.fa")            # 相对路径软链接，模拟 fq/ 下的链接

    broken = root / "broken.fa"
    broken.symlink_to("reads_moved_away.fa")  # 目标从未存在：路径拼错的 ln -s

    victim_src = root / "raw.fa"
    victim_src.write_text(">x\nTTTT\n")
    victim = root / "victim.fa"
    victim.symlink_to("raw.fa")
    os.rename(victim_src, root / "raw_v2.fa")  # 管理员深夜改名：源被移动 → 即刻断链
    return real, good, broken, victim


def probe(name, link: Path, bash="bash"):
    """对一个链接跑全套检测，打印一行结论。"""
    islink = link.is_symlink()
    exists = link.exists()
    isfile = link.is_file()
    lstat_size = os.lstat(link).st_size if islink else None
    target = os.readlink(link) if islink else ""

    cat = subprocess.run([bash, "-c", 'cat "$1" >/dev/null', "_", str(link)],
                         capture_output=True, text=True)
    lsl = subprocess.run([bash, "-c", 'ls -lL "$1" >/dev/null 2>&1', "_", str(link)])
    guard = bash_test(link, bash)

    state = "断链" if (islink and not exists) else "活链接"
    print(f"[{name}] {state}")
    print(f"  is_symlink={islink}  exists={exists}  is_file={isfile}"
          f"   ← bash: [[ -L ]]={islink}  [[ -e ]]={exists}  [[ -f ]]={isfile}")
    print(f"  链接自身大小（lstat）= {lstat_size} B = 目标路径字符串 '{target}' 的字节数"
          f"（vs cp 复制占用 {os.path.getsize(os.path.realpath(link)) if exists else '-'} B 真实文件）")
    print(f"  cat  : rc={cat.returncode}"
          + (f"，stderr='{cat.stderr.strip()}'" if cat.returncode else ""))
    print(f"  ls -lL: rc={lsl.returncode}"
          + ("（非零 = 跟随失败，l0_01 §3 的黄金验证）" if lsl.returncode else ""))
    print(f"  [[ -f ]] 守门（01_seq_stats.sh 同款）: {guard}"
          + (" → 脚本会带『断链』提示退出 1" if guard == "NOTFILE" and islink
             else " → 通过，进入格式识别与统计"))
    return dict(islink=islink, exists=exists, isfile=isfile,
                lstat_size=lstat_size, target=target,
                cat_rc=cat.returncode, cat_err=cat.stderr.strip(),
                lsl_rc=lsl.returncode, guard=guard)


def selftest(bash="bash"):
    print("=== SELFTEST（文件系统行为复现，ta 本机临时目录）===")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _, good, broken, victim = build_workspace(root)
        print("工作区（临时目录，退出即清理）：reads.fa + good.fa(活) + broken.fa(断) "
              "+ victim.fa(源被改名 raw.fa→raw_v2.fa)\n")
        g = probe("good.fa", good, bash)
        print()
        b = probe("broken.fa", broken, bash)
        print()
        v = probe("victim.fa", victim, bash)
        print()

        # 关键断言（正文引用点）
        assert g["islink"] and g["exists"] and g["isfile"], "活链接三件套应全真"
        assert g["cat_rc"] == 0 and g["lsl_rc"] == 0 and g["guard"] == "ISFILE"
        assert g["lstat_size"] == len(g["target"]), "活链接大小应等于路径字符串长度"

        assert b["islink"] and not b["exists"] and not b["isfile"], \
            "断链接：is_symlink 真、exists/is_file 假"
        assert b["cat_rc"] == 1 and "No such file or directory" in b["cat_err"]
        assert b["lsl_rc"] != 0, "ls -lL 对断链应返回非零"
        assert b["guard"] == "NOTFILE"
        assert b["lstat_size"] == len(b["target"]) and b["lstat_size"] < 100, \
            "断链接仍是几十字节的小文件（ls 里看得见）"

        assert v["islink"] and not v["exists"], "源被移动后 victim.fa 应即刻断链"
        assert v["cat_rc"] == 1 and v["guard"] == "NOTFILE"
        print("真实文件 reads.fa 大小 = "
              f"{os.path.getsize(root / 'reads.fa')} B；软链接开销 = {g['lstat_size']} B "
              "→ cp 接入占配额、ln -s 不占（失效条件 4 上半的机理数字）")

    print("SELFTEST PASS：断链三件套（-L 真/-e 假/-f 假）、cat rc=1 + No such file or "
          "directory、ls -lL 非零、[[ -f ]] 守门 NOTFILE、源被移动即断链、链接开销=路径字节数")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="软链接断链检测清单（文件系统行为复现，非合成样本结果）")
    ap.add_argument("--selftest", action="store_true",
                    help="断言正文引用的关键事实后退出")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    return selftest()  # 本演示只有自检一种模式；直接跑全量清单


if __name__ == "__main__":
    sys.exit(main())

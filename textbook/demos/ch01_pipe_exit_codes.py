#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch01_pipe_exit_codes.py — 管道退出码、PIPESTATUS 与 pipefail 对照表；head 截断致上游 SIGPIPE（rc=141）

服务章节：第 1 章 §1.4「概念与方法」硕士深入块（进程与信号、退出码与 pipefail）、
§1.5 失效条件第 3 条（管道的退出码只反映最后一段：上游失败而整条命令 rc=0；
反之 head 截断让上游 SIGPIPE 非零是预期行为——根 CLAUDE.md「set -euo pipefail +
流式截取」实测案例的复现入口）。

数据性质：本脚本不产生任何测序数据；用 subprocess 在 ta 本机调 bash 复现 shell
行为事实（退出码是行为复现，不是合成样本结果，也不是集群实测）。

正文引用的输出：
  - `false | true`：默认 rc=0 而 PIPESTATUS=(1 0)；`set -o pipefail` 后 rc=1
    → 「上游失败而整条命令 rc=0」的对照表（失效条件 3 上半）
  - `grep 不存在的文件 | wc -l`：grep 退出 2，管道 rc=0，打印 0——静默失败典型
  - `yes | head -n 1`：上游 yes 被 SIGPIPE(13) 杀死，退出码 141 = 128 + 13；
    管道默认 rc=0，pipefail 下 rc=141；`set -euo pipefail` 的脚本在此中止且
    后续命令不执行（失效条件 3 下半 + CLAUDE.md 案例）
  - 保护写法要两层：只给紧邻 head 的一段加 `{ cat || true; }` 不够（更上游的 seq
    仍死于 141、pipefail 下整条 rc=141）；根 CLAUDE.md download_phd.sh:92-93 同款是
    组内 `{ … || true; }` + 行尾 `|| true`，然后改用产物有效性检查代替退出码检查
  - 内核管道容量（ta 实测，fcntl F_GETPIPE_SZ）→ 讲义 l0_01 §2「环形缓冲区（通常
    64 KB）」；Linux 2.6.11+ 默认值 65536 B（集群未实测，标 ta 实测）
  - Python 解释器启动时把 SIGPIPE 置为忽略 → 写已关闭管道抛 BrokenPipeError；
    恢复 SIG_DFL 后子进程被信号 13 杀死（subprocess returncode = -13）
    ——解释「为什么 bash 脚本死成 141 而 Python 脚本抛异常」

参数含义：
  --bash    用于复现的 bash 路径（默认沿 PATH 找 bash；断言只依赖 bash 语义）
  --selftest  断言上述关键数字后退出（正文引用前必须保持通过）
"""
import argparse
import fcntl
import os
import shutil
import signal
import subprocess
import sys
import textwrap


def run_bash(snippet, bash="bash"):
    """跑一段 bash 片段，返回 (rc, stdout, stderr)。"""
    p = subprocess.run([bash, "-c", snippet], capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def demo_false_true(bash):
    """对照表第 1 行：上游失败被最后一段掩盖。"""
    rc, out, _ = run_bash(
        'false | true; printf "rc=%d PIPESTATUS=(%s)" "$?" "${PIPESTATUS[*]}"', bash)
    rc_pf, out_pf, _ = run_bash(
        'set -o pipefail; false | true; printf "rc=%d" "$?"', bash)
    print("情形 1  false | true（上游失败、下游成功）")
    print(f"  默认 bash        : {out}")
    print(f"  set -o pipefail  : {out_pf}  ← pipefail 把上游失败翻成管道退出码")
    assert "rc=0" in out and "1 0" in out, f"默认 rc/PIPESTATUS 异常: {out}"
    assert rc == 0 and "rc=1" in out_pf, f"pipefail 应得 rc=1，输出为: {out_pf}"
    return rc, rc_pf


def demo_grep_missing(bash):
    """上游 grep 文件不存在：管道照样 rc=0，输出一个'看起来合法'的 0。"""
    snippet = ('grep ACGT /definitely/not/exists.fa 2>/dev/null | wc -l; '
               'printf "rc=%d PIPESTATUS=(%s)" "$?" "${PIPESTATUS[*]}"')
    rc, out, _ = run_bash(snippet, bash)
    print("情形 2  grep <不存在的文件> | wc -l（生信日常版：上游根本没产出数据）")
    print(f"  默认 bash  : 输出 '{out.splitlines()[0]}'，{out.splitlines()[-1]}"
          "  ← 0 行与'文件里没有匹配'不可区分")
    assert rc == 0 and "2 0" in out, f"grep 情形异常: rc={rc} out={out}"
    return rc


def demo_yes_head(bash):
    """head 截断 → 上游 SIGPIPE → 141；pipefail/set -e 下的脚本中止与修法。"""
    snippet = ('yes | head -n 1 >/dev/null; '
               'printf "rc=%d PIPESTATUS=(%s)" "$?" "${PIPESTATUS[*]}"')
    rc, out, _ = run_bash(snippet, bash)
    rc_pf, out_pf, _ = run_bash(
        'set -o pipefail; yes | head -n 1 >/dev/null; printf "rc=%d" "$?"', bash)
    print("情形 3  yes | head -n 1（head 取够就退出，上游被掐断）")
    print(f"  默认 bash        : {out}")
    print(f"  set -o pipefail  : {out_pf}")
    print("  141 = 128 + 13（SIGPIPE）——非零是这个技术的预期行为，不是错误"
          "（失效条件 3 下半；根 CLAUDE.md「set -euo pipefail + 流式截取」）")

    script_e = textwrap.dedent("""\
        set -euo pipefail
        yes | head -n 1 >/dev/null
        echo AFTER
    """)
    rc_e, out_e, _ = run_bash(script_e, bash)
    print("情形 4  set -euo pipefail 的下载式脚本被 141 整体击毙：")
    print(f"  bash -c '<set -euo pipefail; yes | head -n1; echo AFTER>' "
          f"→ rc={rc_e}，输出 [{out_e or '<空>'}]（AFTER 未执行，脚本静默半途而废）")

    script_half = textwrap.dedent("""\
        set -euo pipefail
        seq 1 100000 | { cat || true; } | head -n 3 | wc -l
        echo "rc=$? AFTER"
    """)
    rc_h, out_h, _ = run_bash(script_half, bash)
    print("情形 5a 只保护紧邻 head 的一段还不够：seq 在更上游照样被 SIGPIPE 杀死，"
          "pipefail 仍得 141：")
    print(f"  seq 1 100000 | {{ cat || true; }} | head -n 3 | wc -l "
          f"→ rc={rc_h}，输出 [{out_h or '<空>'}]（AFTER 仍未执行）")

    script_fix = textwrap.dedent("""\
        set -euo pipefail
        seq 1 100000 | { cat || true; } | head -n 3 | wc -l || true
        echo "rc=$? AFTER"
    """)
    rc_f, out_f, _ = run_bash(script_fix, bash)
    lines = [l for l in out_f.splitlines() if l.strip()]
    print("情形 5b 修法（根 CLAUDE.md download_phd.sh:92-93 同款两层保护）：组内 { … || true; } "
          "+ 行尾 || true，然后改用产物有效性检查：")
    print(f"  seq 1 100000 | {{ cat || true; }} | head -n 3 | wc -l || true "
          f"→ 输出 {lines}，rc={rc_f}")

    assert "141" in out and "0" in out.split("PIPESTATUS=")[1], f"SIGPIPE 情形异常: {out}"
    assert rc == 0 and "rc=141" in out_pf, f"pipefail 应得 141，输出为: {out_pf}"
    assert rc_e == 141 and "AFTER" not in out_e, f"set -e 中止异常: rc={rc_e}"
    assert rc_h == 141 and "AFTER" not in out_h, f"半保护应仍被击毙: rc={rc_h}"
    assert rc_f == 0 and "rc=0 AFTER" in out_f and lines[0].startswith("3"), \
        f"修法异常: rc={rc_f} out={out_f}"
    return rc_pf


def demo_pipe_capacity():
    """讲义「管道环形缓冲区通常 64 KB」的 ta 实测（F_GETPIPE_SZ）。"""
    r, w = os.pipe()
    try:
        cap = fcntl.fcntl(w, fcntl.F_GETPIPE_SZ)
    finally:
        os.close(r)
        os.close(w)
    print(f"情形 6  内核管道容量（ta 实测 fcntl F_GETPIPE_SZ）= {cap} B = {cap/1024:.0f} KiB"
          "  ← l0_01 §2「通常为 64 KB」；Linux 2.6.11+ 默认 65536 B（集群未实测）")
    assert cap == 65536, f"本机管道容量非 64 KiB: {cap}"
    return cap


def demo_python_sigpipe():
    """Python 默认忽略 SIGPIPE → BrokenPipeError；恢复默认则被 13 号信号杀死。"""
    r, w = os.pipe()
    os.close(r)  # 关掉唯一读端：任何写都应触发 EPIPE
    try:
        try:
            os.write(w, b"x")
            raise AssertionError("已关闭管道的写竟然成功了")
        except BrokenPipeError:
            print("情形 7  Python 写已关闭管道 → BrokenPipeError（解释器启动时"
                  "把 SIGPIPE 置为忽略，所以不死于 141 而是抛异常）")
    finally:
        os.close(w)

    code = textwrap.dedent("""\
        import os, signal
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        r, w = os.pipe()
        os.close(r)
        os.write(w, b"x")
        print("unreachable")
    """)
    p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    print(f"情形 8  恢复 SIGPIPE 默认处理的 Python 子进程 → returncode={p.returncode}"
          "（负号 = 被信号杀死，13 = SIGPIPE）")
    assert p.returncode == -signal.SIGPIPE, f"子进程应死于 SIGPIPE: {p.returncode}"


def selftest(bash):
    print("=== SELFTEST（bash 行为复现，ta 本机）===")
    demo_false_true(bash)
    demo_grep_missing(bash)
    demo_yes_head(bash)
    demo_pipe_capacity()
    demo_python_sigpipe()
    print("SELFTEST PASS：rc=0/PIPESTATUS=(1 0)/pipefail=1；SIGPIPE=141 与 set -e 中止；"
          "保护写法 rc=0；管道容量 65536 B；Python BrokenPipeError 与 SIG_DFL returncode=-13")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="管道退出码 / PIPESTATUS / pipefail 对照表与 SIGPIPE(rc=141) 复现"
                    "（bash 行为复现，非合成样本结果）")
    ap.add_argument("--bash", default=shutil.which("bash") or "/bin/bash",
                    help="用于复现的 bash 路径（默认沿 PATH 查找）")
    ap.add_argument("--selftest", action="store_true",
                    help="断言正文引用的关键数字后退出")
    args = ap.parse_args()

    if args.selftest:
        return selftest(args.bash)
    print(f"使用 bash: {args.bash}\n")
    demo_false_true(args.bash)
    print()
    demo_grep_missing(args.bash)
    print()
    demo_yes_head(args.bash)
    print()
    demo_pipe_capacity()
    print()
    demo_python_sigpipe()
    return 0


if __name__ == "__main__":
    sys.exit(main())

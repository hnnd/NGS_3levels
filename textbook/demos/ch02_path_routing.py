#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ch02_path_routing.py — PATH 路由解析演示：activate 把 bin/ 插到栈顶之后，
which 的解析顺序、版本遮蔽、伪激活与 module 抢占

服务章节：第 2 章 §2.4「概念与方法」本科层（PATH 路由：环境激活的本质是
命令查找顺序的重定向）、§2.5 失效条件第 3 条（command -v 通过而一跑就炸的
排查入口：which/conda list 自检三连）与 u01 ⑥ 6.2 ②「伪激活」机理的复现入口。

数据性质：在临时目录里搭一套**合成迷你文件系统**（工具是只打印自身路径与
版本号的两行 shell 脚本，如 samtools@1.17 与系统版 samtools@0.1.19），
纯属行为复现，不是真实 conda 环境、不是真实工具、不是任何集群实测。
脚本无随机性（固定种子不适用），断言全部为确定性路径解析。

正文引用的输出：
  - 情形 1（合成系统）：未激活任何环境，which samtools → 系统目录
    → activate 前命令查找的基线
  - 情形 2（版本遮蔽）：conda activate ngs_ug_base（把 env bin 插到 PATH 最左）
    → which samtools 命中环境内 1.17，系统 0.1.19 被遮蔽——「激活」的全部物理
    效果就是这一条路由规则（l0_03 §1、u01 §4.4）
  - 情形 3（伪激活）：激活了不含 samtools 的环境（模拟 ngs_ug_annot），
    提示符变了而 which 回落到 /usr/bin → u01 ⑥ 6.2 ② 的机理；
    自检三连：conda list 无此包 + which 路径前缀 ≠ 当前环境 = 拿错工具箱
  - 情形 4（module 抢占）：module 式目录被插到环境 bin **之前**（模拟
    l0_03 错误表末行「module 与 conda 冲突」）→ 环境已激活但 which 仍解析到
    module 目录 → 排错动作 module purge 后再查
  - 情形 5（deactivate）：撤销栈顶插入 → 解析回落系统版
  - 结论：which 是验证激活的唯一黄金标准（l0_03 §1 原文口径）

参数含义：
  --selftest  断言上述各情形解析结果后退出（正文引用前必须保持通过）
  --quiet     只打印 selftest 结论
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile


def sh(cmd, cwd=None):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


class MiniFS:
    """合成迷你文件系统：root 下建 system/bin、module/samtools/1.19/bin、
    envs/<name>/bin 等目录；make_tool 放一个打印自身路径与版本的两行脚本。"""

    def __init__(self, root):
        self.root = root
        self.system_bin = os.path.join(root, "usr", "bin")
        self.envs = os.path.join(root, "d3", "lab", "envs")
        self.module_dir = os.path.join(root, "usr", "local", "module", "samtools",
                                       "1.19", "bin")
        for d in (self.system_bin, self.envs, self.module_dir):
            os.makedirs(d, exist_ok=True)

    def make_tool(self, bindir, name, version):
        path = os.path.join(bindir, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("#!/bin/bash\n"
                     f"echo '{os.path.basename(bindir)}/{name} (合成工具 v{version})'\n")
        os.chmod(path, 0o755)
        return path

    def env_bin(self, env_name):
        d = os.path.join(self.envs, env_name, "bin")
        os.makedirs(d, exist_ok=True)
        return d

    def activate(self, current_path, env_name):
        """conda activate 的合成语义：把 env bin 插到 PATH 最左（l0_03 §1）。"""
        return self.env_bin(env_name) + ":" + current_path

    def deactivate(self, current_path, env_name):
        prefix = self.env_bin(env_name) + ":"
        if current_path.startswith(prefix):
            return current_path[len(prefix):]
        return current_path


def scenario(which_path, tool):
    """在指定 PATH 下解析并「执行」工具，返回 (解析到的路径, 运行输出)。"""
    rc, out, _ = sh(f"PATH='{which_path}' command -v {tool}")
    rc2, out2, _ = sh(f"PATH='{which_path}' {tool}")
    return (out if rc == 0 else None), (out2 if rc2 == 0 else None)


def main():
    ap = argparse.ArgumentParser(
        description="PATH 路由与激活遮蔽的行为复现（合成迷你文件系统）")
    ap.add_argument("--selftest", action="store_true", help="断言关键输出后退出")
    ap.add_argument("--quiet", action="store_true", help="只打印 selftest 结论")
    args = ap.parse_args()
    quiet = args.quiet

    tmp = tempfile.mkdtemp(prefix="ch02_path_demo_")
    ok = True

    def check(cond, msg):
        nonlocal ok
        if not cond:
            ok = False
            print(f"  [FAIL] {msg}", file=sys.stderr)

    try:
        fs = MiniFS(tmp)
        # 合成工具布局：系统版 0.1.19；ngs_ug_base 有 samtools 1.17；
        # ngs_ug_annot（模拟注释环境）不含 samtools；module 目录有一份 1.19
        fs.make_tool(fs.system_bin, "samtools", "0.1.19")
        fs.make_tool(fs.module_dir, "samtools", "1.19")
        base_bin = fs.env_bin("ngs_ug_base")
        fs.make_tool(base_bin, "samtools", "1.17")
        fs.make_tool(base_bin, "fastqc", "0.12.1")
        annot_bin = fs.env_bin("ngs_ug_annot")  # 故意不放 samtools
        base = f"{fs.system_bin}:/usr/local/bin:/usr/bin"

        if not quiet:
            print(f"合成迷你文件系统（临时目录，退出即清理）：\n  {tmp}")
            print("  系统 samtools@0.1.19 ｜ module samtools@1.19 ｜ "
                  "ngs_ug_base/samtools@1.17+fastqc ｜ ngs_ug_annot（无 samtools）\n")

        # 情形 1：未激活基线
        path, ran = scenario(base, "samtools")
        if not quiet:
            print(f"情形 1 未激活：which samtools → {path}")
            print(f"  运行 → {ran}（系统基线版）")
        check(path == os.path.join(fs.system_bin, "samtools"), "基线应解析到系统 bin")

        # 情形 2：activate ngs_ug_base → 版本遮蔽
        p2 = fs.activate(base, "ngs_ug_base")
        path2, ran2 = scenario(p2, "samtools")
        if not quiet:
            print(f"\n情形 2 conda activate ngs_ug_base：which samtools → {path2}")
            print(f"  运行 → {ran2}")
            print("  → 环境 1.17 遮蔽系统 0.1.19；激活的物理效果 = PATH 栈顶插入这一条")
        check(path2 == os.path.join(base_bin, "samtools"),
              "激活后应解析到环境 bin")
        check("1.17" in (ran2 or ""), "运行输出应为环境版 1.17")

        # 情形 3：伪激活（环境里没有该工具，回落系统目录）
        p3 = fs.activate(base, "ngs_ug_annot")
        path3, ran3 = scenario(p3, "samtools")
        installed = os.path.exists(os.path.join(annot_bin, "samtools"))
        if not quiet:
            print(f"\n情形 3 伪激活（激活 ngs_ug_annot，其中没有 samtools）：")
            print(f"  which samtools → {path3}（提示符变了，解析却回落系统目录）")
            print(f"  conda list 等价检查（文件存在？）→ {installed}"
                  " → 自检三连：包不在此环境 = 拿错工具箱（u01 ⑥ 6.2 ②）")
        check(path3 == os.path.join(fs.system_bin, "samtools"),
              "伪激活应回落到系统 bin")
        check(not installed, "ngs_ug_annot 不应含 samtools（合成设定）")

        # 情形 4：module 式目录插到环境 bin 之前（抢占）
        p4 = fs.module_dir + ":" + p2
        path4, ran4 = scenario(p4, "samtools")
        if not quiet:
            print(f"\n情形 4 module 抢占（module 目录被插到环境 bin 之前）：")
            print(f"  which samtools → {path4}")
            print(f"  运行 → {ran4}（环境已激活却仍命中 module 版 → module purge 后排错）")
        check(path4 == os.path.join(fs.module_dir, "samtools"),
              "module 目录在前应被命中")
        check(path4 != path2, "module 抢占后解析路径应与环境激活时不同")

        # 情形 5：deactivate 回落
        p5 = fs.deactivate(p2, "ngs_ug_base")
        path5, _ = scenario(p5, "samtools")
        if not quiet:
            print(f"\n情形 5 deactivate：which samtools → {path5}（撤销栈顶插入，回落系统版）")
        check(path5 == path, "deactivate 后应回到基线路径")

        if args.selftest or quiet:
            status = "PASS" if ok else "FAIL"
            print(f"SELFTEST {status}：基线→系统 bin；activate→环境 1.17 遮蔽；"
                  "伪激活→回落系统 bin；module 在前→module 版抢占；"
                  "deactivate→回落；which 是激活的黄金标准")
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""32_hpc_environment_inheritance.py — FIG-M08-32 HPC 作业环境继承陷阱与三道拦截（P64，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-32（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.5.3（非交互 shell 不读 bashrc，SGE 默认不带环境需 -V，SLURM 需显式指定；
三处置线：脚本自激活 + command -v 自检、引擎 per-rule 环境托管、集群参数显式 -S /bin/bash）。
图内汉字 = 方案原句逐字，共 27 字（作业不继承登录环境 / 脚本自激活自检 /
引擎托管环境 / 非软件未装）；命令与选项用 ASCII。红 1 处标「非软件未装」。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 32_hpc_environment_inheritance.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

GATES = [
    ("bash job.sh", "command -v fastp", "脚本自激活自检", GREEN),
    ("--use-conda", "per-rule env", "引擎托管环境", GREEN),
    ("qsub -S /bin/bash", "explicit shell", "显式 shell", GREEN),
]


def main():
    s = SVG()

    # 上方断裂链：登录 shell 正常 → 作业非交互 → command not found
    s.rect(40, 16, 340, 96, CYAN_TINT, CYAN, 4, rx=12)
    s.text(210, 52, "login shell", 30, CYAN_DEEP, "middle", "bold")
    s.text(210, 94, "conda activate rnaseq", 30, GRAY, "middle")

    s.rect(420, 16, 340, 96, ORANGE_TINT, ORANGE_DEEP, 4, rx=12)
    s.text(590, 52, "batch job", 30, ORANGE_DEEP, "middle", "bold")
    s.text(590, 94, "command not found", 30, ORANGE_DEEP, "middle")

    # 断裂箭头（虚线穿不过去，用叉号标断）
    s.arrow(384, 64, 412, 64, GRAY, 4, 13)
    s.cross(398, 64, 9, RED, 5)
    s.text(400, 146, "作业不继承登录环境", 30, BLUE, "middle", "bold")

    # 下方三道拦截闸门（同一作业依次过闸，任一闸都能立刻暴露问题）
    for i, (head, sub, zh, color) in enumerate(GATES):
        y = 190 + i * 116
        s.rect(60, y, 430, 96, WHITE, color, 4, rx=12)
        s.text(76, y + 42, head, 30, color, "start", "bold")
        s.text(76, y + 80, sub, 30, GRAY, "start")
        s.text(524, y + 56, zh, 30, color, "start", "bold")
        s.arrow(496, y + 48, 512, y + 48, color, 4, 12)

    # 唯一警示：报错不是软件没装，是环境没接上
    s.rect(120, 540, 560, 120, RED_TINT, RED, 5, rx=16)
    s.text(400, 592, "非软件未装", 34, RED, "middle", "bold")
    s.text(400, 634, "PATH mismatch only", 30, RED, "middle")

    return s.save("32_hpc_environment_inheritance.svg")


if __name__ == "__main__":
    raise SystemExit(main())

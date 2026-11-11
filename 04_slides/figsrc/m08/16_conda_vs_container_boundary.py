#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_conda_vs_container_boundary.py — FIG-M08-16 Conda 与容器的隔离层级对照（P35，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-16（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.4（conda 换解释器与用户态依赖包，glibc 仍链接宿主；
容器把除内核以外的整段用户态换掉；两者共享宿主内核）。
图内汉字 = 方案原句逐字，共 27 字（Conda 换解释器与库 / 依赖宿主系统库 /
容器换整段用户态 / 宿主内核共享）；末尾层名用 ASCII。
版式：上排两栏卡片 → 中间「宿主内核共享」长条 → 下排语义标签（标签不压连接线）。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 16_conda_vs_container_boundary.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402


def main():
    s = SVG()

    # 左栏（conda）：只换用户态解释器与包，glibc 仍是宿主的
    s.rect(40, 88, 336, 120, CYAN_TINT, CYAN, 4, rx=12)
    s.text(208, 158, "python / fastp / libs", 30, CYAN_DEEP, "middle")
    s.rect(40, 228, 336, 120, ORANGE_TINT, ORANGE_DEEP, 4, rx=12)
    s.text(208, 298, "glibc 2.18 (host)", 30, ORANGE_DEEP, "middle")

    # 右栏（容器）：整段根文件系统一起换，glibc 随镜像进来
    s.rect(424, 88, 336, 260, PURPLE_TINT, PURPLE, 4, rx=12)
    s.label(592, 222, ["rootfs", "glibc 2.35", "toolchain"], 30, BLUE,
            "middle", leading=1.55)

    # 中间：共享宿主内核（深蓝长条，跨两栏）
    s.rect(40, 388, 720, 96, BLUE, rx=14)
    s.text(400, 450, "宿主内核共享", 34, WHITE, "middle", "bold")

    # 两栏向内核收拢的细线（只在卡片与长条之间的空档里）
    for x in (60, 700):
        s.line(x, 356, x, 384, BLUE, 3, dash="10 8")

    # 下排语义标签（放在长条下方，不与任何线相交）
    s.text(208, 548, "Conda 换解释器与库", 30, BLUE, "middle", "bold")
    s.text(208, 608, "依赖宿主系统库", 30, RED, "middle", "bold")
    s.text(592, 548, "容器换整段用户态", 30, BLUE, "middle", "bold")

    return s.save("16_conda_vs_container_boundary.svg")


if __name__ == "__main__":
    raise SystemExit(main())

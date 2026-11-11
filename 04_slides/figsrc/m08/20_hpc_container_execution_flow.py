#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_hpc_container_execution_flow.py — FIG-M08-20 HPC 容器运行分工流（P39，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-20（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.4 与根 CLAUDE.md 集群事实（计算节点无公网：镜像只在登录节点拉取，
经共享存储落到计算节点本地运行；作业内不联网）。
图内汉字 = 方案原句逐字，共 30 字（登录节点联网拉取 / 共享存储落盘缓存 /
计算节点离线运行 / 严禁节点联网）；节点名、命令与文件名用 ASCII。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 20_hpc_container_execution_flow.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402


def main():
    s = SVG()

    # ① 登录节点（有公网）
    s.rect(56, 24, 690, 132, CYAN_TINT, CYAN, 4, rx=14)
    s.text(400, 64, "login node", 30, CYAN_DEEP, "middle", "bold")
    s.text(400, 104, "apptainer pull docker://quay.io/...", 30, GRAY, "middle")
    s.text(400, 142, "登录节点联网拉取", 30, BLUE, "middle", "bold")
    # 箭头走在两卡之间的窄缝（避开标签）
    s.arrow(400, 162, 400, 196, CYAN, 6, 16)

    # ② 共享存储：.sif 落盘
    s.rect(56, 202, 690, 116, WHITE, BLUE, 4, rx=14)
    s.text(400, 246, "/shared/containers/fastp_0.23.4.sif", 30, BLUE, "middle")
    s.text(400, 300, "共享存储落盘缓存", 30, BLUE, "middle", "bold")
    s.arrow(400, 322, 400, 356, CYAN, 6, 16)

    # ③ 计算节点（无公网，离线运行）
    s.rect(56, 362, 690, 150, GREEN_TINT, GREEN, 4, rx=14)
    s.text(400, 406, "compute node", 30, GREEN, "middle", "bold")
    s.text(400, 446, "apptainer exec fastp_0.23.4.sif", 30, GRAY, "middle")
    s.text(400, 486, "计算节点离线运行", 30, GREEN, "middle", "bold")

    # ④ 红色警示：作业内不得联网（唯一警示）
    s.rect(210, 544, 380, 84, RED_TINT, RED, 5, rx=14)
    s.text(400, 596, "严禁节点联网", 34, RED, "middle", "bold")

    return s.save("20_hpc_container_execution_flow.svg")


if __name__ == "__main__":
    raise SystemExit(main())

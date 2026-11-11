#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""25_cluster_two_stage_dispatch.py — FIG-M08-25 两阶段集群作业派发流程（P50，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-25（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.5.3（登录节点联网预建 per-rule 环境缓存，再派发到计算节点池；计算节点无公网）。
图内汉字 = 方案原句逐字，共 28 字（登录节点预建环境 / 显式声明一核 /
集群派发计算池 / 计算节点无外网）；命令与节点名用 ASCII。红 1 处标「计算节点无外网」。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 25_cluster_two_stage_dispatch.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

POOL = [("job 1", 84), ("job 2", 220), ("job 3", 356), ("job ...", 492)]


def main():
    s = SVG()

    # ① 登录节点：联网预建 per-rule 环境缓存（显式一核，避免并发抢带宽）
    s.rect(40, 24, 720, 184, CYAN_TINT, CYAN, 4, rx=14)
    s.text(400, 64, "login node", 30, CYAN_DEEP, "middle", "bold")
    s.text(400, 108,
           "--conda-create-envs-only -c 1", 30, GRAY, "middle")
    s.text(400, 156, "登录节点预建环境", 30, BLUE, "middle", "bold")
    s.text(400, 192, "显式声明一核", 30, BLUE, "middle", "bold")

    # 中间窄缝：派发箭头
    s.arrow(400, 216, 400, 250, CYAN, 6, 16)

    # ② 计算节点池：四格作业并发（绿色）
    s.rect(40, 258, 720, 290, WHITE, GREEN, 4, rx=14)
    s.text(400, 300, "--use-conda -j 50", 30, GREEN, "middle", "bold")
    s.text(400, 338, '--cluster "qsub -V -cwd -S /bin/bash"', 30, GRAY, "middle")
    for name, x in POOL:
        s.rect(x, 362, 124, 100, GREEN_TINT, GREEN, 3, rx=12)
        s.text(x + 62, 420, name, 30, GREEN, "middle", "bold")
    s.text(400, 506, "集群派发计算池", 30, GREEN, "middle", "bold")

    # ③ 唯一警示：计算节点不联网
    s.rect(190, 584, 420, 92, RED_TINT, RED, 5, rx=14)
    s.text(400, 640, "计算节点无外网", 34, RED, "middle", "bold")

    return s.save("25_cluster_two_stage_dispatch.svg")


if __name__ == "__main__":
    raise SystemExit(main())

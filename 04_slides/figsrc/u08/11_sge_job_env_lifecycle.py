#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_sge_job_env_lifecycle.py — 生成 11_sge_job_env_lifecycle.svg（FIG-U08-11：
SGE 非交互作业环境生命周期）

方案：reviews/course/U08_FIGP_001.md §4 FIG-U08-11（P30，cols 一栏，800×700）。
事实：登录节点交互 shell 已加载 ~/.bashrc（绿）；SGE 投递的计算节点跑非交互
子 shell，干净环境不读 ~/.bashrc（橙）；作业脚本必须先 source 再 conda activate
（红桥＝唯一红，讲义 ⑤ 5.0、⑨ E2、手册 §3.2、根 CLAUDE.md 集群事实）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 11_sge_job_env_lifecycle.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 左主机：登录环境（绿）
    s.rect(30, 110, 340, 250, GREEN_TINT, GREEN, 5, rx=16)
    s.text(200, 168, "登录环境：交互已加载", 32, GREEN, "middle", "bold")
    s.text(200, 232, "$ ssh cluster", 30, INK, "middle")
    s.text(200, 278, "interactive bash", 30, INK, "middle")
    s.text(200, 324, "~/.bashrc  ✓", 30, INK, "middle")

    # 右主机：SGE 计算节点（橙）
    s.rect(430, 110, 340, 250, "#FBE5DC", ORANGE, 5, rx=16)
    s.text(600, 158, "SGE 作业：", 32, "#C96432", "middle", "bold")
    s.text(600, 198, "非交互干净环境", 32, "#C96432", "middle", "bold")
    s.text(600, 254, "$ qsub job.sh", 30, INK, "middle")
    s.text(600, 300, "non-interactive shell", 30, INK, "middle")
    s.text(600, 346, "no ~/.bashrc  ×", 30, INK, "middle")

    # 两侧汇入红色指令桥（唯一红）
    s.arrow(200, 360, 200, 402, GRAY, 6)
    s.arrow(600, 360, 600, 402, GRAY, 6)
    s.rect(50, 406, 700, 76, RED, rx=14)
    s.text(400, 442, "必须先 source 再 activate", 34, WHITE, "middle",
           "bold")

    # 代码卡（白底）
    s.rect(100, 516, 600, 116, WHITE, INK, 3, rx=12)
    s.text(130, 566, "source /opt/miniconda3/bin/activate", 30, INK, "start")
    s.text(130, 610, "conda activate ngs_ug_assembly", 30, INK, "start")

    s.save("11_sge_job_env_lifecycle.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""24_reverse_derivation_experiment.py — FIG-M08-24 删中间产物逆向推演验证（P49，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-24（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.2（默认目标齐全时引擎不检查中间产物，报 Nothing to be done；
点名目标才逆向展开，只重跑该分支）；实验指导步骤 6 A1/A2。
图内汉字 = 方案原句逐字，共 27 字（删中间产物默认不重跑 / 终点齐全判定完成 /
点名目标才逆向触发）；命令与文件名用 ASCII。红 1 处标「默认不重跑」。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 24_reverse_derivation_experiment.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402


def main():
    s = SVG()

    # 共同前提：删掉中间产物（两分支由此分叉）
    s.rect(60, 24, 680, 88, PANEL, rx=14)
    s.text(400, 78, "rm results/quant/CK_1/quant.sf", 30, INK, "middle", "bold")

    # 上分支：默认目标 rule all → 终点齐全 → Nothing to be done（红＝易错）
    s.arrow(214, 122, 214, 162, CYAN, 5, 14)
    s.text(214, 200, "终点齐全判定完成", 30, BLUE, "middle", "bold")
    s.rect(40, 226, 348, 230, RED_TINT, RED, 5, rx=16)
    s.text(214, 296, "snakemake -n", 30, RED, "middle")
    s.text(214, 360, "Nothing to be done", 30, RED, "middle", "bold")
    s.text(214, 416, "删中间产物默认不重跑", 30, RED, "middle", "bold")

    # 下分支：点名目标 → 逆向展开 → 只重跑该分支（绿）
    s.arrow(586, 122, 586, 162, CYAN, 5, 14)
    s.text(586, 200, "点名目标才逆向触发", 30, GREEN, "middle", "bold")
    s.rect(412, 226, 348, 230, GREEN_TINT, GREEN, 4, rx=16)
    s.text(586, 302, "snakemake -n quant.sf", 30, GREEN, "middle")
    s.text(586, 392, "1 job (rebuild)", 30, GREEN, "middle", "bold")


    # 绿分支的补充注记（贴在其结果框下沿）
    s.text(586, 502, "missing input", 30, GRAY, "middle")

    return s.save("24_reverse_derivation_experiment.svg")


if __name__ == "__main__":
    raise SystemExit(main())

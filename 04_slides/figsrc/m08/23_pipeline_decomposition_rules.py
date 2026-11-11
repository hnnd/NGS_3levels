#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""23_pipeline_decomposition_rules.py — FIG-M08-23 单体脚本拆为四规则流水线（P47，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-23（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.4（每条规则一个环境：qc / quant / report；换 fastp 版本不牵动 salmon 求解；
salmon 1.10.0–1.10.2 要求 icu 69 而 r-base 4.3.1 要求 72 以上，只有钉到 1.10.3 才能共存）。
图内汉字 = 方案原句逐字，共 28 字（单体脚本拆为四规则 / 首尾相接流水线 /
每规则独立环境 / 防版本冲突）；规则名与文件名用 ASCII。红 1 处标「防版本冲突」。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 23_pipeline_decomposition_rules.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

# (规则名, 环境文件, y)
RULES = [("fastp", "envs/qc.yaml", 84),
         ("salmon_index", "envs/quant.yaml", 178),
         ("salmon_quant", "envs/quant.yaml", 272),
         ("merge_counts", "envs/report.yaml", 366)]
RX, RW = 48, 344          # 规则卡
EX, EW = 424, 328         # 环境卡
CH = 74                   # 卡高


def main():
    s = SVG()

    s.text(400, 54, "单体脚本拆为四规则", 34, BLUE, "middle", "bold")

    for i, (rule, env, y) in enumerate(RULES):
        s.rect(RX, y, RW, CH, BLUE_TINT, BLUE, 4, rx=12)
        s.text(RX + RW / 2, y + 48, rule, 30, BLUE, "middle", "bold")
        s.rect(EX, y, EW, CH, GREEN_TINT, GREEN, 4, rx=12)
        s.text(EX + EW / 2, y + 48, env, 30, GREEN, "middle")
        s.line(RX + RW + 4, y + CH / 2, EX - 6, y + CH / 2, GREEN, 3)
        if i:
            s.arrow(RX + 52, RULES[i - 1][2] + CH + 1, RX + 52, y - 3,
                    CYAN, 5, 12)

    # 两条语义注记（分别在下属列的正下方）
    s.text(RX + RW / 2, 470, "首尾相接流水线", 30, BLUE, "middle", "bold")
    s.text(EX + EW / 2, 470, "每规则独立环境", 30, GREEN, "middle", "bold")

    # 底部唯一警示：防版本冲突
    s.rect(140, 508, 520, 96, RED_TINT, RED, 5, rx=16)
    s.text(400, 566, "防版本冲突", 36, RED, "middle", "bold")

    return s.save("23_pipeline_decomposition_rules.svg")


if __name__ == "__main__":
    raise SystemExit(main())

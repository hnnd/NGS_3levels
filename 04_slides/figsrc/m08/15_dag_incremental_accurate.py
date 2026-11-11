#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_dag_incremental_accurate.py — FIG-M08-15 四样本增量 DAG 精准重跑推演（P34，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-15（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.3（改 CK_1 输入后：fastp(CK_1) → salmon_quant(CK_1) → merge_counts →
report 重跑；CK_2、TR_1、TR_2 与参考索引命中缓存；reason 为 Updated input files）。
本图替换讲义旧图 `01_dag_incremental.svg`（教材标 hold_redraw），按 7.28.1 触发机制绘制。
图内汉字 = 方案原句逐字，共 26 字（输入更新仅单路重算 / 未变样本全命中缓存 /
下游汇总级联更新）；其余只有 ASCII 规则名与样本名。无红色（正常增量重跑行为）。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 15_dag_incremental_accurate.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

CHAIN = [(214, "fastp CK_1"), (300, "quant CK_1"), (386, "merge_counts")]


def main():
    s = SVG()

    s.text(400, 44, "输入更新仅单路重算", 34, BLUE, "middle", "bold")

    # 上游触发点（改动的输入，橙）
    s.rect(40, 88, 300, 96, ORANGE_TINT, ORANGE_DEEP, 4, rx=12)
    s.text(190, 130, "CK_1 输入更新", 30, ORANGE_DEEP, "middle", "bold")
    s.text(190, 166, "reason: Updated", 30, GRAY, "middle")
    s.arrow(190, 184, 190, 210, CYAN, 5, 14)

    # 左：单路级联（橙 = 重跑）
    for i, (y, label) in enumerate(CHAIN):
        s.rect(40, y, 300, 68, ORANGE_TINT, ORANGE_DEEP, 4, rx=12)
        s.text(190, y + 43, label, 30, ORANGE_DEEP, "middle", "bold")
        if i:
            s.arrow(190, CHAIN[i - 1][0] + 70, 190, y - 6, CYAN, 5, 14)

    # 右：未变分支（绿 = 缓存命中），三行折行避免出卡
    s.rect(372, 88, 410, 366, GREEN_TINT, GREEN, 4, rx=16)
    s.label(577, 146, ["未变样本", "全命中缓存"], 30, GREEN, "middle",
            "bold", 1.3)
    s.label(577, 300, ["fastp CK_2 / TR_1 / TR_2", "salmon_index",
                       "quant CK_2 / TR_1 / TR_2"], 30, INK, "middle",
            leading=1.7)

    # 结尾：report 更新（橙，级联）
    s.rect(40, 486, 742, 92, WHITE, ORANGE, 4, rx=14)
    s.text(411, 543, "下游汇总级联更新", 32, ORANGE_DEEP, "middle", "bold")
    s.arrow(190, 456, 190, 482, CYAN, 5, 14)

    return s.save("15_dag_incremental_accurate.svg")


if __name__ == "__main__":
    raise SystemExit(main())

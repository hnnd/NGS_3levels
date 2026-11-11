#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_atomic_step_contract.py — 生成 04_atomic_step_contract.svg
（FIG-P01-05：原子步骤三要素契约）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-05（P20，cols 一栏，800×700）。
依据：教材 §24.4.3 三要素表（输入契约 / 输出判据 / 生物学前置）与「三要素里最
容易被跳过的是输出判据，而它是唯一能自动判对错的部分」；讲义 ④4.1。卡片示例
（2 000 行 × 6 列整数 counts、`padj` 与 `log2FC` 列、recall ≥ 18/20、cor ≈ −1、
2 组 × 3 重复、batch 与 condition 交叉、参考水平 ctrl）逐项取自教材 §24.4.3 同一
张表与 §24.4.4 的判据，不新增数字。
图内中文只有底部方案整句（28 汉字）；三层卡片标题与条目用英文术语 + 具体字段名，
既与讲义代码块同词，也把汉字配额留给结论句。纯示意，无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 04_atomic_step_contract.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "需求拆解三要素：输入契约定量纲，输出判据给断言，生物前置定设计。"
ROWS = [
    ("INPUT", "format · dim · unit",
     ["2 000 × 6, integer_counts", "coldata: 3 columns, same_order"],
     CYAN, "#E7F5F8"),
    ("OUTPUT", "names + machine_asserts",
     ["columns padj / log2FC present", "recall ≥ 18/20, cor ≈ −1"],
     RED, RED_TINT),
    ("DESIGN", "species · reps · batch · ref",
     ["2 groups × 3 biological_reps", "batch_crossed_with_condition"],
     BLUE, BLUE_TINT),
]


def main():
    s = SVG(800, 700, "Atomic step contract: three elements", plan=TEXT)

    for i, (head, sub, lines, edge, tint) in enumerate(ROWS):
        y = 26 + i * 156
        s.rect(40, y, 720, 138, tint, edge, 4, rx=12)
        s.rect(40, y, 10, 138, edge)
        s.text(74, y + 46, head, 32, edge, "start", "bold")
        s.text(736, y + 46, sub, 30, GRAY, "end")
        for j, ln in enumerate(lines):
            s.text(74, y + 92 + j * 38, ln, 30, INK)

    s.caption(["需求拆解三要素：输入契约定量纲，",
               "输出判据给断言，生物前置定设计。"], [INK, INK], 30,
              top=520, gap=44, pad_top=16)
    s.save("04_atomic_step_contract.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_silent_errors_part1.py — 生成 05_silent_errors_part1.svg
（FIG-P01-06：前三类静默语义错误）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-06（P23，cols 一栏，800×700）。
依据：教材 §24.4.2 表 24-1 序号 1–3（统计量误用 / 方向反转 / 单位混淆）与
「代码正常退出、结果表正常生成，错误只体现在数值的含义上」。
右侧三列数字全部来自 demos 现跑（回执列核对表）：
  ① FP 1 → 94：demos/ch24_pvalue_vs_padj.py --selftest 部分 B——padj<0.05 里
     混入 1 个空假设，pvalue<0.05 里 94 个；
  ② TP 0/20：demos/ch24_label_swap_mirror.py --selftest 部分 B——方向写反时
     上调侧命中 0/20；
  ③ SF 1.03×：demos/ch24_double_normalization_sizefactors.py --selftest 部分 B
     ——CPM 后又取整，size factor 散布仅 1.03×。
图内中文只有底部方案整句（28 汉字）；三行错误名用代码术语本身（与讲义代码块
同词），汉字配额全部留给结论句。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 05_silent_errors_part1.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "静默错误一：筛选列误用、方向反转、双重归一化。正常退出但语义全错。"
ROWS = [
    ("1", ["padj  →  pvalue", "wrong_column"], "FP  1 → 94"),
    ("2", ["contrast: swap 2 / 3", "wrong_direction"], "TP  0 / 20"),
    ("3", ["round(CPM) as counts", "double_normalization"], "SF  1.03 X"),
]


def main():
    s = SVG(800, 700, "Silent semantic errors, part 1", plan=TEXT)
    s.text(150, 62, "code", 30, GRAY)
    s.text(736, 62, "output", 30, GRAY, "end")

    for i, (no, labels, num) in enumerate(ROWS):
        y = 78 + i * 132
        s.rect(40, y, 720, 118, WHITE, BLUE, 4, rx=12)
        s.badge(66, y + 59, no, BLUE, WHITE, 30, "start")
        s.text(132, y + 52, labels[0], 32, INK, "start", "bold")
        s.text(132, y + 92, labels[1], 30, GRAY)
        s.text(736, y + 66, num, 32, BLUE, "end", "bold")

    # 三行共同点：进程与产物都正常（唯一红条）
    s.rect(40, 470, 720, 62, RED_TINT, RED, 4, rx=10)
    s.text(400, 510, "exit 0  ·  tables_and_plots_look_fine", 30, RED,
           "middle", "bold")

    s.caption(["静默错误一：筛选列误用、方向反转、",
               "双重归一化。正常退出但语义全错。"], [INK, INK], 30,
              top=548, gap=44, pad_top=14)
    s.save("05_silent_errors_part1.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())

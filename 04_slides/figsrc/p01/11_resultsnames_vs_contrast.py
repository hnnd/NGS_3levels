#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_resultsnames_vs_contrast.py — 生成 11_resultsnames_vs_contrast.svg
（FIG-P01-12：第 ③ 步对比字面核对陷阱）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-12（P35，cols 一栏，800×700）。
依据：教材 §24.4.4 第 ③ 步与讲义 ⑥6.2 第 2 行——`resultsNames(dds)` 的系数名
`condition_treat_vs_ctrl` 由设计式决定（treat 对 ctrl），而 `results(dds,
contrast=...)` 的方向由实参三元组的元素顺序决定；把 ctrl 写第二位、treat 写第三
位，等于 log2(ctrl/treat)，全表符号整体翻转。两者字面都合法，方向却相反。
图内不写任何数值：符号翻转用 `lfc` 与 `-lfc` 表达，避免出现无法追溯到 demos 的
数字（教材此处也只给机制）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 11_resultsnames_vs_contrast.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "字面相同不等于方向相同。系数名由设计式生成，对比参数反转方向。"
ARGS = ["condition", "ctrl", "treat"]


def main():
    s = SVG(800, 700, "resultsNames vs contrast argument order", plan=TEXT)

    # ---------- 上：设计式产物（系数名，青蓝）----------
    s.rect(40, 44, 720, 128, "#E7F5F8", CYAN, 4, rx=12)
    s.text(64, 90, "resultsNames", 30, CYAN_DEEP, "start", "bold")
    s.chip(64, 138, "condition_treat_vs_ctrl", 30, WHITE, CYAN, INK,
           anchor="start", h=54)
    s.check(724, 138, 16, GREEN, 7)

    # ---------- 中：调用实参（深蓝），元素顺序即方向 ----------
    s.rect(40, 190, 720, 214, BLUE_TINT, BLUE, 4, rx=12)
    s.text(64, 236, "contrast", 32, BLUE, "start", "bold")
    for i, a in enumerate(ARGS):
        # 芯片下移到 306，序号上留一行空隙：原 296 时序号基线 268 的
        # 字框底（275）会压住芯片上边框（269）
        s.chip(64 + i * 236, 306, f'"{a}"', 30, WHITE, BLUE, INK,
               anchor="start", h=54)
        s.text(64 + i * 236, 268, str(i + 1), 30, GRAY, "start", "bold")
    # 第 2 元素成为分子、第 3 元素成为分母（红：方向被实参改写）
    s.circle(348, 346, 7, RED)
    s.circle(584, 346, 7, RED)
    s.line(348, 346, 584, 346, RED, 3, dash="8 7")
    s.text(466, 390, "2nd = numerator", 30, RED, "middle", "bold")

    # ---------- 下：全表符号整体翻转 ----------
    s.rect(40, 418, 720, 106, WHITE, GRAY, 3, rx=12)
    s.text(76, 484, "treat_vs_ctrl", 30, INK)
    s.arrow(298, 480, 380, 480, RED, 5, 13)
    s.text(400, 484, "lfc  →  -lfc", 32, RED, "start", "bold")

    s.caption(["字面相同不等于方向相同。",
               "系数名由设计式生成，对比参数反转方向。"], [INK, INK], 30,
              top=546, gap=44, pad_top=16)
    s.save("11_resultsnames_vs_contrast.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())

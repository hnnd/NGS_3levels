#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_pseudobulk_four_details.py — 生成 15_pseudobulk_four_details.svg
（FIG-P02-18：pseudobulk 聚合的四个工程细节）

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-18（Slide 38，cols 一栏，800×700）。
依据：教材 §17.4.9 L215–227；`02_pseudobulk_de.R` 的聚合口径（按样本×类型
原始计数求和、整数断言、≥10 细胞下限、检验前回 RNA assay）。纯示意：
无数据、无随机数、无网络；代码片段为教材同款写法。
图内汉字 = 方案指定整句逐字一致（30 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 15_pseudobulk_four_details.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "按样本类型原始计数直接求和。严禁取平均引入浮点，整数断言守护检验。"


def card(s, x, y, head, color, tint):
    s.rect(x, y, 340, 180, tint, color, 4, rx=12)
    s.text(x + 20, y + 50, head, 32, color, "start", "bold")


def main():
    s = SVG(800, 700, "Four pseudobulk engineering details", plan=TEXT)

    # ① 求和，不取平均
    card(s, 40, 60, "SUM", GREEN, GREEN_TINT)
    s.text(60, 164, "Σ counts", 32, INK, "start", "bold")
    s.text(60, 212, "≠ AVG", 32, GRAY, "start", "bold")
    s.cross(238, 200, 17, RED, 8)          # 红色（唯一警示区）：取平均引入浮点
    s.text(266, 212, "FLOAT", 30, RED, "start", "bold")

    # ② 整数断言
    card(s, 420, 60, "ASSERT", GREEN, GREEN_TINT)
    s.text(440, 164, "pb % 1 == 0", 32, INK, "start")
    s.check(470, 212, 20, GREEN, 7)

    # ③ 每类型每样本至少 10 个细胞
    card(s, 40, 280, "MIN CELLS", BLUE, BLUE_TINT)
    for j, h in enumerate((26, 44, 64, 84)):
        s.rect(70 + j * 52, 428 - h, 38, h, CYAN)
    s.line(62, 428, 268, 428, INK, 3)
    s.text(300, 424, "10", 34, BLUE, "middle", "bold")

    # ④ 检验前把 Assay 切回 RNA
    card(s, 420, 280, "ASSAY", BLUE, BLUE_TINT)
    s.text(440, 386, "DefaultAssay", 32, INK, "start")
    s.text(440, 434, '"RNA"', 32, BLUE, "start", "bold")

    s.caption(["按样本类型原始计数直接求和。",
               "严禁取平均引入浮点，整数断言守护检验。"], [INK, INK], 30,
              top=500)
    s.save("15_pseudobulk_four_details.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())

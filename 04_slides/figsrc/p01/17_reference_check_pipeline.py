#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_reference_check_pipeline.py — 生成 17_reference_check_pipeline.svg
（FIG-P01-18：文献四步核查流水线）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-18（P45，cols 一栏，800×700）。
依据：教材 §24.4.7 的四步核查（FT24-01）——① 用 `curl -sI` 解析 DOI，看返回
301/302 还是 404；② 抓 Crossref REST 元数据，把篇名/作者/卷期页逐字段比对；
③ 用 PubMed `esearch` 反查命中数；④ 人工读摘要，确认文献真的支持该论断。
前三步可脚本化（`03_code/phd/scripts/01_check_refs.sh`），第 ④ 步没有脚本。
图中只有步骤名、判据词与状态色：①②③ 青蓝（自动化），④ 红色（必须人工）。
无网络、无随机数（本图不引任何 DOI 或文献号码）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 17_reference_check_pipeline.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "文献四步核查：解析、抓元数据、反查文献库、人工读摘要。前三步脚本化。"
STEPS = [
    ("1", "resolve", "301 / 302  vs  404", CYAN, "#E7F5F8"),
    ("2", "metadata", "title · author · vol", CYAN, "#E7F5F8"),
    ("3", "esearch", "hit_count", CYAN, "#E7F5F8"),
    ("4", "read_abstract", "supports_the_claim?", RED, RED_TINT),
]


def main():
    s = SVG(800, 700, "Four-step reference verification pipeline", plan=TEXT)

    # 纵向四步管道（每步一行，宽度相同，右侧标判据）
    for i, (no, name, crit, edge, tint) in enumerate(STEPS):
        y = 30 + i * 112
        s.rect(40, y, 720, 96, tint, edge, 5 if i == 3 else 3, rx=12)
        s.badge(62, y + 48, no, edge, WHITE, 30, "start")
        s.text(118, y + 60, name, 32, edge, "start", "bold")
        s.text(736, y + 60, crit, 30, INK, "end")

    # 前三步的脚本括号 + 第四步人工
    s.bracket(40, 472, 420, 498, BLUE, 5)
    s.text(230, 534, "scripted  ① ② ③", 30, BLUE, "middle", "bold")
    s.bracket(452, 472, 760, 498, RED, 5)
    s.text(606, 534, "manual  ④", 30, RED, "middle", "bold")

    s.caption(["文献四步核查：解析、抓元数据、",
               "反查文献库、人工读摘要。前三步脚本化。"], [INK, INK], 30,
              top=556, gap=44, pad_top=12)
    s.save("17_reference_check_pipeline.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())

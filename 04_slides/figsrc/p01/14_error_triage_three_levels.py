#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_error_triage_three_levels.py — 生成 14_error_triage_three_levels.svg
（FIG-P01-15：报错三分法与危险度分层）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-15（P41，cols 一栏，800×700）。
依据：教材 §24.4.6 报错三分法——
  环境层（换机器就消失，典型 `command not found`，AI 装包建议通常可信，低危）；
  数据层（换输入就消失，典型 `not integers` / `NAs`；AI 建议 round()/na.omit()
    等于抹杀诊断线索，高危）；
  逻辑层（换环境、换数据都在，典型 `the model matrix is not full rank`；AI 建议
    删 batch 会把完全混杂永久藏进处理效应，最高危）。
三层自上而下阶梯右移、逐层加长、描边逐层加粗，表达危险度递增；右侧只有方向
箭头，无任何数值刻度（本图不引数字）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 14_error_triage_three_levels.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "报错三分法：环境层低危，数据层高危抹杀线索，逻辑层最高危掩盖混杂。"
TIERS = [
    (36, 44, 480, "env", "command_not_found", "switch_machine → gone",
     GREEN, GREEN_TINT, 3),
    (60, 176, 540, "data", "not integers / NAs", "switch_input → gone",
     ORANGE, ORANGE_TINT, 6),
    (84, 308, 600, "logic", "not_full_rank", "still_there",
     RED, RED_TINT, 9),
]


def main():
    s = SVG(800, 700, "Error triage: three levels of danger", plan=TEXT)

    for x, y, w, name, msg, why, edge, tint, sw in TIERS:
        s.rect(x, y, w, 118, tint, edge, sw, rx=12)
        s.text(x + 26, y + 46, name, 32, edge, "start", "bold")
        s.text(x + w - 26, y + 46, why, 30, GRAY, "end")
        s.text(x + 26, y + 98, msg, 30, INK)

    # 危险度递增（只有方向，无刻度）
    s.arrow(754, 74, 754, 400, GRAY, 4, 14)
    s.text(754, 434, "high", 30, RED, "middle", "bold")

    s.caption(["报错三分法：环境层低危，",
               "数据层高危抹杀线索，",
               "逻辑层最高危掩盖混杂。"], [INK, INK, INK], 30,
              top=470, gap=42, pad_top=14)
    s.save("14_error_triage_three_levels.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())

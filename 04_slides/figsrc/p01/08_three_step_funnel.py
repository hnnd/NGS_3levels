#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_three_step_funnel.py — 生成 08_three_step_funnel.svg
（FIG-P01-09：三步验证法防御梯队漏斗）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-09（P27，cols 一栏，800×700）。
依据：教材 §24.4.4 三步验证法表——① 维度与语义自检「永远做」→ ② 已知答案回归
测试（三步里唯一靠数值响应抓「方向反了」的一步）→ ③ 关键中间量手算复核「只对
要写进论文的数字做」；各步「查不出什么」一列见同表。
方案对时间口径（「约半小时」「40 分钟」）本轮一律不采用，图内不写任何时间数字；
排查成本与覆盖颗粒度只用箭头方向表达，无刻度、无数值。
配色：深蓝顶层、红色中层（唯一红区，凸显无症状错误的唯一抓手）、青蓝底层。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 08_three_step_funnel.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "三步验证法：自检查格式，回归测答案，手算核中间量。第二步抓无症状。"
TIERS = [
    ("1", "self-check", "dim · type · names · order", BLUE, BLUE_TINT, 660, 4),
    ("2", "regression", "recall · mirror r", RED, RED_TINT, 596, 6),
    ("3", "hand-calc", "resultsNames · BH · CPM", CYAN, "#E7F5F8", 532, 4),
]


def main():
    s = SVG(800, 700, "Three-step verification funnel", plan=TEXT)

    for i, (no, head, detail, edge, tint, w, sw) in enumerate(TIERS):
        y = 62 + i * 136
        s.rect(88, y, w, 118, tint, edge, sw, rx=12)
        s.badge(116, y + 59, no, edge, WHITE, 32, "start")
        s.text(178, y + 52, head, 32, edge, "start", "bold")
        s.text(178, y + 96, detail, 30, INK)

    # 右侧标尺：排查成本沿阶梯升高（只有方向，无刻度、无文字）
    s.arrow(760, 150, 760, 470, GRAY, 4, 12)

    # 第 ② 层：无症状错误的唯一数值抓手（0/20 取自 demos 现跑，见回执核对表）
    s.text(660, 268, "0/20", 30, RED, "end", "bold")

    s.caption(["三步验证法：自检查格式，回归测答案，",
               "手算核中间量。",
               "第二步抓无症状。"], [INK, INK, RED], 30,
              top=486, gap=42, pad_top=14)
    s.save("08_three_step_funnel.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())

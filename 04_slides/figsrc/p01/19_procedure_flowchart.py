#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_procedure_flowchart.py — 生成 19_procedure_flowchart.svg
（FIG-P01-20：实践操作四步流水线骨架）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-20（P50，cols 一栏，800×700）。
依据：讲义 ⑤ 全节与教材 §24.4.4、§24.4.7 的实验骨架——
  ① `01_make_spikein_counts.R` 生产已知答案三件套（counts / coldata / spikein）；
  ② `01_ai_generated_de.R` 让 AI 生成的代码在数据上跑出表与图；
  ③ `01_verify_de.R` 执行三步验证法并输出对账报告；
  ④ `01_check_refs.sh` 走文献四步核查。
脚本名与讲义一致（已在讲义 ⑤ 引用），图内不写任何数值与 DOI。
红色 1 处标第 ③ 步对账拦截。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 19_procedure_flowchart.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "实践四步流程：造已知答案，智能体执行分析，三步验证对账，批量核查引用。"
STEPS = [
    ("1", "make_answers", "01_make_spikein_counts.R", BLUE, BLUE_TINT),
    ("2", "run AI code", "01_ai_generated_de.R", BLUE, BLUE_TINT),
    ("3", "verify", "01_verify_de.R", RED, RED_TINT),
    ("4", "check_refs", "01_check_refs.sh", BLUE, BLUE_TINT),
]


def main():
    s = SVG(800, 700, "Four-step practice pipeline", plan=TEXT)

    for i, (no, head, script, edge, tint) in enumerate(STEPS):
        y = 40 + i * 124
        s.rect(40, y, 720, 100, tint, edge, 5 if i == 2 else 3, rx=12)
        s.badge(68, y + 50, no, edge, WHITE, 32, "start")
        s.text(126, y + 38, head, 32, edge, "start", "bold")
        s.text(126, y + 80, script, 30, INK)
        if i < 3:
            s.arrow(400, y + 102, 400, y + 118, GRAY, 4, 11)

    # 第 ③ 步的拦截位置：验证对账把前面两步的产物过一遍（唯一红）
    s.rect(40, 288, 720, 100, "none", RED, 4, rx=12, dash="10 8")
    s.text(740, 344, "gate", 30, RED, "end", "bold")

    s.caption(["实践四步流程：造已知答案，智能体执行分析，",
               "三步验证对账，批量核查引用。"], [INK, INK], 30,
              top=548, gap=44, pad_top=16)
    s.save("19_procedure_flowchart.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())

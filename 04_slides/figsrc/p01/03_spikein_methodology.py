#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""03_spikein_methodology.py — 生成 03_spikein_methodology.svg
（FIG-P01-04：spike-in 已知答案验证闭环）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-04（P16，cols 一栏，800×700）。
依据：教材 §24.4.5「已知答案的三条设计规则」与 24.4.1 的扰动响应；讲义 ③ 案例
数据节。规模与参数直读 03_code/phd/scripts/01_make_spikein_counts.R（2 000 基因
× 6 样本、20 个上调 8 倍、固定种子 20260829，教材 §24.1）。判据阈值 18/20 与镜像
相关 ≈ −1 出自教材 §24.4.4 的教学设计（本例阈值），不是通用标准：本图只标阈值，
不推导，也不暗示别的数据可照搬。纯示意，无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 03_spikein_methodology.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "真实数据无真值。流程外造已知答案，向系统注入已知量，验系统响应。"
X1, X2, W, H = 36, 420, 344, 344      # 左/右栏 x，卡片宽


def box(s, x, y, w, h, head, lines, stroke, tint, kpi=None, gap=36, lsize=30):
    s.rect(x, y, w, h, tint, stroke, 4, rx=12)
    s.text(x + 18, y + 42, head, 32, stroke, "start", "bold")
    for i, ln in enumerate(lines):
        s.text(x + 18, y + 88 + i * gap, ln, lsize, INK)
    if kpi:
        s.text(x + w - 18, y + 42, kpi, 34, stroke, "end", "bold")


def main():
    s = SVG(800, 700, "Known-answer loop: spike-in methodology", plan=TEXT)

    box(s, X1, 56, W, 170, "STEP 1",
        ["2 000 × 6", "20 × 8-fold", "seed 20260829"], CYAN, "#E7F5F8")
    box(s, X2, 56, W, 170, "STEP 2", ["ai_code_runs", "on_this_matrix"],
        BLUE, BLUE_TINT)

    box(s, X1, 290, W, 150, "STEP 4", ["fail→patch_code", "rerun_step2"],
        RED, RED_TINT)
    box(s, X2, 290, W, 150, "STEP 3", ["recall ≥ 18/20", "cor ≈ −1"],
        GREEN, GREEN_TINT)

    # 四步闭环
    s.arrow(X1 + W + 2, 141, X2 - 6, 141, GRAY, 5, 13)          # 1 → 2
    s.arrow(X2 + 172, 230, X2 + 172, 286, GRAY, 5, 13)          # 2 → 3
    s.arrow(X2 - 6, 365, X1 + W + 2, 365, GRAY, 5, 13)          # 3 → 4
    s.arrow(X1 + 172, 286, X1 + 172, 230, RED, 5, 13)           # 4 → 1（未通过重验）
    s.text(X1 + 158, 266, "loop", 30, RED, "end")

    # 通过分支：答案进入分析产物
    s.arrow(X2 + 172, 444, X2 + 172, 508, GREEN, 6, 15)
    s.chip(X2 + 172, 552, "PASS → paper", 30, WHITE, GREEN, GREEN,
           anchor="middle", h=56)

    s.caption(["真实数据无真值。流程外造已知答案，",
               "向系统注入已知量，验系统响应。"], [INK, INK], 30,
              top=600, gap=44, pad_top=16)
    s.save("03_spikein_methodology.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())

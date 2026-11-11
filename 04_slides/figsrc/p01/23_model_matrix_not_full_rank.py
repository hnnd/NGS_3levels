#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""23_model_matrix_not_full_rank.py — 生成 23_model_matrix_not_full_rank.svg
（FIG-P01-24：设计矩阵不满秩与批次混杂）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-24（P62，cols 一栏，800×700）。
依据：教材 §24.4.6 与讲义 ⑨-E3——当批次与处理完全混杂（批次 1 全是对照、
批次 2 全是处理）时，处理列向量与批次列向量重合，设计矩阵秩亏 1，DESeq2 直接
报 `the model matrix is not full rank`；交叉安排（每批都有对照与处理）则满秩可解。
删掉 batch 变量能让代码跑通，但批次效应被永久吸收进处理组效应。
两张 2×2 格子表，格子内只写 grp 标签：CON / TRT。
无网络、无随机数（不引任何数值）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 23_model_matrix_not_full_rank.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "设计矩阵不满秩：批次与处理完全混杂，秩亏一。删批次藏混杂，须交叉安排。"


def grid(s, x, y, cells, edge, tint, sw=4):
    """2×2 格子：cells 为 [[左上, 右上], [左下, 右下]]。"""
    for r in range(2):
        for c in range(2):
            cx, cy = x + c * 104, y + r * 96
            s.rect(cx, cy, 100, 92, tint, edge, sw, rx=8)
            s.text(cx + 50, cy + 58, cells[r][c], 30, INK, "middle", "bold")


def main():
    s = SVG(800, 700, "Model matrix not full rank", plan=TEXT)

    # ---- 左：完全混杂（rank deficient）----
    s.rect(40, 44, 340, 300, RED_TINT, RED, 5, rx=12)
    s.text(60, 90, "confounded", 32, RED, "start", "bold")
    grid(s, 108, 118, [["CON", "TRT"], ["CON", "TRT"]], RED, WHITE, 4)
    s.text(210, 372, "rank - 1", 32, RED, "middle", "bold")

    # ---- 右：交叉安排（full rank）----
    s.rect(420, 44, 340, 300, GREEN_TINT, GREEN, 4, rx=12)
    s.text(440, 90, "crossed", 32, GREEN, "start", "bold")
    grid(s, 488, 118, [["CON", "TRT"], ["TRT", "CON"]], GREEN, WHITE, 4)
    # 对勾放在卡片内部右下角：原 (676,350) 半径 18 会跨在卡片下边框（y=344）上
    s.check(716, 310, 18, GREEN, 8)

    # ---- 下方：得到的两个「修复」----
    s.rect(40, 400, 352, 116, WHITE, RED, 3, rx=12)
    s.text(66, 444, "drop_batch", 32, RED, "start", "bold")
    s.text(66, 490, "runs · bias_kept", 30, INK)

    s.rect(408, 400, 352, 116, WHITE, BLUE, 3, rx=12)
    s.text(434, 444, "keep_batch", 32, BLUE, "start", "bold")
    s.text(434, 490, "full_rank · honest", 30, INK)

    s.caption(["设计矩阵不满秩：批次与处理完全混杂，秩亏一。",
               "删批次藏混杂，须交叉安排。"], [INK, INK], 30,
              top=560, gap=44, pad_top=16)
    s.save("23_model_matrix_not_full_rank.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())

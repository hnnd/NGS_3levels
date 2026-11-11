#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_covariate_matrix_alignment.py — 生成 09_covariate_matrix_alignment.svg
（FIG-P05-09：P24「Q 的工程细节：三件事一起做」，cols 左栏）【new-svg】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-09（800×700，中文共 26 字）。
依据：教材 §21.4.3——GEMMA 的协变量文件有三道工程防线：① 从
`pca.eigenvec` 取前若干个主成分；② 按样本 IID 键与 `.fam` 逐行对齐（直接
`awk` 拼接特征向量会静默错位）；③ 首列显式补一列全 1 作截距（GEMMA 不自动
补截距），并断言行数与 `.fam` 一致。
图内中文严格取方案给定三句（10 + 7 + 9 = 26 字），第一句拆成两行。
配色：深蓝＝矩阵框线，青蓝＝对齐，绿＝截距补全；红色只标「断言行数」这一处。
无网络；不涉及随机数（纯结构示意，无计算结果）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 09_covariate_matrix_alignment.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["主成分键匹配对齐行序",     # 10
           "首列补全一截距",          # 7
           "断言行数防静默错位"]       # 9
TEXT = "".join(PHRASES)
H1A, H1B = "主成分键匹配", "对齐行序"      # 合起来＝PHRASES[0]


def grid(s, x, y, rows, cols, cw, ch, col, hi_col=None):
    """小矩阵图标：rows×cols 的格子；hi_col 指定的列用绿色高亮（截距列）。"""
    for r in range(rows):
        for c in range(cols):
            fill = GREEN_TINT if c == hi_col else WHITE
            s.rect(x + c * cw, y + r * ch, cw - 4, ch - 4, fill, col, 2)


def main():
    s = SVG(800, 700, "Covariate matrix engineering", plan=TEXT)

    # ---------- 卡片 1：取主成分 ----------
    s.rect(40, 38, 720, 132, BLUE_TINT, BLUE, 5, rx=14)
    s.text(64, 92, H1A, 32, BLUE, "start", "bold")
    s.text(64, 144, "pca.eigenvec → PC1–PC4", 30, GRAY)
    grid(s, 566, 62, 3, 4, 42, 32, BLUE)

    s.arrow(400, 172, 400, 192, CYAN_DEEP, 5, 12)

    # ---------- 卡片 2：按 IID 键对齐行序 ----------
    s.rect(40, 196, 720, 132, CYAN_TINT, CYAN_DEEP, 5, rx=14)
    s.text(64, 250, H1B, 32, CYAN_DEEP, "start", "bold")
    s.text(64, 302, "join by IID ／ .fam order", 30, GRAY)
    grid(s, 566, 220, 3, 2, 60, 32, CYAN_DEEP)

    # ---------- 卡片 3：首列补 1 作截距 ----------
    s.rect(40, 356, 720, 132, GREEN_TINT, GREEN, 5, rx=14)
    s.text(64, 410, PHRASES[1], 32, GREEN, "start", "bold")
    s.text(64, 462, "1 ｜ PC1 ｜ PC2 ｜ PC3 ｜ PC4", 30, GRAY)
    grid(s, 566, 380, 3, 5, 34, 32, GREEN, hi_col=0)

    s.arrow(400, 490, 400, 510, CYAN_DEEP, 5, 12)

    # ---------- 断言条：行数不符当场报错（唯一红色警示）----------
    s.rect(40, 512, 720, 150, RED_TINT, RED, 5, rx=14)
    s.text(64, 568, PHRASES[2], 32, RED, "start", "bold")
    s.text(64, 624, "assert(covar_rows == fam_rows)", 30, GRAY)
    s.cross(706, 586, 32, RED)

    s.save("09_covariate_matrix_alignment.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 26, TEXT
    assert H1A + H1B == PHRASES[0]
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_meff_three_routes.py — 生成 11_meff_three_routes.svg
（FIG-P05-11：P28「M_eff 的三条估计路线」，cols 左栏）【new-svg】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-11（800×700，中文共 27 字）。
依据：教材 §21.4.4——有效独立检验数 M_eff 有三条估计路线：① 用 LD 剪枝后
留下的标记行数（可复现、偏保守，适合作起点）；② simpleM：对标记相关矩阵做
特征值分解，按累积贡献估计；③ 置换：重排表型若干次取最小 p 值的 5% 分位，
不依赖独立性假设，是公认黄金标准，但有效性严格依赖交换性（分层存在时无条件
置换的阈值偏松）。
图内中文严格取方案给定两句（13 + 14 = 27 字）；路线 3 的标签用英文
（permutation），不占汉字预算。配色：青蓝＝剪枝计数，紫＝特征值分解，
绿＝置换；红色只标「可交换性」这一处前提。
无网络；不涉及随机数（纯结构示意，无计算结果）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 11_meff_three_routes.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["剪枝计数稳健特征值系统分解",        # 13
           "置换不依独立假设依赖可交换性"]      # 14
TEXT = "".join(PHRASES)
R1, R2 = "剪枝计数稳健", "特征值系统分解"      # 合起来＝PHRASES[0]
R3_TAIL = "可交换性"                          # 末 4 字标红（方案指定）


def main():
    s = SVG(800, 700, "Three routes to the effective number of tests",
            plan=TEXT)

    # ---------- 路线 1：剪枝计数 ----------
    s.rect(40, 40, 720, 118, CYAN_TINT, CYAN, 5, rx=14)
    for i in range(14):
        s.rect(72 + i * 26, 82, 14, 34, CYAN, None, 0, rx=3)
    s.text(452, 108, R1, 32, CYAN_DEEP, "start", "bold")
    s.text(452, 146, "prune.in rows", 30, GRAY)

    # ---------- 路线 2：特征值分解 ----------
    s.rect(40, 172, 720, 118, PURPLE_TINT, PURPLE, 5, rx=14)
    for i, hgt in enumerate((78, 54, 38, 24, 14)):
        s.rect(74 + i * 30, 268 - hgt, 20, hgt, PURPLE, None, 0, rx=3)
    s.text(452, 240, R2, 32, PURPLE, "start", "bold")
    s.text(452, 278, "simpleM eigenvalues", 30, GRAY)

    # ---------- 路线 3：置换（标签用英文，不占汉字预算）----------
    s.rect(40, 304, 720, 118, GREEN_TINT, GREEN, 5, rx=14)
    s.polyline([(72, 342), (128, 342)], GREEN, 4)
    s.polyline([(72, 384), (128, 384)], GREEN, 4)
    s.arrow(150, 384, 150, 342, GREEN, 4, 12)
    s.arrow(186, 342, 186, 384, GREEN, 4, 12)
    s.text(404, 372, "permutation ×1000", 32, GREEN, "start", "bold")
    s.text(404, 410, "min p 5% quantile", 30, GRAY)

    # ---------- 前提：置换依赖可交换性（唯一红色警示）----------
    s.rect(40, 470, 720, 132, WHITE, RED, 5, rx=14)
    s.seg(400, 545, [("置换不依独立假设依赖", INK), (R3_TAIL, RED)], 32,
          "middle", "bold")

    s.save("11_meff_three_routes.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    assert R1 + R2 == PHRASES[0]
    raise SystemExit(main())

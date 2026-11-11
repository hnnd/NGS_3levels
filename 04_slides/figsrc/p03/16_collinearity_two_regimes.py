#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_collinearity_two_regimes.py — 生成 16_collinearity_two_regimes.svg
（FIG-P03-16：第 34 页 cols 一栏「占比协变量两档行为对照」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-16（P34，cols，800×700）。
依据：教材 §16.4.5 L288–296、§16.5.5 L436；专家记录
`reviews/expert/CH16_EXPERT_001.md` 跑③（L99 / L139 / L286，EXP-CH16-07）——
① 严格共线（占比 = 线性组合）：模型矩阵秩亏缺，DESeq2 直接报
「the model matrix is not full rank…」，流程在拟合前安全中断；
② 近似共线（占比加 10⁻⁴ 量级扰动）：矩阵满秩、拟合一路通过，但条件数飙到
2.43×10⁴，系数不可辨识、标准误膨胀——**不报错的那一档才是最危险的一档**。
数字入口：跑③ 捕获的条件数 2.43×10⁴（设例，非实测课程数据）；图内只作两档对照，
不打印其它推断值。脚本内 `check_cond()` 断言该值，任何改动可追溯。
图内中文严格取方案给定 28 字（4 句）。`checkFullRank` 为报错原文中的函数名，
`cond`、`rank deficit` 为矩阵诊断的字段语义，不作英文说明。
配色：深蓝＝报错拦截的安全路径，红色只标近似共线满秩沉默与条件数超万两处。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 16_collinearity_two_regimes.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["严格共线报错停", "近似共线满秩沉默", "条件数超万失真", "沉默掩盖失效"]
TEXT = "".join(PHRASES)
COND_RUN3 = 2.43e4                            # 跑③ 捕获的条件数（设例）


def check_cond():
    if round(COND_RUN3 / 1e4, 2) != 2.43:
        raise SystemExit(f"条件数与专家记录不一致：{COND_RUN3}")
    return f"{COND_RUN3 / 1e4:.2f}×10"


def main():
    base = check_cond()
    s = SVG(800, 700, "Two regimes of collinearity", plan=TEXT)

    # ---------- 左卡：严格共线 → 秩亏 → 报错安全中断 ----------
    s.panel(44, 56, 348, 404, WHITE, BLUE, 4)
    s.band(44, 56, 348, 72, PHRASES[0], BLUE, WHITE, 30, rx=4)
    s.text(218, 186, "rank deficit", 30, GRAY, "middle")
    s.cross(218, 264, 30, RED, 9)                    # 秩亏：拟合前直接拦下
    s.line(70, 318, 366, 318, PANEL, 3)
    s.rect(52, 348, 336, 72, BLUE_TINT, BLUE, 3, rx=10)
    s.text(218, 394, "checkFullRank", 30, BLUE, "middle", "bold")

    # ---------- 右卡：近似共线 → 满秩但系数不可辨识 ----------
    s.panel(408, 56, 348, 404, WHITE, RED, 4)
    s.band(408, 56, 348, 72, PHRASES[1], RED, WHITE, 30, rx=4)
    s.check(582, 186, 30, GREEN, 9)                   # 满秩：一路通过
    s.text(582, 258, "cond", 30, GRAY, "middle")
    s.rect(430, 280, 304, 76, RED_TINT, RED, 3, rx=10)
    s.sci(452, 330, base, "4", 38, RED, "start", "bold")
    s.line(434, 384, 730, 384, PANEL, 3)
    s.text(582, 438, PHRASES[2], 30, RED, "middle", "bold")

    # ---------- 底部总括 ----------
    s.caption([PHRASES[3]], [INK], 30, top=500, gap=48, pad_top=24)
    s.save("16_collinearity_two_regimes.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())

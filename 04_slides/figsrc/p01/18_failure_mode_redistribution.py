#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_failure_mode_redistribution.py — 生成 18_failure_mode_redistribution.svg
（FIG-P01-19：失败模式转移趋势）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-19（P47，cols 一栏，800×700）。
依据：教材 §24.4.8 与讲义 ④4.8——执行型智能体能读报错并重试，浅层失败（语法
报错、不存在的 API、依赖缺失）被大幅压减；但坐标系偏移（0-based vs 1-based）、
批次效应混杂、未做多重校正、单位滑移这些静默语义错误没有报错可读，错误集中
到这里。结论是验证重心移动，而不是错误被消灭。
图中无数值：只用「宽进窄出」的漏斗与下移箭头表达压减方向，漏斗下口不是零。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 18_failure_mode_redistribution.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "智能体消除语法报错，错误向静默语义集中。验证重心转移，不会消亡。"


def main():
    s = SVG(800, 700, "Failure modes redistribute, not disappear", plan=TEXT)

    # 漏斗：上层宽（浅层错误，被压减），下口窄但不闭合（错误没有归零）
    s.polygon([(100, 44), (700, 44), (440, 306), (360, 306)],
              BLUE_TINT, BLUE, 4)
    s.text(400, 100, "syntax · missing_API · deps", 30, BLUE, "middle", "bold")
    s.text(400, 196, "retries → fewer", 30, BLUE, "middle")

    # 下口：残余浅层错误（绿色，仍存在但少）
    s.rect(360, 306, 80, 20, GREEN, GREEN, 2, rx=4)
    s.text(470, 322, "residual", 30, GREEN, "start", "bold")

    # 汇流：静默语义错误在此集中（红）
    s.arrow(400, 330, 400, 392, GRAY, 5, 14)
    s.rect(140, 398, 520, 132, RED_TINT, RED, 5, rx=12)
    s.text(400, 444, "silent_semantic_errors", 32, RED, "middle", "bold")
    s.text(400, 498, "0-based · batch · no FDR · units", 30, RED, "middle")

    s.caption(["智能体消除语法报错，错误向静默语义集中。",
               "验证重心转移，不会消亡。"], [INK, INK], 30,
              top=552, gap=44, pad_top=18)
    s.save("18_failure_mode_redistribution.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())

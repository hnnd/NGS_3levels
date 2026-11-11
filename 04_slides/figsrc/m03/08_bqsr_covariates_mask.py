#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_bqsr_covariates_mask.py — 生成 08_bqsr_covariates_mask.svg
（FIG-M03-11：BQSR 四协变量漂移与已知位点屏蔽机制）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-11（P23，cols 一栏，800×700）。
图内中文按方案（测序循环 序列上下文 经验漂移 已知位点 屏蔽真实变异）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文，工具名/字段名/
命令/参数保留英文，字数不再按 ≤30 字核验。依据：教材 §10.4.3（L124–139）。
无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 48, "BQSR 协变量", 36, INK, "middle", "bold")

    # 左：协变量输入
    s.rect(40, 76, 250, 470, BLUE_TINT, BLUE, 4, rx=16)
    s.text(165, 120, "协变量", 30, BLUE, "middle", "bold")
    covs = [("RG", INK), ("原始 Q 值", INK), ("测序循环", BLUE),
            ("序列上下文", BLUE)]
    for i, (c, col) in enumerate(covs):
        y = 150 + i * 96
        s.rect(60, y, 210, 66, WHITE, BLUE, 4, rx=12)
        s.text(165, y + 44, c, 30, col, "middle", "bold")

    # 中：经验漂移曲线
    s.rect(330, 76, 280, 470, WHITE, PANEL, 3, rx=16)
    s.text(470, 120, "经验漂移", 32, INK, "middle", "bold")
    s.line(370, 470, 580, 470, BLUE, 4)
    s.line(370, 170, 370, 470, BLUE, 4)
    s.text(475, 506, "报告 Q 值", 30, GRAY, "middle")
    s.line(370, 470, 580, 190, PANEL, 5, dash="14 10")
    pts = [(370, 470), (425, 410), (480, 330), (535, 230), (580, 150)]
    s.polyline(pts, CYAN, 7)
    s.text(485, 240, "ΔQ", 34, RED, "middle", "bold")
    s.darrow(440, 350, 470, 306, RED, 5, head=13)
    s.text(470, 546, "Δ = 观测 − 报告", 30, GRAY, "middle")

    # 右：已知位点屏蔽
    s.rect(650, 76, 120, 470, WHITE, PANEL, 3, rx=16)
    s.text(710, 120, "已知位点", 30, BLUE, "middle", "bold")
    s.rect(665, 150, 90, 120, GREEN_TINT, GREEN, 4, rx=10)
    s.text(710, 200, "掩膜", 30, GREEN, "middle", "bold")
    s.text(710, 244, "开", 30, GREEN, "middle", "bold")
    s.rect(665, 300, 90, 120, RED_TINT, RED, 4, rx=10)
    s.text(710, 350, "掩膜", 30, RED, "middle", "bold")
    s.text(710, 394, "关", 30, RED, "middle", "bold")
    s.text(710, 500, "屏蔽真实", 30, INK, "middle")
    s.text(710, 532, "变异", 30, INK, "middle")

    # 连线
    for yy in (183, 279, 375, 471):
        s.arrow(290, yy, 370, 300, GRAY, 5)
    s.arrow(610, 300, 650, 300, GRAY, 5)

    s.rect(40, 580, 720, 58, RED_TINT, RED, 4, rx=12)
    s.text(400, 620, "屏蔽真实变异：无掩膜 = 真变异被当作错误拟合",
           30, RED, "middle", "bold")
    s.text(400, 676, "本课无可信变异集 → 跳过 BQSR", 30, GRAY,
           "middle")
    s.save("08_bqsr_covariates_mask.svg")


if __name__ == "__main__":
    main()

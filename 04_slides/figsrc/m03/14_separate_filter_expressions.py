#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_separate_filter_expressions.py — 生成 14_separate_filter_expressions.svg
（FIG-M03-17：硬过滤逐条分开声明 vs 复合 || 陷阱）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-17（P36，cols 一栏，800×700）。
图内中文按方案（逐条声明 独立拦截 复合表达式 标签缺失 静默全放行）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文，工具名/字段名/
命令/参数保留英文，字数不再按 ≤30 字核验。依据：教材 §10.4.7（L219–226）、
§10.5.2。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403

RULES = [("QD<2", "927"), ("FS>60", "537"), ("MQ<40", "902"),
         ("SOR>3", "1000")]


def main():
    s = SVG(800, 700)
    s.text(400, 46, "VariantFiltration", 36, INK, "middle", "bold")

    # 上：逐条声明
    s.rect(40, 72, 720, 280, WHITE, GREEN, 4, rx=16)
    s.text(400, 114, "逐条声明", 34, GREEN, "middle", "bold")
    for i, (expr, cnt) in enumerate(RULES):
        x = 56 + i * 178
        s.rect(x, 140, 158, 150, GREEN_TINT, GREEN, 4, rx=12)
        s.text(x + 79, 186, expr, 30, INK, "middle", "bold")
        s.text(x + 79, 232, f"拦截 {cnt}", 30, GREEN, "middle", "bold")
        s.text(x + 79, 272, "✓", 34, GREEN, "middle")
    s.text(400, 322, "独立拦截：独立标签 + 独立计数", 30, GRAY,
           "middle")

    # 下：复合陷阱
    s.rect(40, 390, 720, 250, WHITE, RED, 4, rx=16)
    s.text(240, 432, "复合表达式", 32, RED, "middle", "bold")
    s.rect(80, 452, 420, 64, RED_TINT, RED, 4, rx=12)
    s.text(290, 496, "QD<2 || FS>60 || MQ<40 || SOR>3", 30, INK, "middle",
           "bold")
    s.text(590, 496, "单行", 30, RED, "middle", "bold")
    # 求值链
    s.arrow(290, 516, 290, 552, GRAY, 5)
    s.rect(120, 556, 200, 64, WHITE, ORANGE, 4, rx=10)
    s.text(220, 584, "标签缺失", 30, ORANGE, "middle", "bold")
    s.text(220, 610, "缺 MQRankSum", 30, GRAY, "middle")
    s.arrow(320, 588, 380, 588, GRAY, 5)
    s.rect(384, 556, 190, 64, WHITE, RED, 4, rx=10)
    s.text(479, 584, "JEXL 短路", 30, RED, "middle", "bold")
    s.text(479, 610, "退出码 0", 30, GRAY, "middle")
    s.arrow(574, 588, 630, 588, RED, 6)
    s.rect(634, 556, 106, 64, GREEN_TINT, GREEN, 4, rx=10)
    s.text(687, 584, "PASS", 32, GREEN, "middle", "bold")
    s.text(687, 610, "拦截=0", 30, RED, "middle")
    s.text(400, 662, "静默全放行：整条表达式失效，计数 = 0", 30, RED,
           "middle", "bold")
    s.save("14_separate_filter_expressions.svg")


if __name__ == "__main__":
    main()

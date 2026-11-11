#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""23_jexl_silent_pass.py — 生成 23_jexl_silent_pass.svg
（FIG-M03-26：JEXL 缺失标签静默放行机制）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-26（P48，cols 一栏，800×700）。
图内中文按方案（表达式求值 变量未定义 默认放行 退出码 零 零拦截警报）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文；GATK 引擎名、
字段名与日志原文（JEXL/MQRankSum、WARN: undefined variable）保留英文，
字数不再按 ≤30 字核验。依据：教材 §10.4.7（L219–226）、§10.5.2。
无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 44, "JEXL 静默 PASS", 36, INK, "middle", "bold")

    # 1. 记录缺标签
    s.rect(40, 70, 720, 100, WHITE, PANEL, 3, rx=14)
    s.text(95, 114, "1", 32, BLUE, "middle", "bold")
    s.rect(120, 88, 440, 62, BLUE_TINT, BLUE, 3, rx=8)
    s.text(340, 130, "QD=1.8  DP=62（无 MQRankSum）", 30, INK, "middle")
    s.text(635, 114, "标签缺失", 32, RED, "middle", "bold")
    s.text(648, 152, "无 INFO 标签", 30, GRAY, "middle")

    # 2. JEXL 求值
    s.arrow(400, 170, 400, 206, GRAY, 6)
    s.rect(40, 210, 720, 130, WHITE, ORANGE, 4, rx=14)
    s.text(100, 254, "2", 32, ORANGE, "middle", "bold")
    s.text(240, 254, "表达式求值", 32, ORANGE, "middle", "bold")
    s.rect(400, 226, 330, 52, WHITE, ORANGE, 3, rx=8)
    s.text(565, 262, "MQRankSum < -12.5", 30, INK, "middle")
    s.text(270, 304, "WARN: undefined variable", 30, ORANGE, "middle")
    s.text(600, 304, "变量未定义", 32, ORANGE, "middle", "bold")
    s.text(270, 336, "退出码 0", 30, GRAY, "middle")
    s.text(600, 336, "退出码零", 32, RED, "middle", "bold")

    # 3. 默认放行（破损门禁）
    s.arrow(400, 340, 400, 366, RED, 6)
    s.rect(40, 370, 460, 130, RED_TINT, RED, 5, rx=14)
    s.text(100, 412, "3", 32, RED, "middle", "bold")
    s.text(260, 412, "默认放行", 32, RED, "middle", "bold")
    s.line(130, 462, 400, 462, RED, 8)
    s.line(185, 440, 228, 484, RED, 6)
    s.line(270, 440, 313, 484, RED, 6)
    s.line(355, 440, 398, 484, RED, 6)
    s.text(265, 492, "门禁破损，静默 PASS", 30, RED, "middle")
    s.rect(540, 390, 200, 90, GREEN_TINT, GREEN, 4, rx=12)
    s.text(640, 428, "FILTER", 30, GREEN, "middle")
    s.text(640, 464, "PASS", 34, GREEN, "middle", "bold")
    s.arrow(500, 425, 540, 425, GRAY, 6)

    # 4. 拦截 = 0
    s.arrow(640, 480, 640, 526, GRAY, 6)
    s.rect(40, 530, 720, 110, WHITE, RED, 4, rx=14)
    s.text(100, 578, "4", 32, RED, "middle", "bold")
    s.text(300, 578, "零拦截警报", 32, RED, "middle", "bold")
    s.rect(520, 548, 220, 56, RED_TINT, RED, 4, rx=10)
    s.text(630, 586, "拦截计数 = 0", 30, RED, "middle", "bold")
    s.text(300, 630, "质控看似通过；规则形同虚设", 30, GRAY, "middle")
    s.save("23_jexl_silent_pass.svg")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_exit_code_matrix.py — 生成 18_exit_code_matrix.svg
（FIG-U04-21：退出码矩阵与兜底产物四查，FT06-02 落地【机制/兜底】）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-21（P56，cols 一栏，viewBox 800×700）。
左面板（橙）：FastQC 缺失输入 exit 0——缺失输入退出零、静默跳过无报错；
右面板（绿）：兜底产物四查——兜底四查对产物（count / non-empty / mtime / input）；
底部红框「零退出码非做成」。
依据：教材 §6.4.6 L170–178、§6.5.2；figures/ch06_figures.yml FT06-02。
图内汉字 28，红色 1 处。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 18_exit_code_matrix.py
"""
from svghelp import *


def main():
    s = SVG(800, 700)

    # 左面板：exit 0 静默
    s.rect(40, 60, 330, 460, WHITE, stroke=ORANGE_DEEP, sw=6, rx=18)
    s.rect(40, 60, 330, 56, ORANGE_TINT, rx=18)
    s.rect(40, 88, 330, 28, ORANGE_TINT)
    s.text(205, 99, "FastQC", 30, INK, "middle", "bold")
    s.text(205, 190, "exit 0", 40, ORANGE_DEEP, "middle", "bold")
    for i, lab in enumerate(("缺失输入退出零", "静默跳过无报错")):
        y = 268 + i * 76
        s.rect(72, y - 26, 14, 14, ORANGE)
        s.text(104, y, lab, 30, INK, "start", "bold")

    # 右面板：兜底四查
    s.rect(430, 60, 330, 460, WHITE, stroke=GREEN_DEEP, sw=6, rx=18)
    s.text(595, 124, "兜底四查对产物", 32, GREEN_DEEP, "middle", "bold")
    for i, lab in enumerate(("count", "non-empty", "mtime", "input")):
        y = 190 + i * 80
        s.check(486, y - 10, 22, GREEN)
        s.text(530, y, lab, 30, INK, "start", "bold")

    # 底部红框（唯一红色处）
    s.rect(150, 570, 500, 80, RED, rx=18)
    s.text(400, 622, "零退出码非做成", 34, WHITE, "middle", "bold")

    s.save("18_exit_code_matrix.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

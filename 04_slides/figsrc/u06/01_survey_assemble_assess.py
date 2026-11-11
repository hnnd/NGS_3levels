#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_survey_assemble_assess.py — 生成 01_survey_assemble_assess.svg
（FIG-U06-01：勘测→组装→评估路线图）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-01（P8，cols 一栏，800×700）。
数据：无量字数字（教材 §8.1 L21–23 三个问题、§8.6 L425 判断链）。
③评估红描边＝最易被跳过的一步。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 01_survey_assemble_assess.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    blocks = [
        (70, "① 勘测", "多大？多复杂？", BLUE, WHITE, None),
        (270, "② 组装", "拼回原始顺序", BLUE, WHITE, None),
        (470, "③ 评估", "拼得对不对？", WHITE, INK, RED),
    ]
    for y, t1, t2, fill, tcol, border in blocks:
        s.rect(190, y, 420, 130, fill, border, 6, rx=18)
        s.text(400, y + 58, t1, 40, tcol, "middle", "bold")
        s.text(400, y + 102, t2, 30, tcol, "middle")

    s.arrow(400, 206, 400, 262, CYAN, 8)
    s.arrow(400, 406, 400, 462, CYAN, 8)

    s.save("01_survey_assemble_assess.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

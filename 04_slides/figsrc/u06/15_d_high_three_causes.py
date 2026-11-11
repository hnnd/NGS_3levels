#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_d_high_three_causes.py — 生成 15_d_high_three_causes.svg（FIG-U06-15：D 偏高三原因）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-15（P39，cols 一栏，800×700）。
数据：无量字数字（判据定性：总长是否偏大、命中是否集中、深度是否正常）。
三分支处理方向相反（教材 §8.4.8 L286–288、§8.5.5 L407–413）。
注：方案图内文字清单未含「先看深度」（清单合计 29 字＝上限边缘），
③分支末端仅画红色结论「不能去冗余」；如总编要求三分支对称，请示下替换。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 15_d_high_three_causes.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 根节点
    s.rect(290, 50, 220, 80, BLUE, rx=14)
    s.text(400, 102, "D 偏高", 38, WHITE, "middle", "bold")

    # 三分支（青蓝 / 橙 / 紫）+ 分支标签
    children = [
        (40, CYAN, "两套都拼出", "先看总长"),
        (290, ORANGE, "混菌或污染", "看命中与 GC"),
        (540, PURPLE, "真实复制", None),
    ]
    for x, color, name, tag in children:
        s.line(400, 130, x + 110, 270, color, 5)
        s.rect(x, 280, 220, 80, WHITE, color, 5, rx=14)
        s.text(x + 110, 332, name, 34, INK, "middle", "bold")
        if tag:
            s.line(x + 110, 360, x + 110, 396, color, 4)
            s.rect(x + 10, 400, 200, 62, WHITE, color, 4, rx=12)
            s.text(x + 110, 442, tag, 30, INK, "middle", "bold")

    # ③分支末端红色结论（唯一红色：真实复制不能去冗余）
    s.line(650, 360, 650, 480, PURPLE, 4)
    s.rect(540, 484, 220, 66, RED, rx=12)
    s.text(650, 528, "不能去冗余", 34, WHITE, "middle", "bold")

    s.save("15_d_high_three_causes.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_annotation_pipeline.py — 生成 01_annotation_pipeline.svg（FIG-U07-01：两层注释流水线与数据总线）

方案：reviews/course/U07_FIGP_001.md §4.3 FIG-U07-01（P10，cols 一栏，viewBox 800×700）。
数据：无量字数字。结构找位置 → 功能赋名字 → 下游照算；红字＝实验才定功能
（教材 §9.4.1 L80–94）。输入盒与下游盒用英文标注（汉字预算 28 已满）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 01_annotation_pipeline.py
"""
from svghelp import *  # noqa: F401,F403

BOX_W, BOX_H, GAP, Y0, X0 = 160, 140, 20, 230, 50


def main():
    s = SVG(800, 700)

    # 顶部数据总线（大括号式括线 + 方案逐字标签）
    s.line(70, 118, 730, 118, BLUE, 5)
    s.line(70, 118, 70, 140, BLUE, 5)
    s.line(730, 118, 730, 140, BLUE, 5)
    s.text(400, 88, "注释是数据总线", 34, BLUE, "middle", "bold")

    boxes = [
        (BLUE, ["FASTA"]),
        (CYAN, ["结构注释", "找位置"]),
        (PURPLE, ["功能注释", "赋名字"]),
        (GREEN, ["compare", "pathway", "breeding"]),
    ]
    for i, (color, lines) in enumerate(boxes):
        x = X0 + i * (BOX_W + GAP)
        s.rect(x, Y0, BOX_W, BOX_H, color, rx=14)
        n = len(lines)
        for j, ln in enumerate(lines):
            yy = Y0 + BOX_H / 2 + (j - (n - 1) / 2) * 42 + 11
            s.text(x + BOX_W / 2, yy, ln, 30, WHITE, "middle", "bold")
        if i < 3:
            s.arrow(x + BOX_W + 2, Y0 + BOX_H / 2, x + BOX_W + GAP - 2,
                    Y0 + BOX_H / 2, GRAY, 6)

    # 红色结论条（唯一红色：实验才定功能）
    s.rect(190, 560, 420, 60, RED, rx=12)
    s.text(400, 602, "实验验证看功能", 34, WHITE, "middle", "bold")

    s.save("01_annotation_pipeline.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

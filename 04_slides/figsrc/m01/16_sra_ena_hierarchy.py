#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_sra_ena_hierarchy.py — 生成 16_sra_ena_hierarchy.svg
（FIG-M01-18：SRA/ENA 四级层级树与 n 的定位）

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-18（P44，cols 一栏，800×700）。
依据：教材 §13.4.6 L288–296、§13.5.1 L345；讲义 ⑤5.1。无数字、无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 16_sra_ena_hierarchy.py
"""
from svghelp import *  # noqa: F401,F403

NW, NH = 380, 78  # 节点宽/高
X = 110           # 节点左缘（中心 300）


def main():
    s = SVG(800, 700)

    # BioProject（项目）
    s.rect(X, 56, NW, NH, BLUE, rx=14)
    s.text(300, 106, "BioProject 项目", 32, WHITE, "middle", "bold")
    s.line(300, 134, 300, 168, BLUE, 5)

    # BioSample（样本：真正 n，绿色实线框突出）
    s.rect(X, 168, NW, NH, GREEN_TINT, GREEN, 6, rx=14)
    s.text(300, 218, "BioSample 样本：真正 n", 30, INK, "middle", "bold")
    s.line(300, 246, 300, 280, BLUE, 5)

    # Experiment（文库平台）
    s.rect(X, 280, NW, NH, BLUE, rx=14)
    s.text(300, 330, "Experiment 文库平台", 32, WHITE, "middle", "bold")
    s.line(300, 358, 300, 392, BLUE, 5)

    # Run（数据文件）→ 两个 Run 子节点
    s.rect(X, 392, NW, NH, ORANGE, rx=14)
    s.text(300, 442, "Run", 32, WHITE, "middle", "bold")
    s.line(300, 470, 300, 496, ORANGE, 5)
    s.line(300, 496, 220, 496, ORANGE, 5)
    s.line(300, 496, 380, 496, ORANGE, 5)
    s.line(220, 496, 220, 516, ORANGE, 5)
    s.line(380, 496, 380, 516, ORANGE, 5)
    for cx in (220, 380):
        s.rect(cx - 72, 516, 144, 62, ORANGE_TINT, ORANGE, 4, rx=12)
    s.text(220, 557, "Run 1", 30, INK, "middle", "bold")
    s.text(380, 557, "Run 2", 30, INK, "middle", "bold")

    # 右侧红色警示虚线：Run 数 ≠ n（全图唯一红色）
    s.line(490, 431, 512, 431, RED, 4, dash="10 8")
    s.rect(512, 386, 280, 100, "none", RED, 5, rx=14, dash="14 10")
    s.text(652, 432, "Run 文件：", 30, RED, "middle", "bold")
    s.text(652, 470, "Run 数≠n", 30, RED, "middle", "bold")

    s.save("16_sra_ena_hierarchy.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

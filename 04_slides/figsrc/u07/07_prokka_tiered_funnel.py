#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_prokka_tiered_funnel.py — 生成 07_prokka_tiered_funnel.svg（FIG-U07-07：Prokka 分层注释漏斗，FT09-01）

方案：reviews/course/U07_FIGP_001.md §4.2 FIG-U07-07（P21，cols 一栏，viewBox 800×700）。
数据：无量字数字。先严后宽：用户精选库 → 核心参考库 → 特异结构域 → 假定蛋白兜底
（教材 §9.4.3 L140–152、§9.5.1；figures/ch09_figures.yml FT09-01 落地）。
层级英文库名不占汉字预算。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 07_prokka_tiered_funnel.py
"""
from svghelp import *  # noqa: F401,F403

TIERS = [
    ("用户精选库", BLUE, 220, ["--proteins", "/ --hmms"]),
    ("核心参考库", CYAN_DEEP, 300, ["ISfinder·AMR", "Swiss-Prot"]),
    ("特异结构域", PURPLE, 380, ["Pfam", "TIGRFAM"]),
    ("假定蛋白兜底", ORANGE, 460, ["hypothetical"]),
]
CX = 340  # 漏斗中轴


def main():
    s = SVG(800, 700)
    y = 60
    for i, (name, color, w, tags) in enumerate(TIERS):
        last = i == len(TIERS) - 1
        h = 96
        if last:
            s.rect(CX - w / 2, y, w, h, ORANGE, RED, 6, rx=10)
        else:
            s.polygon([
                (CX - w / 2 + 10, y), (CX + w / 2 - 10, y),
                (CX + w / 2 + 30, y + h), (CX - w / 2 - 30, y + h),
            ], color)
        tcolor = INK if last else WHITE
        s.text(CX, y + h / 2 + 12, name, 32, tcolor, "middle", "bold")
        ty = y + h / 2 + 2 - (len(tags) - 1) * 20
        for j, tag in enumerate(tags):
            s.text(600, ty + j * 44, tag, 30, GRAY, "start")
        s.line(CX + w / 2 + (10 if not last else 0), y + h / 2, 592,
               y + h / 2, PANEL, 3)
        if not last:
            s.arrow(CX, y + h + 4, CX, y + h + 28, GRAY, 5, head=12)
        y += h + 32

    # 底部 caption（方案逐字：先严后宽）；唯一红色＝底层托盘红描边
    s.text(CX, 636, "先严后宽", 34, BLUE, "middle", "bold")

    s.save("07_prokka_tiered_funnel.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_mash_screen_vs_fastani.py — 生成 14_mash_screen_vs_fastani.svg（FIG-U08-14：
Mash screen 初筛与 FastANI 片段精确比对）

方案：reviews/course/U08_FIGP_001.md §4 FIG-U08-14（P41，cols 一栏，800×700）。
数据来源：FastANI README 官方规范 fragLen=3000、k=16（ALN §0.6 实查）；
Mash screen k=21、s=1000（教材 §11.4.2、§11.6）。零登录号（规避 ALN W17）。
两阶段漏斗：Mash MinHash 草图初筛 Top 10 → FastANI 3,000 bp 片段双向精细
比对 → 红色焦点框（唯一红）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 14_mash_screen_vs_fastani.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # —— 第一阶段：Mash screen（深蓝）——
    s.text(48, 56, "第一步 Mash：", 32, BLUE, "start", "bold")
    s.text(48, 96, "草图初筛 Top10", 32, BLUE, "start", "bold")
    s.rect(118, 124, 110, 52, WHITE, BLUE, 4, rx=10)
    s.text(173, 158, "query", 30, INK, "middle", "bold")
    s.text(173, 208, "RefSeq 6 GB", 30, GRAY, "middle")
    # 漏斗
    s.polygon([(48, 224), (298, 224), (258, 306), (88, 306)], BLUE)
    s.text(173, 274, "MinHash k=21", 30, WHITE, "middle", "bold")
    s.rect(68, 328, 210, 60, BLUE, rx=12)
    s.text(173, 368, "Top 10 参考集", 32, WHITE, "middle", "bold")

    # 阶段间箭头
    s.arrow(318, 280, 400, 280, GRAY, 7)

    # —— 第二阶段：FastANI 片段精细比对（青蓝）——
    s.text(420, 56, "第二步 FastANI：", 32, CYAN_DEEP, "start", "bold")
    s.text(420, 96, "片段精细比对", 32, CYAN_DEEP, "start", "bold")
    # 片段条（3,000 bp × 6）
    for i in range(6):
        y = 140 + i * 34
        s.rect(420, y, 130, 22, CYAN, rx=5)
        if i % 2 == 0:
            s.arrow(556, y + 11, 606, y + 11, CYAN_DEEP, 4, head=12)
        else:
            s.arrow(606, y + 11, 556, y + 11, CYAN_DEEP, 4, head=12)
    s.text(420, 360, "3,000 bp frags", 30, GRAY, "start")
    # 红色焦点框：精确 ANI 输出（唯一红）
    s.rect(620, 190, 140, 110, WHITE, RED, 5, rx=14)
    s.text(690, 238, "ANI", 34, RED, "middle", "bold")
    s.text(690, 276, "精确值", 32, RED, "middle", "bold")

    # 底部规范注记（ASCII）
    s.rect(150, 470, 500, 62, PANEL, rx=12)
    s.text(400, 512, "fragLen = 3000, k = 16", 32, INK, "middle", "bold")

    s.save("14_mash_screen_vs_fastani.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

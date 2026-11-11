#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_four_symlinks_pipeline.py — 生成 05_four_symlinks_pipeline.svg（FIG-U08-05：
选型不可逆：四条下游软链接与跨环境串行）

方案：reviews/course/U08_FIGP_001.md §4 FIG-U08-05（P21，cols 一栏，800×700）。
路径来自手册 §4.3.3 / §4.4.3 / §4.5.3 / §4.6.3 四处真实软链接命令
（anno、ident、phylo、pangenome 四个工作子目录，盒内两行显示＝完整路径）；
跨环境串行 annot → phylo（教材 §11.4.2、讲义 ④ 4.3）。
红 1 处＝指向不一致扣分（考核底线）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 05_four_symlinks_pipeline.py
"""
from svghelp import *  # noqa: F401,F403

LINKS = [("anno/", "genome.fasta"), ("ident/", "genome.fasta"),
         ("phylo/", "mygenome.fasta"), ("pangenome/", "genomes/")]


def main():
    s = SVG(800, 700)

    # 顶部选型结果卡（绿）
    s.rect(180, 44, 360, 72, GREEN, rx=14)
    s.text(360, 92, "选型定稿：指向 Flye", 34, WHITE, "middle", "bold")

    # 红色警示角标（唯一红）
    s.rect(570, 44, 220, 60, RED, rx=12)
    s.text(680, 84, "指向不一致扣分", 30, WHITE, "middle", "bold")

    # 四个软链接目标（青蓝分支；两行＝完整路径）
    pos = [(40, 200), (440, 200), (40, 330), (440, 330)]
    for (x, y), (d, f) in zip(pos, LINKS):
        s.line(360, 116, x + 160, y, CYAN_DEEP, 5)
    for (x, y), (d, f) in zip(pos, LINKS):
        s.rect(x, y, 320, 84, WHITE, CYAN_DEEP, 4, rx=12)
        s.text(x + 160, y + 38, d, 30, GRAY, "middle", "bold")
        s.text(x + 160, y + 70, f, 30, INK, "middle", "bold")

    # 副标题与跨环境串行注记（置于扇形线下方，避免穿越）
    s.text(360, 472, "四条软链接同步改", 32, INK, "middle", "bold")
    s.rect(150, 520, 500, 58, PANEL, rx=12)
    s.text(400, 558, "跨环境串行：annot → phylo", 32, INK, "middle", "bold")

    s.save("05_four_symlinks_pipeline.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

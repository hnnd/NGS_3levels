#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_tree_skip.py — 生成 20_tree_skip.svg
（FIG-U02-20：环境不对，树静默缺一张）

方案：reviews/course/U02_FIGP_001.md §4 FIG-U02-20（P51，cols 一栏，viewBox 800×700）。
数据：缺包打印 [skip]、退出码 0、只有泛基因组图落盘——教材 §3.4.7 L247＋
03_code/02_plot_tree_and_pangenome.R ggsave 行（本任务 grep 复核见回执）。
图内只写教材口径行为，不写行号。红 1 处＝静默缺失块。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 20_tree_skip.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    s.text(140, 150, "缺包不报错", 32, RED, "middle", "bold")
    s.rect(30, 180, 220, 100, BLUE, rx=12)
    s.text(140, 242, "ggtree / ape", 32, WHITE, "middle", "bold")
    s.arrow(250, 230, 276, 230, CYAN, 7)
    s.rect(280, 180, 240, 100, BLUE, rx=12)
    s.text(400, 242, "[skip]，退出码 0", 32, WHITE, "middle", "bold")
    s.arrow(520, 230, 556, 230, CYAN, 7)
    s.rect(560, 180, 220, 100, RED, rx=12)
    s.text(670, 242, "树静默缺失", 34, WHITE, "middle", "bold")

    s.arrow(610, 284, 566, 314, GRAY, 5)
    s.rect(430, 320, 260, 104, CYAN, rx=8)
    s.text(560, 362, "pangenome_", 30, INK, "middle", "bold")
    s.text(560, 400, "composition.pdf", 30, INK, "middle", "bold")
    s.line(712, 284, 712, 497, GRAY, 5)
    s.arrow(712, 497, 694, 497, GRAY, 5)
    s.rect(430, 444, 260, 104, "none", GRAY, 4, dash="12 9", rx=8)
    s.text(560, 486, "core_gene_", 30, GRAY, "middle", "bold")
    s.text(560, 524, "tree.pdf", 30, GRAY, "middle", "bold")

    s.rect(290, 596, 220, 64, GREEN_TINT, GREEN, 4, rx=10)
    s.text(400, 638, "验收＝数文件", 32, GREEN, "middle", "bold")
    s.text(400, 688, "expected 2 PDFs → count files", 30, GRAY, "middle")
    s.save("20_tree_skip.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

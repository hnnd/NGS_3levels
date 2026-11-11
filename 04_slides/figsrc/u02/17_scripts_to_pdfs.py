#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_scripts_to_pdfs.py — 生成 17_scripts_to_pdfs.svg
（FIG-U02-17：三个脚本、五个 PDF）

方案：reviews/course/U02_FIGP_001.md §4 FIG-U02-17（P46，cols 一栏，viewBox 800×700）。
数据：1+2+2=5 个 PDF——教材 §3.4.7/§3.4.9＋03_code 三脚本 ggsave 行已核
（kmer L104；assembly L123/L128；tree L43、pan L92；本任务 grep 复核见回执）。
「四类图、五个文件」口径：CNT-U02-03/BEG-U02-11。图内不印尺寸数字（方案约定）。
红 1 处＝缺包树静默缺失标签。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 17_scripts_to_pdfs.py
"""
from svghelp import *  # noqa: F401,F403

SCRIPTS = [
    ("02_plot_kmer_", "histogram.R"),
    ("02_plot_assembly_", "metrics.R"),
    ("02_plot_tree_and_", "pangenome.R"),
]
PDFS = [("kmer.pdf", 84, 60, False), ("quast_compare.pdf", 180, 60, False),
        ("busco_stacked.pdf", 252, 60, False), ("core_gene_tree.pdf", 380, 60, True),
        ("pangenome_", 452, 100, False)]


def main():
    s = SVG(800, 700)
    s.text(210, 52, "三个脚本", 32, BLUE, "middle", "bold")
    s.text(622, 52, "五个 PDF", 32, CYAN_DEEP, "middle", "bold")

    cy = []
    for i, (l1, l2) in enumerate(SCRIPTS):
        y = 84 + i * 160
        cy.append(y + 52)
        s.rect(20, y, 380, 104, BLUE, rx=10)
        s.text(210, y + 45, l1, 30, WHITE, "middle", "bold")
        s.text(210, y + 84, l2, 30, WHITE, "middle", "bold")

    py = []
    for name, y, h, dashed in PDFS:
        py.append((y, h))
        if name == "pangenome_":
            s.rect(456, y, 332, h, CYAN, rx=8)
            s.text(622, y + 42, "pangenome_", 30, INK, "middle", "bold")
            s.text(622, y + 80, "composition.pdf", 30, INK, "middle", "bold")
        else:
            if dashed:
                s.rect(456, y, 332, h, "none", RED, 4, dash="12 9", rx=8)
                s.text(622, y + 40, name, 30, GRAY, "middle", "bold")
            else:
                s.rect(456, y, 332, h, CYAN, rx=8)
                s.text(622, y + 40, name, 30, INK, "middle", "bold")

    s.text(622, 348, "缺包树会静默少一张", 30, RED, "middle", "bold")

    s.arrow(404, cy[0], 450, py[0][0] + 30, CYAN, 6)
    s.arrow(404, cy[1] - 12, 450, py[1][0] + 30, CYAN, 6)
    s.arrow(404, cy[1] + 12, 450, py[2][0] + 30, CYAN, 6)
    s.arrow(404, cy[2] - 12, 450, py[3][0] + 30, CYAN, 6)
    s.arrow(404, cy[2] + 12, 450, py[4][0] + 50, CYAN, 6)
    s.save("17_scripts_to_pdfs.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_sam_three_outputs.py — 生成 01_sam_three_outputs.svg（FIG-U05-01：比对输出三样东西）

方案：reviews/course/U05_FIGP_001.md §4 FIG-U05-01（P10，cols 一栏，viewBox 800×700）。
SAM 记录 11 列条带，只标列名、不填任何示例值（RNAME 槽位不写实名，规避 F07-02
未登记 contig 名与 TLEN 不自洽两类坑，Q7）；高亮三段并外引标签。
依据教材 §7.1 L13/L15（比对输出三样东西、三层不等价）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 01_sam_three_outputs.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    s.text(40, 352, "SAM", 30, GRAY, "start", "bold")

    # 11 列条带：灰（1–2 列）｜深蓝 RNAME POS（3–4）｜橙 MAPQ（5）｜青蓝 CIGAR（6）｜灰（7–11）
    band_y, band_h = 380, 80
    s.rect(40, band_y, 130, band_h, PANEL, rx=6)          # QNAME FLAG
    s.rect(170, band_y, 200, band_h, BLUE, rx=6)          # RNAME POS
    s.rect(370, band_y, 110, band_h, ORANGE, rx=6)        # MAPQ
    s.rect(480, band_y, 140, band_h, CYAN, rx=6)          # CIGAR
    s.rect(620, band_y, 140, band_h, PANEL, rx=6)         # 7–11 列

    s.text(270, 430, "RNAME POS", 30, WHITE, "middle", "bold")
    s.text(425, 430, "MAPQ", 30, WHITE, "middle", "bold")
    s.text(550, 430, "CIGAR", 30, WHITE, "middle", "bold")

    # 外引标签（引线避开互撞：宽标签上移一行）
    s.line(270, 252, 270, 378, GRAY, 4)
    s.text(270, 240, "候选坐标＝地址", 32, INK, "middle", "bold")
    s.line(425, 280, 425, 378, GRAY, 4)
    s.text(425, 268, "置信度", 32, INK, "middle", "bold")
    s.line(550, 280, 550, 378, GRAY, 4)
    s.text(550, 268, "比对形状", 32, INK, "middle", "bold")

    # 红色警示条（唯一红）
    s.rect(360, 560, 400, 68, RED, rx=12)
    s.text(560, 604, "相似不等于放对", 34, WHITE, "middle", "bold")

    s.save("01_sam_three_outputs.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

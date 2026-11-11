#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_vcf_record_anatomy.py — 生成 18_vcf_record_anatomy.svg
（FIG-M03-21：一行 VCF 的双层断言解剖）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-21（P42，cols 一栏，800×700）。
图内中文按方案（固定前八列 位点断言 样本字段 基因型断言 闭区间坐标）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文；VCF 列名字段
（CHROM/POS/ID/REF/ALT/QUAL/FILTER/INFO/FORMAT）保留英文，字数不再按
≤30 字核验。依据：教材 §10.4.1（L71–86）。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 46, "VCF 记录解剖", 36, INK, "middle", "bold")

    # 上层：位点级
    s.rect(40, 74, 720, 230, WHITE, BLUE, 4, rx=16)
    s.text(160, 116, "位点断言", 32, BLUE, "middle", "bold")
    s.text(480, 116, "固定前八列", 32, GRAY, "middle", "bold")
    cols8 = ["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO"]
    vals8 = ["chr", "12043", ".", "A", "G", "91.9", "PASS", "DP=31"]
    widths = [92, 70, 50, 64, 64, 80, 110, 80]
    x = 48
    for i, (c, v) in enumerate(zip(cols8, vals8)):
        w = widths[i]
        s.rect(x, 136, w, 110, BLUE_TINT if i % 2 == 0 else WHITE, BLUE, 3,
               rx=8)
        s.text(x + w / 2, 172, c, 30, BLUE, "middle", "bold")
        s.text(x + w / 2, 222, v, 30, INK, "middle")
        x += w + 6
    s.text(400, 286, "此处是否有非参考等位？", 30, BLUE, "middle")

    # 下层：样本级
    s.rect(40, 336, 720, 230, WHITE, CYAN_DEEP, 4, rx=16)
    s.text(180, 378, "基因型断言", 32, CYAN_DEEP, "middle", "bold")
    s.text(510, 378, "样本字段", 32, GRAY, "middle", "bold")
    s.rect(60, 398, 190, 126, CYAN, None, rx=8)
    s.text(155, 442, "FORMAT", 30, WHITE, "middle", "bold")
    s.text(155, 480, "GT:AD:DP:", 30, WHITE, "middle")
    s.text(155, 514, "GQ:PL", 30, WHITE, "middle")
    samples = [("s01", "0/1  AD=23,8", CYAN_DEEP), ("s02", "0/0  AD=24,0", PURPLE)]
    for j, (name, gt, col) in enumerate(samples):
        x = 280 + j * 240
        s.rect(x, 398, 220, 120, WHITE, col, 4, rx=8)
        s.text(x + 110, 440, name, 30, col, "middle", "bold")
        s.text(x + 110, 482, gt, 30, INK, "middle")
    s.text(400, 548, "该样本基因型是什么？", 30, CYAN_DEEP, "middle")

    # 侧边注记
    s.rect(40, 596, 350, 76, WHITE, PANEL, 3, rx=12)
    s.text(215, 628, "闭区间坐标", 32, INK, "middle", "bold")
    s.text(215, 660, "1 起始闭区间", 30, GRAY, "middle")
    s.rect(420, 596, 340, 76, WHITE, PANEL, 3, rx=12)
    s.text(590, 628, "QUAL = 位点级", 30, BLUE, "middle", "bold")
    s.text(590, 660, "GQ = 样本级", 30, CYAN_DEEP, "middle")
    s.save("18_vcf_record_anatomy.svg")


if __name__ == "__main__":
    main()

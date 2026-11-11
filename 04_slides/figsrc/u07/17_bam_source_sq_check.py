#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_bam_source_sq_check.py — 生成 17_bam_source_sq_check.svg（FIG-U07-17：BAM 来源与 @SQ 头核对）

方案：reviews/course/U07_FIGP_001.md §4.3 FIG-U07-17（P52，cols 一栏，viewBox 800×700）。
数据：读段回贴本讲 genome.fasta；@SQ 的 SN 与 LN 逐项一致（教材 §9.4.6 L252–258、
07_prep_igv_inputs.sh L51–64）。图内 contig 名与总长沿用 deck 已登记数据
（GCA_987216485，4,768,212 bp）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 17_bam_source_sq_check.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 顶部步骤题注（方案逐字）
    s.text(400, 66, "读段回贴本讲序列", 32, BLUE, "middle", "bold")

    # 左：reads（青蓝）
    s.rect(30, 120, 160, 110, CYAN, rx=12)
    for i in range(3):
        s.rect(50, 140 + i * 26, 120, 16, WHITE, rx=6)
    s.text(110, 282, "reads", 30, GRAY, "middle")

    # 比对箭头（minimap2 为课程默认比对器）
    s.arrow(196, 175, 284, 175, CYAN_DEEP, 6)
    s.text(240, 312, "minimap2", 30, GRAY, "middle")

    # 中：reads.bam + @SQ 表头卡片（深蓝）
    s.rect(290, 110, 220, 170, BLUE, rx=12)
    s.text(400, 154, "reads.bam", 30, WHITE, "middle", "bold")
    s.text(400, 200, "@SQ contig_1", 30, WHITE, "middle")
    s.text(400, 240, "LN:4,768,212", 30, WHITE, "middle")

    # 右：genome.fasta + .fai（白底深蓝框）
    s.rect(530, 110, 240, 170, WHITE, BLUE, 6, rx=12)
    s.text(650, 154, "genome.fasta", 30, BLUE, "middle", "bold")
    s.text(650, 200, ".fai", 30, GRAY, "middle")
    s.text(650, 240, "contig_1", 30, INK, "middle")

    # 对比引线（绿＝两项一致）+ 方案逐字标签
    s.line(510, 180, 530, 180, GREEN, 6)
    s.circle(520, 180, 9, GREEN)
    s.line(510, 232, 530, 232, GREEN, 6)
    s.circle(520, 232, 9, GREEN)
    s.text(520, 320, "头行名称长度一致", 32, BLUE, "middle", "bold")

    # 底部红色禁令横幅（唯一红色）
    s.rect(230, 560, 340, 60, RED, rx=12)
    s.text(400, 602, "严禁跨组装混用", 34, WHITE, "middle", "bold")

    s.save("17_bam_source_sq_check.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

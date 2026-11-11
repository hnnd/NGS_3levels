#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_pipeline_boundary_flow.py — 生成 13_pipeline_boundary_flow.svg
（FIG-M03-16：两套脚本分工与端到端重测序数据流水线）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-16（P32，cols 一栏，800×700）。
图内中文按方案（原始数据 单样本流程 联合分型 敏感性扫描 变异注释）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文，工具名/字段名/
命令/参数保留英文，字数不再按 ≤30 字核验。依据：教材 §10.6（L371–411）。
无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 46, "端到端流程", 36, INK, "middle", "bold")

    def stage(x, y, w, title, sub, col, fill):
        s.rect(x, y, w, 130, fill, col, 5, rx=16)
        s.text(x + w / 2, y + 48, title, 32, col, "middle", "bold")
        s.text(x + w / 2, y + 94, sub, 30, GRAY, "middle")

    stage(40, 72, 190, "原始数据", "清洗 FASTQ", BLUE, BLUE_TINT)
    stage(270, 72, 280, "单样本流程", "03_gatk_pipeline.sh", BLUE, BLUE_TINT)
    stage(590, 72, 170, "联合分型", "手动串联", ORANGE, ORANGE_TINT)
    stage(300, 310, 410, "敏感性扫描", "03_filter_sensitivity.sh", PURPLE,
          PURPLE_TINT)
    stage(40, 310, 220, "变异注释", "SnpEff", GREEN, GREEN_TINT)

    s.arrow(230, 137, 270, 137, BLUE, 6)
    s.arrow(550, 137, 590, 137, ORANGE, 6)
    s.arrow(675, 202, 675, 310, ORANGE, 6)
    s.arrow(300, 375, 260, 375, GREEN, 6)
    s.text(252, 266, "gVCF × 12", 30, CYAN_DEEP, "middle", "bold")
    s.line(252, 240, 252, 204, CYAN_DEEP, 4, dash="9 8")

    s.rect(40, 490, 720, 160, WHITE, PANEL, 3, rx=14)
    s.text(400, 540, "03_gatk_pipeline.sh 止于单样本 gVCF", 30, BLUE,
           "middle", "bold")
    s.text(400, 592, "联合分型 + 阈值扫描：学生手动串联",
           30, ORANGE, "middle")
    s.text(400, 636, "终产物：过滤后 SNP/InDel VCF + SnpEff 表", 30,
           GREEN, "middle")
    s.save("13_pipeline_boundary_flow.svg")


if __name__ == "__main__":
    main()

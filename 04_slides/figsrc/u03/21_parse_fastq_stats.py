#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""21_parse_fastq_stats.py — 生成 21_parse_fastq_stats.svg（FIG-U03-21：主统计脚本三参数）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-21（P53，cols 一栏，800×700）。
教材依据：chapters/ch05/manuscript.qmd §5.6、讲义 ⑤5.6、03_parse_fastq_stats.sh。
命令三参数（P1 输入文件 / P2 基因组大小 G / P3 解码条数）→ 内部流水线
（魔数 → 首字符 → 等长 → N50·D）→ 全量计算一律 qsub 投递。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 21_parse_fastq_stats.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 50, "三参数质控流水线", 36, BLUE, "middle", "bold")
    s.text(400, 92, "登录节点只编辑，计算全量投递", 30, GRAY, "middle",
           "bold")

    # 命令行分解盒
    s.rect(50, 130, 700, 96, "#1E293B", rx=14)
    s.text(80, 172, "bash 03_parse_fastq_stats.sh", 30, WHITE, "start",
           "bold")
    s.text(80, 208, "<F input>  <G genome>  <N decode>", 28, CYAN, "start",
           "bold")

    # 三参数卡（P1/P2/P3，含义由 deck 右栏承载）
    for i, tag in enumerate(["P1", "P2", "P3"]):
        x = 90 + i * 220
        s.rect(x, 270, 160, 100, WHITE, CYAN_DEEP, 4, rx=12)
        s.text(x + 80, 334, tag, 38, CYAN_DEEP, "middle", "bold")
        if i < 2:
            s.arrow(x + 164, 320, x + 216, 320, CYAN_DEEP, 6)

    # 内部流水线
    steps = ["魔数", "首字符", "等长", "N50 · D"]
    for i, st in enumerate(steps):
        x = 50 + i * 180
        s.rect(x, 440, 140, 70, GREEN_TINT, GREEN, 4, rx=12)
        s.text(x + 70, 486, st, 30, GREEN, "middle", "bold")
        if i < 3:
            s.arrow(x + 142, 475, x + 176, 475, GREEN, 6)

    # 红色焦点：投递纪律
    s.rect(140, 580, 520, 76, "none", RED, 6, rx=14)
    s.polygon([(180, 596), (220, 618), (180, 640)], RED)
    s.text(430, 630, "qsub 投递", 34, RED, "middle", "bold")

    s.save("21_parse_fastq_stats.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

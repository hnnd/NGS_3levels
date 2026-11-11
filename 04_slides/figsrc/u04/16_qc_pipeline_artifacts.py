#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_qc_pipeline_artifacts.py — 生成 16_qc_pipeline_artifacts.svg
（FIG-U04-19：四步质控流水线与可对账产物【流程】）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-19（P41，cols 一栏，viewBox 800×700）。
四阶段：原始质检留报告（深蓝）→ 修剪产物留双表（青蓝）→ 复检确认曲线降（橙）
→ 多样本汇总成总表（绿）；每步下方绿色对勾，产物文件名以拉丁文标注。
产物来源：03_code/undergraduate/scripts/04_run_fastqc.sh 实际产物清单。
依据：教材 §6.4.6 L165–188、L180。图内汉字 29，红色 0 处。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 16_qc_pipeline_artifacts.py
"""
from svghelp import *


def main():
    s = SVG(800, 700)
    stages = [
        ("原始质检", "留报告", BLUE, ["fastqc.html", "fastqc.zip"]),
        ("修剪产物", "留双表", CYAN_DEEP, ["clean.fq.gz", "fastp.json",
                                           "fastp.html"]),
        ("复检确认", "曲线降", ORANGE_DEEP, ["fastqc.html", "(clean)"]),
        ("多样本汇总", "成总表", GREEN_DEEP, ["multiqc", "report.html"]),
    ]
    for i, (t1, t2, color, arts) in enumerate(stages):
        x = 16 + i * 192
        # 阶段盒
        s.rect(x, 96, 180, 130, color, rx=14)
        s.text(x + 90, 150, t1, 30, WHITE, "middle", "bold")
        s.text(x + 90, 196, t2, 30, WHITE, "middle", "bold")
        if i < 3:
            s.arrow(x + 182, 161, x + 190, 161, GRAY, sw=6, head=14)
        # 产物卡
        s.rect(x, 292, 180, 210, WHITE, stroke=PANEL, sw=3, rx=14)
        for j, a in enumerate(arts):
            s.text(x + 90, 352 + j * 48, a, 30, GRAY, "middle")
        s.line(x + 90, 234, x + 90, 286, color, sw=5)
        # 绿勾
        s.check(x + 90, 566, 24, GREEN)

    s.save("16_qc_pipeline_artifacts.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

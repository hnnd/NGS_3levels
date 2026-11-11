#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_dual_track_qc.py — 生成 01_dual_track_qc.svg（FIG-U04-01：双轨质控路线）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-01（P09，cols 一栏，viewBox 800×700）。
左轨 Illumina 短读长清洗流水线（FastQC → fastp → 复检 → MultiQC）；
右轨 ONT 长读长特征评估（读长分布 / 碱基总量 / 读段 N50），红字「不做外部质量修剪」；
两轨汇聚到绿框「下游分析」。
依据：教材 §6.4.1 L58–60。图内汉字 27，红色 1 处。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 01_dual_track_qc.py
"""
from svghelp import *


def main():
    s = SVG(800, 700)
    s.text(60, 64, "短读长：清洗流水线", 32, BLUE, "start", "bold")
    s.text(430, 64, "长读长：特征评估", 32, CYAN_DEEP, "start", "bold")

    # 左轨：四步清洗流水线
    steps = ["FastQC", "fastp trim", "re-check", "MultiQC"]
    for i, lab in enumerate(steps):
        y = 116 + i * 122
        s.rect(60, y, 310, 74, BLUE, rx=12)
        s.text(215, y + 48, lab, 32, WHITE, "middle", "bold")
        if i < 3:
            s.arrow(215, y + 76, 215, y + 118, BLUE, sw=6)

    # 右轨：三项特征评估
    feats = ["length dist.", "total bases", "read N50"]
    for i, lab in enumerate(feats):
        y = 116 + i * 122
        s.rect(430, y, 310, 74, CYAN, rx=12)
        s.text(585, y + 48, lab, 32, WHITE, "middle", "bold")

    # 红字警示（唯一红色处）
    s.text(585, 520, "不做外部质量修剪", 30, RED, "middle", "bold")

    # 汇聚到下游分析
    s.arrow(215, 560, 285, 600, GREEN, sw=6)
    s.arrow(585, 552, 515, 600, GREEN, sw=6)
    s.rect(275, 600, 250, 68, GREEN, rx=14)
    s.text(400, 645, "下游分析", 34, WHITE, "middle", "bold")

    s.save("01_dual_track_qc.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

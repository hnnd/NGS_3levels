#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_gff_dual_derivation.py — 生成 09_gff_dual_derivation.svg（FIG-U07-09：同一 GFF3 原件的两种派生）

方案：reviews/course/U07_FIGP_001.md §4.2 FIG-U07-09（P25，cols 一栏，viewBox 800×700）。
数据：无量字数字。带序列完整版 → 机器分析（Roary 依赖末尾序列）；切尾展示版 →
桌面查看（教材 §9.4.4 L186–198、§9.5.2：喂错版本可能报错或结果无效）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 09_gff_dual_derivation.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 中央原件：Prokka 原始 mygenome.gff（深蓝卡片，内置 ##FASTA 段）
    s.rect(250, 56, 300, 160, BLUE, rx=14)
    s.text(400, 104, "mygenome.gff", 32, WHITE, "middle", "bold")
    s.text(400, 142, "GFF3 features", 30, WHITE, "middle")
    s.rect(298, 158, 204, 42, ORANGE, rx=8)
    s.text(400, 188, "##FASTA", 30, INK, "middle", "bold")

    # 左流（绿）：完整原件 → 机器分析
    s.text(40, 240, "带序列完整版", 32, GREEN, "start", "bold")
    s.arrow(262, 220, 196, 292, GREEN, 6)
    s.rect(56, 300, 260, 120, WHITE, GREEN, 6, rx=14)
    s.text(186, 358, "机器分析", 32, GREEN, "middle", "bold")
    s.text(186, 398, "Roary · pan", 30, GRAY, "middle")

    # 右流（青蓝）：awk 切除 ##FASTA → 切尾展示版 → 桌面查看
    s.rect(498, 232, 92, 40, PANEL, rx=8)
    s.text(544, 261, "awk", 30, INK, "middle", "bold")
    s.text(606, 260, "切尾展示版", 32, CYAN_DEEP, "start", "bold")
    s.arrow(538, 220, 604, 292, CYAN_DEEP, 6)
    s.rect(484, 300, 260, 120, WHITE, CYAN_DEEP, 6, rx=14)
    s.text(614, 358, "桌面查看", 32, CYAN_DEEP, "middle", "bold")
    s.text(614, 398, "IGV", 30, GRAY, "middle")

    # 底部红色警示条（唯一红色：一个原件两用法，切勿喂错）
    s.rect(220, 560, 360, 60, RED, rx=12)
    s.text(400, 602, "一个原件两用法", 34, WHITE, "middle", "bold")

    s.save("09_gff_dual_derivation.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

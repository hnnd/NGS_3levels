#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""22_mq_ranksum_metrics.py — 生成 22_mq_ranksum_metrics.svg
（FIG-M03-25：MQ 与两个秩和检验机制）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-25（P47，cols 一栏，800×700）。
图内中文按方案（均方根质量 秩和检验 末端聚集 偏倚显著 即伪影）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文；指标名
（MQ/MQRankSum/ReadPosRankSum/MAPQ）保留英文，字数不再按 ≤30 字核验。
依据：教材 §10.4.7（L209–218）。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 44, "MQ / RankSum", 36, INK, "middle", "bold")

    # ① MQ
    s.rect(40, 68, 720, 160, WHITE, PANEL, 3, rx=14)
    s.text(120, 108, "MQ", 34, ORANGE, "middle", "bold")
    s.text(400, 108, "均方根质量：读段 MAPQ 的 RMS", 30, GRAY, "middle")
    for x, h in [(100, 56), (150, 60), (200, 58), (250, 38), (300, 16)]:
        s.rect(x, 215 - h, 40, h, ORANGE if h < 40 else CYAN, None, rx=3)
    s.text(400, 172, "低 MQ → 重复区", 30, RED, "middle")
    s.rect(545, 135, 180, 58, RED_TINT, RED, 4, rx=10)
    s.text(635, 174, "MQ < 40", 32, RED, "middle", "bold")

    # ② MQRankSum
    s.rect(40, 252, 350, 210, WHITE, PANEL, 3, rx=14)
    s.text(215, 290, "MQRankSum", 32, PURPLE, "middle", "bold")
    s.text(215, 322, "秩和检验", 30, GRAY, "middle")
    for y, col, lab, med in [(356, CYAN, "REF", 150), (416, ORANGE, "ALT", 105)]:
        s.line(90, y, 310, y, col, 6)
        s.rect(med - 28, y - 24, 56, 48, WHITE, col, 4, rx=6)
        s.line(med, y - 32, med, y + 32, col, 4)
        s.text(338, y + 10, lab, 30, col, "middle")
    s.text(215, 448, "ALT 更难比对 → 偏负", 30, RED, "middle")

    # ③ ReadPosRankSum
    s.rect(410, 252, 350, 210, WHITE, PANEL, 3, rx=14)
    s.text(585, 290, "ReadPosRankSum", 30, PURPLE, "middle", "bold")
    s.text(585, 322, "末端聚集", 30, GRAY, "middle")
    s.rect(450, 348, 270, 30, PANEL, GRAY, 3, rx=4)
    for x in (690, 700, 692, 708, 696):
        s.line(x, 332, x, 396, ORANGE, 6)
    s.text(585, 414, "ALT 仅在 5–10 bp 末端", 30, GRAY, "middle")
    s.text(585, 448, "接头 / 末端伪影", 30, RED, "middle")

    # 底部结论
    s.rect(40, 492, 720, 90, RED_TINT, RED, 4, rx=14)
    s.text(400, 532, "偏倚显著即伪影", 34, RED, "middle", "bold")
    s.text(400, 566, "ALT 读段系统性偏差 → 伪影信号", 30,
           GRAY, "middle")
    s.text(400, 628, "缺 RankSum 列 → 静默 PASS（P48）", 30,
           ORANGE, "middle")
    s.save("22_mq_ranksum_metrics.svg")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""03_pacbio_ccs_consensus.py — 生成 03_pacbio_ccs_consensus.svg
（FIG-M01-05：PacBio SMRT 环共识机制与同聚物残余）

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-05（P17，cols 一栏，800×700）。
依据：教材 §4.4.3 L100–120、§4.4.5 L145（Wenger 2019 HG002 实测：
HiFi 残余不一致 92.0% 为同聚物背景 indel）；讲义 ④4.1。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 03_pacbio_ccs_consensus.py
"""
from svghelp import *  # noqa: F401,F403

# 突变位点在 subread 条带上的固定位置（行, x偏移, 颜色）
MUTS = [
    (1, 150, ORANGE), (2, 60, GRAY), (3, 230, GRAY), (5, 110, ORANGE),
    (6, 280, GRAY), (8, 90, ORANGE), (9, 200, GRAY), (10, 40, GRAY),
    (11, 250, ORANGE),
]


def main():
    s = SVG(800, 700)

    # 左：SMRTbell 哑铃形环化文库
    s.rect(40, 70, 300, 300, WHITE, PANEL, 3, rx=14)
    s.circle(120, 200, 40, BLUE)
    s.circle(120, 200, 18, WHITE)
    s.circle(260, 200, 40, BLUE)
    s.circle(260, 200, 18, WHITE)
    s.line(120, 188, 260, 188, CYAN, 9)
    s.line(120, 212, 260, 212, CYAN, 9)
    s.text(190, 300, "SMRTbell 环化文库", 30, INK, "middle", "bold")

    # 右：多圈 subreads 堆叠
    s.rect(380, 70, 380, 340, WHITE, PANEL, 3, rx=14)
    for i in range(12):
        y = 100 + i * 22
        s.rect(410, y, 320, 14, BLUE_TINT)
    for row, dx, color in MUTS:
        y = 100 + row * 22
        s.rect(410 + dx, y, 8, 14, color)
    s.text(570, 388, "多圈重读 ≥10 圈", 30, INK, "middle", "bold")

    # 下部流程：多数票 → 高准确 HiFi
    s.arrow(280, 445, 380, 445, GREEN, 8)
    s.rect(380, 420, 110, 52, GREEN, rx=10)
    s.text(435, 456, "HiFi", 32, WHITE, "middle", "bold")
    s.text(510, 456, "多数票压随机错误", 30, GREEN, "start", "bold")

    # 右下：同聚物残留警示（全图唯一红色）
    s.rect(430, 530, 330, 84, RED_TINT, RED, 5, rx=14)
    s.text(595, 584, "同聚物残留 92%", 34, RED, "middle", "bold")

    s.save("03_pacbio_ccs_consensus.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

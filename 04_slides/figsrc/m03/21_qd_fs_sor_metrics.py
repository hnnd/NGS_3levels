#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""21_qd_fs_sor_metrics.py — 生成 21_qd_fs_sor_metrics.svg
（FIG-M03-24：QD/FS/SOR 三指标物理机制与链偏捕捉）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-24（P46，cols 一栏，800×700）。
图内中文按方案（深度去偏 链偏检验 优势比 单向倾斜判定 假变异）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文；指标名与公式
（QD/FS/SOR、QUAL/DP、REF+/ALT- 等）保留英文，字数不再按 ≤30 字核验。
依据：教材 §10.4.7（L202–218）。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 44, "QD / FS / SOR", 36, INK, "middle", "bold")

    # ① QD
    s.rect(40, 68, 720, 180, WHITE, PANEL, 3, rx=14)
    s.text(110, 108, "QD", 34, BLUE, "middle", "bold")
    s.text(320, 108, "QUAL / 未过滤深度", 30, GRAY, "middle")
    for r in range(2):
        for c in range(10):
            s.rect(90 + c * 26, 140 + r * 32, 22, 26, CYAN, None, rx=3)
    s.arrow(370, 166, 430, 166, GRAY, 6)
    s.text(480, 146, "QUAL/DP", 30, BLUE, "middle", "bold")
    s.rect(580, 122, 170, 60, GREEN_TINT, GREEN, 4, rx=10)
    s.text(645, 162, "深度去偏", 30, GREEN, "middle", "bold")
    s.text(320, 222, "深堆叠：虚高 QUAL 被压缩", 30, GRAY,
           "middle")

    # ② FS
    s.rect(40, 272, 350, 200, WHITE, PANEL, 3, rx=14)
    s.text(215, 310, "FS", 34, ORANGE, "middle", "bold")
    s.text(215, 346, "链偏检验 2×2", 30, GRAY, "middle")
    cells = [(80, 366, "REF+", "24", CYAN), (190, 366, "REF-", "1", CYAN),
             (80, 414, "ALT+", "22", ORANGE), (190, 414, "ALT-", "0", ORANGE)]
    for x, y, t, v, col in cells:
        s.rect(x, y, 104, 42, WHITE, col, 3, rx=6)
        s.text(x + 32, y + 30, t, 30, col, "middle")
        s.text(x + 78, y + 30, v, 30, INK, "middle")
    s.text(330, 396, "P↓", 30, RED, "middle", "bold")
    s.text(330, 434, "FS↑", 30, RED, "middle", "bold")

    # ③ SOR
    s.rect(410, 272, 350, 200, WHITE, PANEL, 3, rx=14)
    s.text(585, 310, "SOR", 34, PURPLE, "middle", "bold")
    s.text(585, 346, "对称优势比", 30, GRAY, "middle")
    s.line(450, 420, 450, 360, BLUE, 3)
    s.line(450, 420, 720, 420, BLUE, 3)
    pts = [(450, 420), (520, 392), (600, 370), (690, 362), (720, 360)]
    s.polyline(pts, PURPLE, 6)
    s.text(585, 452, "极端处平滑", 30, GRAY, "middle")

    # 底部结论
    s.rect(40, 500, 720, 90, RED_TINT, RED, 4, rx=14)
    s.text(400, 540, "单向倾斜判定假变异", 34, RED, "middle", "bold")
    s.text(400, 574, "仅一条链有变异 → 伪影而非等位", 30,
           GRAY, "middle")
    s.text(400, 636, "默认： QD 2.0 / FS 60 / SOR 3.0", 30, GRAY, "middle")
    s.save("21_qd_fs_sor_metrics.svg")


if __name__ == "__main__":
    main()

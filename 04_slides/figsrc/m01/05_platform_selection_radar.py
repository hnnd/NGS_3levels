#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_platform_selection_radar.py — 生成 05_platform_selection_radar.svg
（FIG-M01-07：测序平台选型四维雷达与放弃项）

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-07（P21，cols 一栏，800×700）。
依据：教材 §4.4.7 L195–216（硕士四维选型）、§13.4.1 L82；讲义 ④4.2。
无数字、无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 05_platform_selection_radar.py
"""
from svghelp import *  # noqa: F401,F403

T, R, B, L = (400, 60), (760, 340), (400, 620), (40, 340)
C = (400, 340)


def main():
    s = SVG(800, 700)

    # 菱形四象限（淡色底纹均为批准色相；顶点：上 下 左 右）
    s.polygon([L, T, C], BLUE_TINT)      # 左上：连通性
    s.polygon([T, R, C], GREEN_TINT)     # 右上：准确率
    s.polygon([R, B, C], ORANGE_TINT)    # 右下：成本通量
    s.polygon([B, L, C], PURPLE_TINT)    # 左下：样本与修饰
    s.polygon([T, R, B, L], "none", BLUE, 5)
    s.line(T[0], T[1], B[0], B[1], BLUE, 4)
    s.line(L[0], L[1], R[0], R[1], BLUE, 4)
    s.circle(C[0], C[1], 22, WHITE, BLUE, 5)

    # 象限标签（两排，逐字按方案）
    s.text(400, 168, "连通性", 32, BLUE, "middle", "bold")
    s.text(400, 210, "跨重复", 30, INK, "middle")
    s.text(585, 320, "准确率", 32, GREEN, "middle", "bold")
    s.text(585, 362, "免抛光", 30, INK, "middle")
    s.text(400, 480, "成本通量", 32, ORANGE, "middle", "bold")
    s.text(400, 522, "大样本", 30, INK, "middle")
    s.text(215, 378, "样本与修饰", 32, PURPLE, "middle", "bold")

    # 红色警示：必写放弃项（全图唯一红色）
    s.rect(280, 642, 240, 52, RED, rx=12)
    s.text(400, 679, "必写放弃项", 32, WHITE, "middle", "bold")

    s.save("05_platform_selection_radar.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

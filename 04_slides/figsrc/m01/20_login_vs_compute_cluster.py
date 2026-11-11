#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_login_vs_compute_cluster.py — 生成 20_login_vs_compute_cluster.svg
（FIG-M01-23：集群节点网络与算力分工）

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-23（P63，cols 一栏，800×700）。
依据：根 CLAUDE.md 集群反直觉事实（登录节点通外网；计算节点不通外网）；
教材 §13.4.6；讲义 ⑨E4。无数字、无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 20_login_vs_compute_cluster.py
"""
from svghelp import *  # noqa: F401,F403


def server(s, x, y, w, h, color):
    for i in range(3):
        yy = y + i * (h + 8)
        s.rect(x, yy, w, h, "none", color, 5, rx=8)
        s.circle(x + 20, yy + h / 2, 5, color)
        s.line(x + 36, yy + h / 2, x + w - 14, yy + h / 2, color, 4)


def rack(s, x, y, color):
    for r in range(3):
        for c in range(3):
            s.rect(x + c * 62, y + r * 50, 52, 40, "none", color, 4, rx=6)
            s.circle(x + c * 62 + 14, y + r * 50 + 20, 4, color)


def main():
    s = SVG(800, 700)

    # 左泳道：登录节点（通外网，做下载建环境）
    s.rect(40, 80, 330, 430, "none", CYAN_DEEP, 6, rx=18)
    s.text(205, 138, "登录节点：通外网", 32, CYAN_DEEP, "middle", "bold")
    s.text(205, 182, "做下载建环境", 30, INK, "middle", "bold")
    server(s, 80, 210, 130, 34, GREEN)
    s.text(205, 400, "curl · prefetch", 30, GRAY, "middle")
    s.text(205, 442, "conda install", 30, GRAY, "middle")
    s.text(205, 484, "verify_accessions", 30, GRAY, "middle")

    # 右泳道：计算节点集群（无外网，qsub 算力池）
    s.rect(430, 80, 330, 430, "none", BLUE, 6, rx=18)
    s.text(595, 138, "计算节点：无外网", 32, BLUE, "middle", "bold")
    s.text(595, 182, "qsub 算力池", 30, INK, "middle", "bold")
    rack(s, 480, 230, BLUE)
    s.text(595, 428, "pigz · zcat · wc", 30, GRAY, "middle")
    s.text(595, 470, "md5sum", 30, GRAY, "middle")

    # 中央红色警示（全图唯一红色）
    s.rect(60, 548, 680, 68, RED, rx=14)
    s.text(400, 594, "严禁反串运行", 36, WHITE, "middle", "bold")

    s.save("20_login_vs_compute_cluster.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

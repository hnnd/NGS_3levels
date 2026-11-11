#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_cluster_dual_node_architecture.py — 18_cluster_dual_node_architecture.svg
（FIG-M02-24，P45，cols）：集群双节点架构分工（登录外网 vs 计算算力池）【new-svg】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-24。
依据：根 CLAUDE.md 集群事实；讲义 ⑤ 5.0、⑨ 9.1。无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 18_cluster_dual_node_architecture.py
"""
from svghelp import (BLUE, CYAN, CYAN_DEEP, GRAY, INK, PANEL, RED, SVG, WHITE)


def chip(s, x, y, w, h, text, color):
    s.rect(x, y, w, h, WHITE, color, 4, rx=12)
    s.text(x + w / 2, y + h / 2 + 11, text, 30, INK, "middle", "bold")


def main():
    s = SVG(800, 700)
    s.text(790, 44, "cluster rules (schematic)", 30, GRAY, "end")

    # 左泳道：登录节点（青蓝）
    s.rect(30, 140, 330, 460, WHITE, CYAN, 7, rx=18)
    s.text(195, 84, "登录节点：通外网，", 30, CYAN_DEEP, "middle", "bold")
    s.text(195, 122, "做下载建环境", 30, CYAN_DEEP, "middle", "bold")
    chip(s, 70, 230, 250, 76, "curl / wget", CYAN)
    chip(s, 70, 330, 250, 76, "BUSCO lineage", CYAN)
    chip(s, 70, 430, 250, 76, "conda env", CYAN)
    s.text(195, 560, "login node", 30, GRAY, "middle")

    # 右泳道：计算节点（深蓝）
    s.rect(440, 140, 330, 460, WHITE, BLUE, 7, rx=18)
    s.text(605, 84, "计算节点：无外网，", 30, BLUE, "middle", "bold")
    s.text(605, 122, "qsub 算力池", 30, BLUE, "middle", "bold")
    chip(s, 470, 230, 270, 76, "qsub submit", BLUE)
    chip(s, 470, 330, 270, 76, "Flye/OrthoFinder", BLUE)
    chip(s, 470, 430, 270, 76, "CAFE5", BLUE)
    s.text(605, 560, "compute node", 30, GRAY, "middle")

    # 中央红色警示条 + 底部红字横幅（严禁反串运行只出现一次）
    s.rect(368, 350, 64, 160, RED, rx=12)
    s.line(400, 290, 400, 344, RED, 7)
    s.polygon([(400, 350), (386, 324), (414, 324)], RED)
    s.rect(240, 636, 320, 52, PANEL, RED, 5, rx=12)
    s.text(400, 672, "严禁反串运行", 32, RED, "middle", "bold")

    s.save("18_cluster_dual_node_architecture.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

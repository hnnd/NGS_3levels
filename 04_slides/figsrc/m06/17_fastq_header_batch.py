#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_fastq_header_batch.py — FIG-M06-17 FASTQ 序列头拆解与批次识别

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-17（P30，cols 一栏 800×700，new-svg）。
教材依据：§18.4.4（年份不等于 run：年份写 `library_name` 前缀，flowcell 与 run 只能按 FASTQ
头的 instrument/run 号核实）、§18.6（metadata 的 `batch` 列按 run 填）。
图内汉字 = 方案原句逐字，共 22 字（仪器与运行标识 / 真实物理批次 / 采样年份不等于批次）；
其余标注为 FASTQ 字段名与示例值（英文、数字）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 17_fastq_header_batch.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ================= 上：FASTQ 头逐字段拆解 =================
s.text(400, 58, "FASTQ header", 34, BLUE, "middle", "bold")
s.rect(44, 88, 712, 252, WHITE, PANEL, 3, rx=14)

FIELDS = ["@M01234", ":56", ":FC1", ":1", ":1101:14025"]
CS, GAP, Y = 30, 14, 190
w = [text_width(f, CS, True) + 32 for f in FIELDS]
total = sum(w) + GAP * (len(FIELDS) - 1)
x = 400 - total / 2
edges = []
for f, wi in zip(FIELDS, w):
    s.chip(x + wi / 2, Y, f, CS, WHITE, PURPLE, INK, padx=16, pady=11, sw=3)
    edges.append((x, x + wi))
    x += wi + GAP

# 仪器号 + 运行号：青色高亮框（真实物理批次的两段）
x0, x1 = edges[0][0], edges[1][1]
s.rect(x0 - 10, Y - 46, x1 - x0 + 20, 92, "none", CYAN, 5, rx=12)
s.text((x0 + x1) / 2, 132, "仪器与运行标识", 30, CYAN_DEEP, "middle", "bold")

# 绿色括线 + 结论
s.line(x0, 252, x1, 252, GREEN, 5, cap="round")
s.line(x0, 246, x0, 258, GREEN, 5, cap="round")
s.line(x1, 246, x1, 258, GREEN, 5, cap="round")
s.text((x0 + x1) / 2, 296, "真实物理批次", 30, GREEN, "middle", "bold")

# 后三段的字段说明（英文，避免与左侧中文相撞）
s.text(360, 296, "flowcell · lane · xy", 30, GRAY, "start")

# ================= 下：一个采样年份横跨多个 run =================
s.rect(44, 372, 712, 268, WHITE, PANEL, 3, rx=14)
s.text(180, 420, "library_name", 30, GRAY, "middle")
s.chip(180, 480, "year 2017", 32, ORANGE_TINT, ORANGE_DEEP, INK, padx=18, pady=12)

RUNS = [("run 1", 412), ("run 2", 480), ("run 3", 548)]
for name, ry in RUNS:
    s.arrow(292, 480, 486, ry, GREEN, 5, head=14)
    s.chip(556, ry, name, 30, GREEN_TINT, GREEN, INK, padx=16, pady=10)

s.text(400, 610, "采样年份不等于批次", 32, BLUE, "middle", "bold")

s.save("17_fastq_header_batch.svg")

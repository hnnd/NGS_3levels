#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""32_aldex2_silent_failure_audit.py — FIG-M07-35 相对丰度喂给 ALDEx2 的静默失效体征

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-34/35（P64，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.5.6（ALDEx2 吃整数计数：喂相对丰度它不报错、照常输出 p 值，
但结论全部无意义）。三个可自查体征：① 有值、无报错（假象）；
② 表里最大值不大于 1（相对丰度必然 ≤1，整数计数不可能）；
③ 每列（样本）之和恒为 1；处置是换回整数计数重跑。
版式：左「假象报告卡」——表头 p / q / ✓ 与几行灰条，示意「看着像成功」，不写具体数值；
中偏右「体征放大镜」两个可自查体征（≤1 与 =1），两侧用引线接到说明文字；
底部红色虚线卡「换回整数计数」，灰色下行箭头连过去。
≤1 / =1 是定义式，不是实测数字。
图内汉字 = 方案清单逐字（有值无报错假象 7 / 最大值不大于一 7 / 列和恒为一 5 /
换回整数计数 6）＝ 25 字。
红色一处：「换回整数计数」与其虚线边框（同一语义组）。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 32_aldex2_silent_failure_audit.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 左：假象报告卡 ----------------
RY, RW, RH = 88, 272, 356
s.rect(56, RY, RW, RH, WHITE, BLUE, 3, rx=16)
s.text(192, 136, "有值无报错假象", 30, BLUE, "middle", "bold")
s.rect(76, 160, RW - 40, 40, BLUE_TINT, rx=8)
s.text(106, 188, "p", 30, BLUE, "start", "bold")
s.text(196, 188, "q", 30, BLUE, "start", "bold")
s.text(276, 188, "\u2713", 30, GREEN, "start", "bold")
for i in range(4):
    y = 214 + i * 44
    s.rect(76, y, RW - 40, 32, PANEL if i % 2 else WHITE, rx=6)
    for k, w in enumerate((36, 44, 26)):
        s.rect(92 + k * 64, y + 9, w, 14,
               BLUE_TINT if k < 2 else GREEN_TINT, rx=4)

# ---------------- 中右：体征放大镜 ----------------
MX, MY, MR = 478, 300, 98
s.line(342, 348, MX - MR * 0.64, MY + MR * 0.64, GRAY, 9, cap="round")
s.circle(MX, MY, MR, CYAN_TINT)
s.circle(MX, MY, MR, "none", ORANGE_DEEP, 6)
s.text(MX, MY - 12, "\u2264 1", 36, ORANGE_DEEP, "middle", "bold")
s.text(MX, MY + 46, "= 1", 36, GREEN, "middle", "bold")

# ---------------- 右侧说明（引线连接） ----------------
s.line(MX + MR * 0.70, MY - 34, 620, MY - 62, GRAY, 3)
s.label(708, MY - 74, ["最大值", "不大于一"], 30, ORANGE_DEEP, "middle", "bold",
        leading=1.36)
s.line(MX + MR * 0.70, MY + 20, 620, MY + 46, GRAY, 3)
s.label(708, MY + 58, ["列和", "恒为一"], 30, GREEN, "middle", "bold",
        leading=1.36)

# ---------------- 底部：红色警示卡 ----------------
s.arrow(192, RY + RH + 8, 192, 500, GRAY, 4, 14)
s.rect(96, 508, 608, 80, WHITE, RED, 4, rx=16, dash="12 9")
s.text(400, 558, "换回整数计数", 34, RED, "middle", "bold")

s.save("32_aldex2_silent_failure_audit.svg")

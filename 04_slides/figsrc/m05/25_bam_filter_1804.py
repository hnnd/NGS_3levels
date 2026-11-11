#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""25_bam_filter_1804.py — FIG-M05-25 比对清洗与标记去重（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.3 FIG-M05-25（P47，`.cols` 800×700，new-svg）。
教材依据：§15.3 L42、§15.6 L413–L415。`1804 = 4 + 8 + 256 + 512 + 1024`
（unmapped / mate unmapped / secondary / QC fail / duplicate 五类，按 `samtools view -F`
的位掩码语义逐位相加，可手算；deck 正文已列这个加法，故图上只给五个位值）。

布局：左原始 BAM（读段条）→ 中掩码过滤桶（五个位值各配一条被划掉的读段，
直观表示「这一类被滤掉」）→ 右保留的高质唯一比对双端读段（三条成对）。
掩码旁另写合计 `= 1804`，与 deck 手算一致。
配色：保留绿、被滤读段灰、唯一警示色红只用于两处（桶边框 1 + 「识别光学重复」1）——
光学重复是 `1024` 位，正是最需要提醒的一类。
图内汉字 28 字：标题「过滤标记」4 ＋ 结论「按掩码清除低质未配对读段」12 ＋
「识别光学重复」6 ＋ 框名「原始」2、「滤除」2、「保留」2 = 28。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 25_bam_filter_1804.py
"""
from svghelp import *

MASK = 4 + 8 + 256 + 512 + 1024
assert MASK == 1804

s = SVG()

s.text(400, 62, "过滤标记", 36, BLUE, "middle", "bold")

# ---------------- 左：原始 BAM ----------------
LX, LY, LW, LH = 34, 132, 190, 300
s.rect(LX, LY, LW, LH, WHITE, PANEL, 3, rx=14)
s.text(LX + LW / 2, LY + 42, "原始", 30, GRAY, "middle", "bold")
for i in range(6):
    s.rect(LX + 34, LY + 84 + i * 34, LW - 68, 18, CYAN, None, rx=4)

# ---------------- 中：掩码过滤桶 ----------------
BX, BY, BW_, BH_ = 268, 130, 210, 312
s.rect(BX, BY, BW_, BH_, WHITE, RED, 5, rx=14)
s.text(BX + BW_ / 2, BY + 40, "滤除", 30, GRAY, "middle", "bold")
for i, v in enumerate((4, 8, 256, 512, 1024)):
    y = BY + 78 + i * 40
    s.rect(BX + 20, y, 62, 28, PANEL, rx=6)
    s.text(BX + 51, y + 21, str(v), 30, GRAY, "middle", "bold")
    rx0, rx1 = BX + 96, BX + BW_ - 20                     # 被滤掉的读段条
    s.rect(rx0, y + 5, rx1 - rx0, 18, "#CFCFC9", rx=4)
    s.line(rx0 + 6, y + 22, rx1 - 6, y + 6, GRAY, 3)      # 划掉
s.text(BX + BW_ / 2, BY + BH_ - 16, "= 1804", 32, BLUE, "middle", "bold")

# 原始 → 桶 → 保留
s.arrow(LX + LW + 8, LY + 150, BX - 10, LY + 150, GRAY, 5, 14)
s.arrow(BX + BW_ + 8, LY + 150, 546, LY + 150, GRAY, 5, 14)

# ---------------- 右：保留的高质双端读段 ----------------
RX, RY, RW, RH = 546, 132, 218, 300
s.rect(RX, RY, RW, RH, GREEN_TINT, GREEN, 4, rx=14)
s.text(RX + RW / 2, RY + 42, "保留", 30, GREEN, "middle", "bold")
for i, w in enumerate((104, 84, 116)):
    y = RY + 96 + i * 62
    s.rect(RX + 24, y - 6, 14, 50, GREEN, None, rx=4)     # 双端读段的另一端
    s.line(RX + 40, y, RX + 40 + w, y, GREEN, 7)
    s.line(RX + 40, y + 38, RX + 40 + w, y + 38, GREEN, 7)

# ---------------- 结论（方案原句逐字） ----------------
s.text(400, 552, "按掩码清除低质未配对读段", 32, INK, "middle", "bold")
s.text(400, 614, "识别光学重复", 32, RED, "middle", "bold")

s.save("25_bam_filter_1804.svg")
print(f"check: 掩码 4+8+256+512+1024 = {MASK}")

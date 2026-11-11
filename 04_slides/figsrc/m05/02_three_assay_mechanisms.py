#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_three_assay_mechanisms.py — FIG-M05-02 三技术切割机制（谁决定切割位置）

方案：`reviews/course/M05_FIGP_001.md` §4.1 FIG-M05-02（P14，`.cols` 800×700，new-svg）。
教材依据：§15.4.1 L85–L101。
图内汉字 26 字，逐字取方案原句（不增不减）：
标题「机制决定选型」6 字；三卡说明「抗体随机捞取」6、「就地引导切割」6、「与转座酶切开放区」8。
其余标注仅为工具与符号（ChIP-seq / CUT&Tag / ATAC-seq / IgG / pA-Tn5 / Tn5），不写整句英文。
配色（spec §2）：抗体青蓝、Tn5 转座酶深蓝、ATAC 无抗体依赖以唯一警示色红框标出（每图 1 处）。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 02_three_assay_mechanisms.py
"""
from svghelp import *

s = SVG()

s.title("机制决定选型", y=64)

PX = [36, 288, 540]
PW, PY, PH = 224, 96, 524
DNA_Y = 430
CAP_Y = 548                     # 说明行块中心（面板内下沿，逐卡内居中）

CARDS = [
    ("ChIP-seq", CYAN, CYAN_DEEP, "抗体随机捞取", None),
    ("CUT&Tag", BLUE, BLUE, "就地引导切割", None),
    ("ATAC-seq", GREEN, GREEN, "与转座酶切开放区", RED),
]

for x, (name, fill, ink, cap, flag) in zip(PX, CARDS):
    s.panel(x, PY, PW, PH, caption=name, cap_size=32, cap_fill=ink,
            stroke=flag if flag else PANEL)
    s.line(x + 20, DNA_Y, x + PW - 20, DNA_Y, INK, 5)          # DNA 主轴


def antibody(cx, top, color):
    """抗体 Y 形：两臂 + Fc 圆 + 柄。"""
    s.polyline([(cx - 20, top), (cx, top + 18), (cx + 20, top)], color, 5)
    s.circle(cx, top + 32, 13, WHITE, color, 4)
    s.line(cx, top + 45, cx, top + 54, color, 4)


# ---------------- ChIP-seq：交联 → 超声打断 → 抗体随机捞取 ----------------
x = PX[0]
for i in range(6):                                              # 打断后的片段
    s.rect(x + 20 + i * 32, DNA_Y - 7, 24, 14, CYAN, CYAN_DEEP, 3, rx=4)
s.rect(x + 84, DNA_Y - 28, 24, 21, CYAN, CYAN_DEEP, 3, rx=4)    # 交联在片段上的蛋白
s.text(x + 96, 246, "IgG", 30, CYAN_DEEP, "middle", "bold")
antibody(x + 96, 262, CYAN_DEEP)
s.arrow(x + 96, 320, x + 96, DNA_Y - 34, CYAN_DEEP, 4, 12)      # 抗体非特异捞取

# ---------------- CUT&Tag：抗体原位定位，pA-Tn5 就地切 ----------------
x = PX[1]
s.text(x + 112, 246, "pA-Tn5", 30, BLUE, "middle", "bold")
antibody(x + 112, 258, BLUE)
s.polygon([(x + 112, 322), (x + 88, 348), (x + 136, 348)], BLUE)   # pA-Tn5 载在 Fc 上
for dx in (-18, 18):                                            # 双切口位置由抗体决定
    s.line(x + 112 + dx, DNA_Y - 18, x + 112 + dx, DNA_Y + 18, BLUE, 5)

# ---------------- ATAC-seq：游离 Tn5 插入无核小体开放区 ----------------
x = PX[2]
s.text(x + 112, 246, "Tn5", 30, GREEN, "middle", "bold")
s.polygon([(x + 112, 258), (x + 90, 288), (x + 134, 288)], GREEN)
s.arrow(x + 112, 292, x + 112, DNA_Y - 32, GREEN, 4, 12)
for cx in (x + 58, x + 166):                                    # 核小体占据区
    s.circle(cx, DNA_Y, 24, GREEN_TINT, GREEN, 4)
for dx in (-14, 14):                                            # 开放区无核小体，随处可切
    s.line(x + 112 + dx, DNA_Y - 18, x + 112 + dx, DNA_Y + 18, GREEN, 5)

# ---------------- 三卡机制说明（方案原句逐字；多行块垂直居中） ----------------
for x, (_, _, _, cap, _) in zip(PX, CARDS):
    s.label(x + PW / 2, CAP_Y, wrap(cap, 30, PW - 34), 30, INK)

s.save("02_three_assay_mechanisms.svg")

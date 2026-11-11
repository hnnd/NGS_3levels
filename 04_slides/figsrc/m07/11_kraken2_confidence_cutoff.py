#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_kraken2_confidence_cutoff.py — FIG-M07-11 过滤假阳性的两道防线

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-11（P23，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.2（Kraken2 两道防线：置信度得分压制偶然匹配；最小读段数截断幽灵长尾；
阈值必须写进方法）。漏斗出口的可信名单只用绿色块表达，不写字——方案「全部图内文字」三条
合计 29 汉字，再加「可信名单」会破 30 红线。
图内汉字 = 方案清单逐字，共 29 字（第一道：置信度压偶然匹配 / 第二道：读段数截断长尾 /
阈值写进方法）。无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 11_kraken2_confidence_cutoff.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

CX = 380


def funnel_band(y, wtop, wbot, h, fill, stroke, label, size=34, ink=None):
    s.polygon([(CX - wtop / 2, y), (CX + wtop / 2, y),
               (CX + wbot / 2, y + h), (CX - wbot / 2, y + h)],
              fill, stroke, 4)
    s.text(CX, y + h * 0.62, label, size, ink or stroke, "middle", "bold")


s = SVG()

# ---------------- 入口：候选读段（图标表达，不写字） ----------------
s.rect(120, 52, 520, 56, BLUE_TINT, BLUE, 3, rx=12)
for i in range(9):
    s.rect(146 + i * 54, 68, 40, 24, BLUE if i % 2 == 0 else CYAN_DEEP, rx=5)

# ---------------- 第一道：置信度 ----------------
funnel_band(150, 660, 560, 150, CYAN_TINT, CYAN_DEEP,
            "第一道：置信度压偶然匹配", 34, CYAN_DEEP)

# ---------------- 第二道：最小读段数 ----------------
funnel_band(322, 520, 420, 130, GREEN_TINT, GREEN,
            "第二道：读段数截断长尾", 34, GREEN)

# ---------------- 出口：可信名单（绿色块 + 对勾，不写字） ----------------
s.rect(CX - 150, 484, 300, 74, GREEN, rx=14)
s.polyline([(CX - 26, 522), (CX - 6, 540), (CX + 30, 502)], WHITE, 8)
s.arrow(CX, 300, CX, 320, CYAN_DEEP, 5, 14)
s.arrow(CX, 452, CX, 482, GREEN, 5, 14)

# ---------------- 底部红字：阈值写进方法（红虚线框住出口 = 同一处警示） ----------------
s.rect(CX - 162, 472, 324, 98, "none", RED, 4, rx=16, dash="12 9")
s.text(CX, 646, "阈值写进方法", 36, RED, "middle", "bold")

s.save("11_kraken2_confidence_cutoff.svg")

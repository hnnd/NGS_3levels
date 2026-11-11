#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_single_vs_coassembly.py — FIG-M07-15 单样本组装 vs 混合组装的天平权衡

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-15（P28，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.3（单样本保留优势种、无跨样嵌合风险；混合组装把多份样本的深度聚起来
更易拼出低丰度基因组，但内存与运行量剧增；取舍依生境而定）。
图内汉字 = 方案清单逐字，共 29 字（单样本：保优势无跨样嵌合 / 混合拼：聚深度但内存剧增 /
按生境权衡）。天平左倾示意「单样本支点轻、覆盖浅」，右倾示意「混合重量大」，只画形态不给比例数字。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 15_single_vs_coassembly.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 支架与横梁 ----------------
PX, PY = 400, 322                     # 支点顶点
s.polygon([(PX, PY), (PX - 62, 528), (PX + 62, 528)], BLUE_TINT, BLUE, 4)
s.rect(PX - 96, 528, 192, 22, BLUE, rx=8)

LX, LY = 138, 246                     # 左梁端（高 = 轻）
RX, RY = 662, 306                     # 右梁端（低 = 重）
s.line(LX, LY, RX, RY, BLUE, 10, cap="round")
s.circle(PX, PY, 12, BLUE)

# ---------------- 左盘：单样本 ----------------
PLX = LX + 6
s.line(LX, LY, PLX - 46, 414, GRAY, 3)
s.line(LX, LY, PLX + 46, 414, GRAY, 3)
s.polygon([(PLX - 96, 414), (PLX + 96, 414), (PLX + 70, 448), (PLX - 70, 448)],
          CYAN_TINT, CYAN_DEEP, 4)
# 盘内：一个优势种的高柱 + 相邻小柱（无跨样嵌合）
s.rect(PLX - 84, 336, 56, 72, CYAN, rx=6)
s.rect(PLX - 16, 372, 38, 36, CYAN_DEEP, rx=6)
s.rect(PLX + 34, 384, 34, 24, CYAN_DEEP, rx=6)

# ---------------- 右盘：混合组装 ----------------
PRX = RX - 6
s.line(RX, RY, PRX - 46, 470, GRAY, 3)
s.line(RX, RY, PRX + 46, 470, GRAY, 3)
s.polygon([(PRX - 96, 470), (PRX + 96, 470), (PRX + 70, 504), (PRX - 70, 504)],
          GREEN_TINT, GREEN, 4)
# 盘内：多份样本的矮柱聚成一片（深度叠加）
for i in range(4):
    s.rect(PRX - 84 + i * 44, 392, 36, 72, GREEN if i % 2 == 0 else GREEN_TINT,
           rx=6)

# ---------------- 两侧标签 ----------------
s.label(PLX, 112, ["单样本：", "保优势无跨样嵌合"], 30, CYAN_DEEP, "middle",
        "bold", leading=1.34)
s.label(PRX, 112, ["混合拼：", "聚深度但内存剧增"], 30, GREEN, "middle",
        "bold", leading=1.34)

# ---------------- 唯一红处：支座上的取舍结论 ----------------
s.text(PX, 640, "按生境权衡", 36, RED, "middle", "bold")

s.save("15_single_vs_coassembly.svg")

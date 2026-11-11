#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""31_two_methods_consensus.py — FIG-M07-34 两法共识决策流与 Jaccard 交并比

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-34（P60，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.8、§19.9 第 9 题（同一批样本分别用 ALDEx2 与 ANCOM-BC 检验，
ALDEx2 交出 8 个显著类群、ANCOM-BC 交出 6 个，两法交集只有 2 个；
交并比 Jaccard = 2/(8+6−2) = 2/12，课程口径只认两法交集）；
计数直接取自方案与教材设例（8 / 6 / 2），非实测输出，图内按设例标注、不代入真实数据。
版式：上韦恩图（左青蓝 ALDEx2、右橙 ANCOM-BC、交集绿并标 2），
下「交并比算式十二分之二」+ 算式 2/(8+6−2)=2/12；红字「单法显著降级」只在图的右下出现一次。
图内汉字 = 方案清单逐字（两法独立取交集 7 / 交并比算式十二分之二 10 / 交集可信 4 /
单法显著降级 6）＝ 27 字。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 31_two_methods_consensus.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 上：韦恩图 ----------------
CY, R = 274, 132
LCX, RCX = 336, 464
s.circle(LCX, CY, R, CYAN_TINT, CYAN_DEEP, 4)      # ALDEx2
s.circle(RCX, CY, R, ORANGE_TINT, ORANGE_DEEP, 4)  # ANCOM-BC

s.badge(LCX - 78, CY + 6, "8", 30, CYAN_DEEP, WHITE)
s.badge(RCX + 78, CY + 6, "6", 30, ORANGE_DEEP, WHITE)
s.badge(400, CY + 6, "2", 32, GREEN, WHITE)

s.text(400, 100, "两法独立取交集", 32, INK, "middle", "bold")
s.text(LCX - 82, CY - 84, "ALDEx2", 30, CYAN_DEEP, "middle", "bold")
s.text(RCX + 84, CY - 84, "ANCOM-BC", 30, ORANGE_DEEP, "middle", "bold")

# 交集结论
s.chip(400, 452, "交集可信", 30, GREEN_TINT, GREEN, GREEN, padx=24, pady=12)

# ---------------- 下：交并比算式 ----------------
s.text(400, 528, "交并比算式十二分之二", 30, GRAY, "middle", "bold")
s.text(400, 588, "2 / (8 + 6 \u2212 2) = 2 / 12", 32, INK, "middle", "bold")

# ---------------- 唯一红处：单法显著降级 ----------------
s.rect(88, 624, 624, 62, WHITE, RED, 4, rx=14, dash="12 9")
s.text(400, 668, "单法显著降级", 32, RED, "middle", "bold")

s.save("31_two_methods_consensus.svg")

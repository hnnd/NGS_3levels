#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_rdp_bootstrap_vote.py — FIG-M06-18 RDP 8-mer 与 bootstrap 投票机制

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-18（P31，cols 一栏 800×700，new-svg）。
教材依据：§18.4.5（参考序列切 8-mer 训练各阶元条件概率；对目标 ASV 评分后做 100 次 bootstrap，
得票够 `minBoot` 才输出该阶元；课程脚本 `MINBOOT=80`；短读长常止于属，种水平退为 `NA`）。
图内汉字 = 方案原句逐字，共 19 字（八聚体条件概率 / 百次重抽样 / 八成一致赋标签）；
其余标注为 8-mer、100、minBoot、Genus、Species、NA 等术语。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 18_rdp_bootstrap_vote.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

s.text(400, 56, "RDP naive Bayes", 34, BLUE, "middle", "bold")

# ================= ① 读段按 8-mer 切分 =================
s.text(400, 112, "八聚体条件概率", 30, CYAN_DEEP, "middle", "bold")

BX, BY, BW, BH = 62, 136, 676, 56
s.rect(BX, BY, BW, BH, CYAN_TINT, BLUE, 4, rx=8)
for i in range(1, 8):
    s.line(BX + BW * i / 8, BY, BX + BW * i / 8, BY + BH, BLUE, 3)
for fx in (0.15, 0.63):
    cx = BX + BW * fx
    s.rect(cx - 26, BY + BH + 10, 52, 12, CYAN, rx=6)
    s.text(cx, BY + BH + 56, "8-mer", 30, GRAY, "middle")

# ================= ② 100 次 bootstrap 投票 =================
s.text(300, 292, "百次重抽样", 30, BLUE, "middle", "bold")
s.text(700, 292, "80 / 100", 30, GRAY, "end")

CX0, CY0 = 74, 336
for j in range(5):
    for i in range(20):
        k = j * 20 + i
        cx, cy = CX0 + i * 34, CY0 + j * 34
        if k < 80:
            s.circle(cx, cy, 9, GREEN)
        else:
            s.circle(cx, cy, 9, WHITE, PURPLE, 3)
s.line(58, CY0 + 3 * 34 + 17, 742, CY0 + 3 * 34 + 17, BLUE, 3, dash="10 8")

# ================= ③ 两种输出 =================
AR = CY0 + 4 * 34 + 30          # 网格之下
s.arrow(250, AR, 250, AR + 30, GREEN, 5, head=14)
s.chip(250, 556, "Genus", 32, ORANGE_TINT, ORANGE_DEEP, INK, padx=22, pady=12)

s.arrow(556, AR, 556, AR + 30, PURPLE, 5, head=14)
s.chip(556, 556, "Species NA", 30, PURPLE_TINT, PURPLE, INK, padx=20, pady=12)

s.line(64, 606, 736, 606, PANEL, 3)
s.text(400, 656, "八成一致赋标签", 32, BLUE, "middle", "bold")

s.save("18_rdp_bootstrap_vote.svg")

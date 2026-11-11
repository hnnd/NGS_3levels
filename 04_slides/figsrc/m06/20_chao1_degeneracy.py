#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_chao1_degeneracy.py — FIG-M06-20 Chao1 公式退化机理

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-20（P33，cols 一栏 800×700，new-svg）。
教材依据：§18.4.6（Chao1 靠单例与双例外推；DADA2 去噪把部分单例判为错误，去嵌合后 `n1` 可能接近 0，
此时 Chao1 退化成 `S_obs`，不再有外推能力；ASV 表的 Chao1 不应与 OTU 表的直接比较）。
图内汉字 = 方案原句逐字，共 20 字（单例项决定外推 / 去噪压低单例 / 退化为观察种类）；
公式按纯文本 `S = S_obs + n1(n1-1)/(2(n2+1))` 书写，abundance class 标 1–4。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 20_chao1_degeneracy.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

s.text(400, 56, "Chao1", 32, BLUE, "middle", "bold")

# ================= 公式骨架（单例项高亮）=================
s.rect(48, 88, 704, 96, WHITE, PANEL, 3, rx=14)
s.text(392, 148, "S = S_obs +", 30, BLUE, "end", "bold")
s.text(400, 148, "n1(n1-1)/(2(n2+1))", 30, ORANGE_DEEP, "start", "bold")

# ================= 左：OTU 计数表（单例庞大）=================
s.rect(48, 212, 336, 288, WHITE, BLUE, 4, rx=14)
s.text(78, 258, "OTU", 30, BLUE, "start", "bold")
s.text(354, 258, "n1 > 0", 30, ORANGE_DEEP, "end", "bold")

BASE, BW = 428, 44
XB = [(96, 104), (170, 74), (244, 56), (318, 42)]
for x, v in XB:
    s.rect(x, BASE - v, BW, v, ORANGE, rx=6)
for i, x in enumerate((96, 170, 244, 318)):
    s.text(x + BW / 2, BASE + 34, str(i + 1), 30, GRAY, "middle")
s.line(74, BASE, 358, BASE, BLUE, 3)

# ================= 右：ASV 计数表（单例趋零）=================
s.rect(416, 212, 336, 288, WHITE, RED, 4, rx=14)
s.text(446, 258, "ASV", 30, BLUE, "start", "bold")
s.text(722, 258, "n1 → 0", 30, RED, "end", "bold")

YB = [(464, 8), (538, 62), (612, 54), (686, 46)]
for x, v in YB:
    s.rect(x, BASE - v, BW, v, PURPLE, rx=6)
for i, x in enumerate((464, 538, 612, 686)):
    s.text(x + BW / 2, BASE + 34, str(i + 1), 30, GRAY, "middle")
s.line(442, BASE, 726, BASE, BLUE, 3)

# ================= 三段结论 =================
s.text(216, 556, "单例项决定外推", 30, ORANGE_DEEP, "middle", "bold")
s.text(584, 556, "去噪压低单例", 30, BLUE, "middle", "bold")

s.arrow(400, 584, 400, 606, BLUE, 5, head=13)
s.text(400, 646, "退化为观察种类", 32, BLUE, "middle", "bold")

s.save("20_chao1_degeneracy.svg")

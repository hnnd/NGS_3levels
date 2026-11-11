#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""29_zero_types_distinction.py — FIG-M07-32 零值的两种本质：采样零 vs 结构零

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-32（P58，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.8（宏基因组数据的零有两类来源，处置方向相反：采样零是「这个类群其实在，
只是深度不够没抽到」，加深测序或先用先验平滑可解（可平滑）；结构零是「这个环境里它根本不在」，
任何填补都是凭空造数据（不可填）。「全局加半」这类操作对所有零一视同仁，会把两类零一起
捏成同一个假值，杠杆效应被扭曲）。
版式：左右对照的天平：左盘青蓝=采样零（可平滑），右盘绿色=结构零（不可填），
中柱下压指针示意两者不可合并处理；底部红字标「全局加半扭曲杠杆」。
不写任何比例数字（无实测入口）。
图内汉字 = 方案清单逐字（采样零：未抽到可平滑 10 / 结构零：真缺失不可填 10 /
全局加半扭曲杠杆 8）＝ 28 字。
红色一处：「全局加半扭曲杠杆」。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 29_zero_types_distinction.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 天平：支点 + 横梁 ----------------
PX, PY = 400, 330                     # 支点顶点
s.polygon([(PX, PY), (PX - 60, 520), (PX + 60, 520)], BLUE_TINT, BLUE, 4)
s.rect(PX - 98, 520, 196, 22, BLUE, rx=8)

LX, LY, RX, RY = 168, 268, 632, 268
s.line(LX, LY, RX, RY, BLUE, 10, cap="round")
s.circle(PX, PY, 11, BLUE)

# ---------------- 左盘：采样零 ----------------
PLX = LX
s.line(LX, LY, PLX - 56, 398, GRAY, 3)
s.line(LX, LY, PLX + 56, 398, GRAY, 3)
s.polygon([(PLX - 112, 398), (PLX + 112, 398), (PLX + 82, 440), (PLX - 82, 440)],
          CYAN_TINT, CYAN_DEEP, 4)
# 盘内：稀疏的浅色圆点（少量抽到）+ 一个虚线空心圆（没抽到但存在）
for cx, cy in ((PLX - 62, 366), (PLX - 18, 376), (PLX + 32, 362)):
    s.circle(cx, cy, 11, CYAN)
s.circle(PLX + 68, 368, 13, "none", CYAN_DEEP, 3, dash="6 5")

# ---------------- 右盘：结构零 ----------------
PRX = RX
s.line(RX, RY, PRX - 56, 398, GRAY, 3)
s.line(RX, RY, PRX + 56, 398, GRAY, 3)
s.polygon([(PRX - 112, 398), (PRX + 112, 398), (PRX + 82, 440), (PRX - 82, 440)],
          GREEN_TINT, GREEN, 4)
# 盘内：空盘 + 一个叉（真的没有）
s.text(PRX, 378, "0", 32, GREEN, "middle", "bold")

# ---------------- 两侧标题 ----------------
s.label(PLX, 132, ["采样零：", "未抽到可平滑"], 30, CYAN_DEEP, "middle", "bold",
        leading=1.36)
s.label(PRX, 132, ["结构零：", "真缺失不可填"], 30, GREEN, "middle", "bold",
        leading=1.36)

# ---------------- 唯一红处 ----------------
s.text(400, 648, "全局加半扭曲杠杆", 34, RED, "middle", "bold")

s.save("29_zero_types_distinction.svg")

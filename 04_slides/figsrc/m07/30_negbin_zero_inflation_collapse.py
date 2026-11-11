#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""30_negbin_zero_inflation_collapse.py — FIG-M07-33 负二项模型在零膨胀下的失效机制

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-33（P59，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.8（DESeq2 一类负二项模型靠「中位数比值」估尺寸因子，每个基因在各样本间的
几何均值作参考；宏基因组特征表零值极多，几何均值含零即整体归零，尺寸因子估不出来，
归一化彻底失效；强行套用会让假阳性极端放大）。
版式：三行「图标 + 结论」纵向三段，段间向下箭头表示连锁失效：
  ① 零膨胀——4×5 格子里只有零星非零值（深蓝），其余全为空格；
  ② 漏斗收窄并在瓶颈处断裂（红色锯齿）——尺寸因子估不出来；
  ③ 瓶颈下口炸开成一排高低不一的柱——假阳性大量涌现。
底部红框徽标「不可照搬」（与第 ③ 行红字同属一个警示语义组）。
不写任何零占比或假阳性倍数（无实测入口；方案 §6 W10 已明确剔除硬比例数字）。
图内汉字 = 方案清单逐字（零膨胀拖垮几何均值 9 / 尺寸因子模型崩溃 8 / 假阳性极端放大 7 /
不可照搬 4）＝ 28 字。红色一处语义组：第 ③ 行「假阳性极端放大」文字 + 底部徽标「不可照搬」。
瓶颈断裂锯齿用橙色（属「崩溃」语义，不再占红）。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 30_negbin_zero_inflation_collapse.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- ① 零膨胀矩阵 ----------------
CELL, GAP = 24, 8
PITCH = CELL + GAP
NONZERO = {1, 7, 14, 18}
for r in range(5):
    for c in range(4):
        s.rect(90 + c * PITCH, 92 + r * PITCH, CELL, CELL,
               BLUE if (r * 4 + c) in NONZERO else PANEL, rx=4)

# ---------------- ② 漏斗收窄 + 瓶颈断裂 ----------------
s.polygon([(82, 276), (262, 276), (200, 384), (144, 384)],
          BLUE_TINT, BLUE, 3)
s.path("M 144 384 L 158 370 L 172 396 L 200 384", ORANGE_DEEP, 6)

# ---------------- ③ 下口炸开 ----------------
for i, h in enumerate((44, 76, 34, 92, 58)):
    s.rect(92 + i * 34, 560 - h, 26, h,
           ORANGE_DEEP if i % 2 else ORANGE, rx=5)

# ---------------- 段间箭头 ----------------
s.arrow(172, 246, 172, 272, GRAY, 4, 12)
s.arrow(172, 392, 172, 430, GRAY, 4, 12)

# ---------------- 三行结论 ----------------
s.text(300, 176, "零膨胀拖垮几何均值", 32, BLUE, "start", "bold")
s.text(300, 340, "尺寸因子模型崩溃", 32, ORANGE_DEEP, "start", "bold")
s.text(300, 508, "假阳性极端放大", 32, RED, "start", "bold")

# ---------------- 唯一红处（第二组元素）：不可照搬 ----------------
s.chip(400, 642, "不可照搬", 34, WHITE, RED, RED, padx=32, pady=14)

s.save("30_negbin_zero_inflation_collapse.svg")

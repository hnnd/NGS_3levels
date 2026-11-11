#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_four_quadrant.py — FIG-M05-20 联合解读四象限（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.2 FIG-M05-20（P40，`.cols` 800×700，new-svg）。
教材依据：§15.4.7 L291–L302 的方向表（增强/减弱 × 上调/下调 → 候选激活、候选抑制、
激活因子的撤除；「增强 + 无变化」也是常见结果，不是失败）。

读图约定：横轴「可及性」向右＝由关到开，纵轴「转录」向上＝由降到升（方向由两支
箭头承担，不写「开/关/升/降」四个汉字，把字数让给方案原句）。
四象限：右上＝开 + 升（协同激活，绿）；左上＝关 + 升（阻遏释放，橙）；
左下＝关 + 降（协同沉默，紫）；右下＝开 + 降（抑制性重塑，橙）。

图内汉字 29 字（上限 30）：标题「多组学象限」5 ＋ 副题「可及性开闭与转录升降」10
＋ 结论「协同激活或阻遏机制」9 ＋ 轴名「可及性」3、「转录」2。
无警示语义，红不上图。无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 20_four_quadrant.py
"""
from svghelp import *

s = SVG()

s.text(400, 62, "多组学象限", 36, BLUE, "middle", "bold")
s.text(400, 108, "可及性开闭与转录升降", 30, GRAY, "middle")

# ---------------- 坐标系（居中于画布） ----------------
L, R, B, T = 176, 664, 470, 214
CX, CY = (L + R) / 2, (B + T) / 2

s.line(L, B, R, B, INK, 4)
s.line(L, B, L, T, INK, 4)
s.line(CX, B, CX, T, PANEL, 5, dash="14 10")
s.line(L, CY, R, CY, PANEL, 5, dash="14 10")

# 轴名 + 方向箭头（箭头即方向语义：右＝更可及，上＝更高表达）
s.text(L - 6, B + 50, "可及性", 30, GRAY, "start")
s.arrow(L + 112, B + 44, R - 20, B + 44, GRAY, 4, 16)
s.text(L - 18, T - 16, "转录", 30, GRAY, "end")
s.arrow(L - 44, B - 24, L - 44, T + 18, GRAY, 4, 16)

# ---------------- 四象限色块 ----------------
PAD = 12
QW, QH = (R - L) / 2 - 2 * PAD, (B - T) / 2 - 2 * PAD
CELLS = [
    ("Q1", CX + PAD, T + PAD, GREEN, GREEN_TINT, "↑"),        # 开 + 升：协同激活
    ("Q2", L + PAD, T + PAD, ORANGE, ORANGE_TINT, "↑"),       # 关 + 升：阻遏释放
    ("Q3", L + PAD, CY + PAD, PURPLE, PURPLE_TINT, "↓"),      # 关 + 降：协同沉默
    ("Q4", CX + PAD, CY + PAD, ORANGE, ORANGE_TINT, "↓"),     # 开 + 降：抑制性重塑
]
for tag, x, y, ink, fill, sym in CELLS:
    s.rect(x, y, QW, QH, fill, ink, 3, rx=14)
    s.text(x + QW - 20, y + 40, tag, 30, ink, "end", "bold")
    s.text(x + 22, y + QH - 16, sym, 36, ink, "start", "bold")

# 四格颜色与位置的图例语义（右下角小色块组，不写字）
s.text(400, 604, "协同激活或阻遏机制", 32, INK, "middle", "bold")

s.save("20_four_quadrant.svg")

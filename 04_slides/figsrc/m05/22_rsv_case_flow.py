#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""22_rsv_case_flow.py — FIG-M05-22 水稻抗条纹病毒案例的联合锁定路线（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.2 FIG-M05-22（P42，`.cols` 800×700，new-svg）。
教材依据：§15.4.7 L303–L308（RSV 案例：ATAC 与 RNA 各 1/3 个样本，差异可及性 6 462 开
/ 3 587 关，差异基因 5 461，交集后 motif 富集锁定 34 个候选 TF；证据层级是「候选关联」，
不是「某个元件调控某个基因」。案例原文 [@li2024rsv]）。

五级流程横向排列，最后一级用绿色表示「候选」而非「因果」。第四级额外标注来自
RNA 一侧的输入（DEG 芯片），说明交集发生在这里。
图内数字：34 个候选 TF 取自案例原文；另外两个数字（差异可及性区域、差异基因）不上图，
避免图面过载——它们写在右栏要点里。
图内汉字 23 字，逐字取方案原句：标题「联合锁定」4 ＋ 结论「差异开放区交集差异基因」11
＋「富集候选转录因子」8。流程盒内用工具名/符号（QC、MACS2、DAR、DEG、motif），不写英文句。
配色：ATAC 流向青蓝、RNA 流向紫、交集候选绿。无警示语义，红不上图。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 22_rsv_case_flow.py
"""
from svghelp import *

s = SVG()

s.text(400, 62, "联合锁定", 36, BLUE, "middle", "bold")

# ---------------- 五级流程 ----------------
BOX_W, BOX_H, GAP = 132, 132, 16
Y = 206
STAGES = [("QC", CYAN, CYAN_DEEP), ("MACS2", CYAN, CYAN_DEEP),
          ("DAR", CYAN, CYAN_DEEP), ("∩ DEG", PURPLE, "#5C6C8C"),
          ("motif", GREEN, GREEN)]
X0 = (800 - (5 * BOX_W + 4 * GAP)) / 2

for i, (lab, fill, ink) in enumerate(STAGES):
    x = X0 + i * (BOX_W + GAP)
    s.rect(x, Y, BOX_W, BOX_H, fill if i >= 3 else WHITE, ink, 4, rx=14)
    s.text(x + BOX_W / 2, Y + BOX_H / 2 + 12, lab, 32,
           WHITE if i >= 3 else ink, "middle", "bold")
    if i < 4:
        s.arrow(x + BOX_W + 1, Y + BOX_H - 24, x + BOX_W + GAP - 3,
                Y + BOX_H - 24, GRAY, 5, 14)

# ---------------- RNA 一侧的输入（DEG 芯片，自下而上进入第四级） ----------------
DX = X0 + 3 * (BOX_W + GAP)
s.rect(DX + 26, Y + BOX_H + 62, BOX_W - 52, 62, PURPLE_TINT, "#5C6C8C", 3, rx=12)
s.text(DX + BOX_W / 2, Y + BOX_H + 104, "DEG", 30, "#5C6C8C", "middle", "bold")
s.arrow(DX + BOX_W / 2, Y + BOX_H + 58, DX + BOX_W / 2, Y + BOX_H + 8,
        "#5C6C8C", 4, 14)

# ---------------- 末级产出：34 个候选 ----------------
LX = X0 + 4 * (BOX_W + GAP)
s.text(LX + BOX_W / 2, Y + BOX_H + 74, "34", 40, GREEN, "middle", "bold")

# ---------------- 结论（方案原句逐字） ----------------
s.text(400, 592, "差异开放区交集差异基因", 32, INK, "middle", "bold")
s.text(400, 652, "富集候选转录因子", 32, GREEN, "middle", "bold")

s.save("22_rsv_case_flow.svg")

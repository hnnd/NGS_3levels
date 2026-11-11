#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_design_card.py — FIG-M05-01 主线设计卡：12 个 ATAC run 与 m04 RNA-seq 一一对应

方案：`reviews/course/M05_FIGP_001.md` §4.1 FIG-M05-01（P10，`.cols` 一栏 800×700，new-svg）。
教材依据：§15.1 L12（2 处理 × 3 时点 × 2 重复 = 12 run，与第 14 章 12 个 RNA-seq 一一对应）。
图内汉字 = 方案原句逐字，共 27 字（标题 8 + 副题 12 + 结论 7）；其余标注为
处理代号 K/N、重复代号 A/B、时点数字与工具名 RNA。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 01_design_card.py
"""
from svghelp import *

s = SVG()

# ---- 方案原句（27 汉字）----
s.title("复氮时序十二样本")                        # 8
s.subtitle("对照与处理各三时点双重复")             # 12

# ---------------- 左：2 处理 × 3 时点 × 2 重复 ----------------
X0, RW, CG, CW, CH = 84, 6, 16, 148, 146
ROW_Y = {"K": 176, "N": 176 + CH + 74}
TINT = {"K": (CYAN, CYAN_DEEP), "N": (ORANGE, "#C0623F")}

for tag, y in ROW_Y.items():
    fill, ink = TINT[tag]
    s.text(X0 - 20, y + CH / 2 + 12, tag, 34, ink, "end", "bold")
    for i, t in enumerate(("30", "60", "120")):
        x = X0 + i * (CW + CG)
        s.rect(x, y, CW, CH, fill, ink, 4, rx=14)
        s.text(x + CW / 2, y + 44, t, 32, INK, "middle", "bold")
        for k, rep in enumerate(("A", "B")):
            cx = x + CW / 2 + (k - 0.5) * 52
            s.circle(cx, y + CH - 42, 19, WHITE, ink, 4)
            s.text(cx, y + CH - 31, rep, 30, INK, "middle", "bold")

# 时点轴
AX = X0 + 3 * (CW + CG) - CG
AY = ROW_Y["N"] + CH + 30
s.line(X0, AY, AX, AY, INK, 4)
s.text(AX + 8, AY + 10, "min", 30, GRAY, "start")

# ---------------- 右：与 m04 RNA-seq 的 1:1 配对 ----------------
PA_X, PA_W = 618, 150
PA_Y, PA_H = ROW_Y["K"], ROW_Y["N"] + CH - ROW_Y["K"]
s.rect(PA_X, PA_Y, PA_W, PA_H, WHITE, PURPLE, 4, rx=14)
s.text(PA_X + PA_W / 2, PA_Y + 46, "RNA", 32, PURPLE, "middle", "bold")
for g in range(4):                       # 12 个 RNA 样本：4 组 × 3 点
    for j in range(3):
        s.circle(PA_X + 44 + j * 34, PA_Y + 96 + g * 34, 10, PURPLE)
s.text(PA_X + PA_W / 2, PA_Y + PA_H - 26, "1:1", 32, BLUE, "middle", "bold")

# 配对箭头 + 「同批」标注
s.arrow(AX + 10, ROW_Y["K"] + CH / 2, PA_X - 12, ROW_Y["K"] + CH / 2,
        BLUE, 6, 16)
s.arrow(AX + 10, ROW_Y["N"] + CH / 2, PA_X - 12, ROW_Y["N"] + CH / 2,
        BLUE, 6, 16)

# ---- 结论行（7 汉字）----
s.bottom(["同批转录组配对"], y=636)
s.save("01_design_card.svg")

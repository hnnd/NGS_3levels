#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_binding_modes.py — FIG-M05-19 直接结合 / 共结合 / 间接招募（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.2 FIG-M05-19（P39，`.cols` 800×700，new-svg）。
教材依据：§15.4.6 L279–L283（motif 富集只给序列关联：可能是直接识别，可能是伴随因子
共占同一开放区，也可能是经蛋白复合体被拴系到 DNA 上、自身并不接触 DNA）。

图内汉字 29 字（上限 30）：标题「结合模式」4 ＋ 三卡说明逐字取方案原句
「直接识别结合」6、「共结合因子伴随」6、「间接蛋白招募」6 ＋ 结论「富集不等于接触」7。
三卡的机制差异由图说话：① 蛋白直接压在 motif 方块上；② 两个蛋白并肩各踩一个 motif；
③ 锚蛋白踩 motif、被招募的蛋白只经虚线接头悬在旁边（与 DNA 保持距离）。

配色：直接结合绿、共结合青蓝、间接招募橙（spec §2 辅助对比色）。无警示语义，
红不上图。无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 19_binding_modes.py
"""
from svghelp import *

s = SVG()

s.text(400, 62, "结合模式", 36, BLUE, "middle", "bold")

PX = [30, 280, 530]
PW, PY, PH = 240, 112, 424
DNA_Y = 372                                    # 卡内 DNA 轴 y
CAP_Y = 486                                    # 卡下说明块中心

CARDS = [("直接识别结合", GREEN, 0),
         ("共结合因子伴随", CYAN_DEEP, 1),
         ("间接蛋白招募", ORANGE, 2)]

for x, (cap, color, mode) in zip(PX, CARDS):
    s.panel(x, PY, PW, PH)

    # DNA 轴（双线示意双螺旋主链）
    s.line(x + 24, DNA_Y - 4, x + PW - 24, DNA_Y - 4, GRAY, 4)
    s.line(x + 24, DNA_Y + 4, x + PW - 24, DNA_Y + 4, GRAY, 4)

    if mode == 0:                               # ① 直接：蛋白压在 motif 上
        mx = x + PW / 2 - 30
        s.rect(mx, DNA_Y - 11, 60, 22, color, color, 3, rx=4)
        s.circle(x + PW / 2, DNA_Y - 72, 42, color, color, 3)
        s.line(x + PW / 2, DNA_Y - 30, x + PW / 2, DNA_Y - 13, color, 6)

    elif mode == 1:                             # ② 共结合：两蛋白并肩各踩一个 motif
        for dx in (-58, 58):
            cx = x + PW / 2 + dx
            s.rect(cx - 28, DNA_Y - 11, 56, 22, color, color, 3, rx=4)
            s.circle(cx, DNA_Y - 62, 32, color, color, 3)
            s.line(cx, DNA_Y - 30, cx, DNA_Y - 13, color, 6)
        s.line(x + PW / 2 - 30, DNA_Y - 62, x + PW / 2 + 30, DNA_Y - 62,
               color, 3, dash="10 8")

    else:                                       # ③ 间接：招募者悬空，不接触 DNA
        ax = x + PW / 2 - 68
        s.rect(ax - 28, DNA_Y - 11, 56, 22, GREEN, GREEN, 3, rx=4)
        s.circle(ax, DNA_Y - 64, 32, GREEN, GREEN, 3)
        s.line(ax, DNA_Y - 32, ax, DNA_Y - 13, GREEN, 6)
        rx_ = x + PW / 2 + 62                    # 被招募的蛋白：只在蛋白层面接触
        s.circle(rx_, DNA_Y - 134, 36, color, color, 3)
        s.line(ax + 24, DNA_Y - 84, rx_ - 30, DNA_Y - 114, color, 4, dash="13 9")

    s.label(x + PW / 2, CAP_Y, wrap(cap, 30, PW - 24), 30, color, weight="bold")

# ---------------- 结论：motif 富集只说明序列关联 ----------------
s.text(400, 604, "富集不等于接触", 32, INK, "middle", "bold")

s.save("19_binding_modes.svg")

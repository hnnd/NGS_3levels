#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""31_homer_motif_masking.py — FIG-M05-31 HOMER motif 搜索与屏蔽（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.3 FIG-M05-31（P53，`.cols` 800×700，new-svg）。
教材依据：§15.4.6 L259–L265、§15.6 L420–L421。HOMER `findMotifsGenome.pl` 以峰顶 summit
为中心取窗（默认 `-size 200`，即 summit ±100 bp），把前景序列的出现率与该工具自建的背景
序列集比对；`-mask` 把低复杂度与转座子重复序列在比对前打成 `N`，否则 Top motif 常被重复
家族的共有序列污染 [@heinz2010homer] [@homer2026docs]。

图面三段：① 峰轮廓＋summit＋200 bp 取窗括号（青蓝核心区）；② 取窗内两条序列行：上行
含一段重复序列（灰，被打叉屏蔽），下行同位置换成保留的匹配基序（绿）；③ 结论句。
上下行同位置对照，一眼看出「同一段窗口，只有非重复部分进入检验」。

图内汉字 28 字（上限 30），逐字取方案原句：标题「基序搜索」4 ＋「提取峰顶窗口」6
＋「屏蔽重复序列对比匹配背景」12 ＝ 22，加两行状态名「屏蔽前」3「屏蔽后」3 ＝ 28。
参数写拉丁字符（summit／200 bp／-mask）。
配色：峰顶核心区青蓝 `#4DBBD5`、重复序列屏蔽灰 `#8491B4`、匹配基序绿 `#00A087`。
无警示语义，红不上图。无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 31_homer_motif_masking.py
"""
import math

from svghelp import *

s = SVG()

s.text(400, 62, "基序搜索", 36, BLUE, "middle", "bold")

# ---------------- 上：峰轮廓 + summit + 200 bp 取窗 ----------------
PX0, PX1, PB, PH = 96, 704, 232, 104
pts = []
for i in range(0, 121):
    frac = i / 120.0
    x = PX0 + (PX1 - PX0) * frac
    y = PB - PH * math.exp(-((frac - 0.5) / 0.15) ** 2)
    pts.append((x, y))
s.curve(pts, CYAN_DEEP, 5)
s.line(PX0, PB, PX1, PB, INK, 4)

SUM_X = (PX0 + PX1) / 2
s.line(SUM_X, PB - PH, SUM_X, PB + 10, CYAN_DEEP, 4, dash="12 8")
s.text(SUM_X - 18, PB - PH - 12, "summit", 30, CYAN_DEEP, "end", "bold")

# 200 bp 取窗：summit ±100 bp 的括号（宽度按峰轮廓比例给出，非真实尺度）
WX0, WX1, WY = SUM_X - 118, SUM_X + 118, PB + 38
s.line(WX0, WY - 12, WX0, WY + 12, GREEN, 4)
s.line(WX1, WY - 12, WX1, WY + 12, GREEN, 4)
s.line(WX0, WY, WX1, WY, GREEN, 4)
s.text(SUM_X, WY + 48, "200 bp", 30, GREEN, "middle", "bold")

# ---------------- 中：取窗内两条序列行（屏蔽前 / 屏蔽后） ----------------
SEQ_X0, SEQ_W, SEQ_H = 200, 520, 36
REP0, REPW = 0.30, 0.34                       # 重复序列段在窗口中的位置与宽度
BLK0, BLK1 = SEQ_X0 + SEQ_W * REP0, SEQ_X0 + SEQ_W * (REP0 + REPW)

# 屏蔽前：重复序列（灰，打叉 = 不进入检验）
s.rect(SEQ_X0, 388, SEQ_W, SEQ_H, WHITE, PANEL, 3, rx=6)
s.rect(BLK0, 388, BLK1 - BLK0, SEQ_H, PURPLE, PURPLE, 3, rx=5)
s.line(BLK0 + 10, 388 + SEQ_H - 6, BLK1 - 10, 388 + 6, GRAY, 4)
s.line(BLK0 + 10, 388 + 6, BLK1 - 10, 388 + SEQ_H - 6, GRAY, 4)
s.text(BLK1 + 12, 388 + 27, "-mask", 30, GRAY, "start", "bold")
s.text(SEQ_X0 - 14, 388 + 27, "屏蔽前", 30, GRAY, "end", "bold")

# 屏蔽后：同位置的匹配基序（绿块保留）
s.rect(SEQ_X0, 452, SEQ_W, SEQ_H, WHITE, PANEL, 3, rx=6)
s.rect(BLK0, 452, BLK1 - BLK0, SEQ_H, GREEN, GREEN, 3, rx=5)
s.text(SEQ_X0 - 14, 452 + 27, "屏蔽后", 30, GREEN, "end", "bold")

# 两行同位置对照的引导括号
s.line(BLK0 - 18, 388 + SEQ_H / 2, BLK0 - 18, 452 + SEQ_H / 2, INK, 4)
s.line(BLK0 - 24, 388 + SEQ_H / 2, BLK0 - 12, 388 + SEQ_H / 2, INK, 4)
s.line(BLK0 - 24, 452 + SEQ_H / 2, BLK0 - 12, 452 + SEQ_H / 2, INK, 4)

# 取窗 → 序列行
s.arrow(SUM_X - 100, WY + 66, SUM_X - 100, 382, GRAY, 4, 14)

# ---------------- 结论（方案原句逐字，两句） ----------------
s.text(400, 570, "提取峰顶窗口", 32, BLUE, "middle", "bold")
s.text(400, 630, "屏蔽重复序列对比匹配背景", 32, INK, "middle", "bold")

s.save("31_homer_motif_masking.svg")
print(f"check: 取窗 200 bp = summit ±100 bp；屏蔽段占窗口 {REPW:.2f}（示意比例）")

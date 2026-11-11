#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""32_candidate_deg_venn.py — FIG-M05-32 候选基因与 DEG 交集（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.3 FIG-M05-32（P54，`.cols` 800×700，new-svg）。
教材依据：§15.4.7 L286–L290、§15.6 L421–L422。左侧韦恩展示「差异峰关联的候选基因」与
「第 14 章 DESeq2 差异表达基因」两集合的重叠；右侧引出交集大小的置换显著性检验——
交集大小没有解析零分布（取决于两个列表长度、基因密度与峰长分布），所以「重叠了很多个」
本身不是统计陈述，必须与置换零分布比 [@li2025nitrogen]。

图面**不写任何集合大小或交集计数**：§15.4.7 的 137 是设例，置换期望与零分布的具体数字
已在 FIG-M05-21 承载，本图只画「交集 → 置换检验」这一衔接动作，写第二遍数字会与 21 图
的口径分叉（同一数字两张图各自表述是 u06 返工过的类型）。

图内汉字 24 字（上限 30），逐字取方案原句「多组学求交：峰关联基因与差异表达基因集合互证」
加右侧检验项：标题「多组学求交」5 ＋ 两圈名「峰关联基因」5「差异表达基因」6
＋ 结论「集合互证」4 ＋「置换检验」4 = 24。轴只写拉丁术语 null／obs，不写整句英文。
配色按方案：表观峰基因青蓝 `#4DBBD5`、转录组 DEG 紫 `#8491B4`、交集核心绿 `#00A087`。
无警示语义，红不上图。无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 32_candidate_deg_venn.py
"""
import math

from svghelp import *

s = SVG()

s.text(400, 62, "多组学求交", 36, BLUE, "middle", "bold")

# ---------------- 左：两集合韦恩（交集用第三种颜色单独成块） ----------------
CX1, CX2, CY, RR = 172, 308, 290, 104
s.circle(CX1, CY, RR, CYAN, CYAN, 3)
s.circle(CX2, CY, RR, PURPLE, PURPLE, 3)
half = (CX2 - CX1) / 2.0                        # 交集＝两圆的透镜形
h = math.sqrt(max(RR ** 2 - half ** 2, 0))
mx = CX1 + half
s.path(f"M {mx:.1f} {CY - h:.1f} A {RR} {RR} 0 0 1 {mx:.1f} {CY + h:.1f} "
       f"A {RR} {RR} 0 0 1 {mx:.1f} {CY - h:.1f} Z", None, 0, fill=GREEN)

# 圈名：各贴本圈下方错开横位，同一条基线上，互不相撞
s.text(140, 452, "峰关联基因", 30, BLUE, "middle", "bold")
s.text(352, 452, "差异表达基因", 30, "#5C6C8C", "middle", "bold")

# ---------------- 右：交集 → 置换零分布 ----------------
AX0, AX1, AB, AT = 496, 762, 412, 236
s.line(AX0, AB, AX1, AB, INK, 4)
s.line(AX0, AB, AX0, AT, INK, 4)
s.text(AX0, AB + 46, "null", 30, GRAY, "start")
s.text(AX1, AB + 46, "obs", 30, GREEN, "end", "bold")

# 零分布柱（解析形状，非实测）：右偏，观察值落在右尾之外
BARS = 12
for i in range(BARS):
    frac = i / (BARS - 1.0)
    hgt = 64 * math.exp(-((frac - 0.22) / 0.30) ** 2)
    w = (AX1 - AX0) / BARS
    s.rect(AX0 + i * w + 3, AB - hgt, w - 6, hgt, PURPLE, None, rx=3)

OBS_X = AX1 - 20
s.line(OBS_X, AB, OBS_X, AT - 6, GREEN, 6, dash="14 9")

# 韦恩交集 → 零分布
s.arrow(420, 300, AX0 - 12, 356, GRAY, 5, 14)

# ---------------- 结论（方案原句逐字 ＋ 右侧检验项） ----------------
s.text(400, 556, "集合互证", 32, INK, "middle", "bold")
s.text(400, 620, "置换检验", 32, BLUE, "middle", "bold")

s.save("32_candidate_deg_venn.svg")
print(f"check: 零分布为解析形状（{BARS} 柱），obs 线在右尾之外；不标计数")

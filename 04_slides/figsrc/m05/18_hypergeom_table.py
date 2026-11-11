#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_hypergeom_table.py — FIG-M05-18 超几何检验四格表（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.2 FIG-M05-18（P38，`.cols` 800×700，new-svg）。
教材依据：§15.4.6 L267–L278 与引言 L18（超几何 `75/495` 属可手算那类）。
数据入口：`textbook/demos/ch15_motif_gc_background.py` Part 0 手算规则——
N = 12、K = 5、n = 4、k = 3 → P(X ≥ 3) = (C(5,3)C(7,1) + C(5,4)C(7,0)) / C(12,4)
= 75/495 = 0.152（直接调用 demo 里的手算实现，另以 math.comb 复核 75 与 495）。
四个格子由这组参数直接得出：
前景命中 3、未含 1；背景命中 5、未含 7。本脚本用超几何分布复算并断言 0.152。

图内汉字 29 字（规格上限 30）：
  标题「基序富集手算」6 ＋ 行名「前景」「背景」4
  ＋ 结论「前景阳性率对比匹配背景」11 ＋「超几何检验显著性」8。
四格与公式只用数字与符号。命中列彩色实填、未命中列白底彩框——颜色即列语义，
故不写「含/缺」列头（初版加列头连同行名把汉字顶到 31 字，且列头与行名相撞）。
配色：前景列青蓝、背景列紫、手算框深蓝。本图无警示语义，红不上图。
无网络；随机数不使用（纯组合数）。用法：PYTHONDONTWRITEBYTECODE=1 python3 18_hypergeom_table.py
"""
import sys
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]              # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from ch15_motif_gc_background import hypergeom_sf_hand   # noqa: E402

from svghelp import *                                    # noqa: F401,F403,E402

N, K, n, k = 12, 5, 4, 3                     # demo Part 0 手算参数
# 直接用 demo 里那支手算实现（math.comb 组合数），与 demo `--selftest` 打印的 0.152 同源
P_TAIL = float(hypergeom_sf_hand(k, N, K, n))
assert k <= n and k <= K and abs(P_TAIL - 0.152) < 5e-4, P_TAIL
assert abs(75 / 495 - P_TAIL) < 1e-12
assert comb(5, 3) * comb(7, 1) + comb(5, 4) * comb(7, 0) == 75
assert comb(12, 4) == 495
CELLS = {"f_hit": k, "f_miss": n - k, "b_hit": K, "b_miss": N - K}

s = SVG()

s.text(400, 62, "基序富集手算", 36, BLUE, "middle", "bold")

# ---------------- 四格表：前景 / 背景 × 命中 / 未命中 ----------------
CW, RH, GAPX = 150, 92, 10
X0, Y0 = 244, 168                            # 表体左上角
ROWS = [("前景", f"n = {n}", 0, CYAN, CYAN_DEEP, CELLS["f_hit"], CELLS["f_miss"]),
        ("背景", f"N = {N}", 1, PURPLE, "#5C6C8C", CELLS["b_hit"], CELLS["b_miss"])]
for name, tag, r, fill, ink, hit, miss in ROWS:
    y = Y0 + r * RH
    s.text(X0 - 28, y + 34, name, 32, ink, "end", "bold")
    s.text(X0 - 28, y + 72, tag, 30, GRAY, "end")
    for c, v in ((0, hit), (1, miss)):
        s.rect(X0 + c * (CW + GAPX), y, CW, RH, fill if c == 0 else WHITE, ink, 3, rx=10)
        s.text(X0 + c * (CW + GAPX) + CW / 2, y + RH / 2 + 12, str(v), 38,
               WHITE if c == 0 else ink, "middle", "bold")

TABLE_B = Y0 + 2 * RH                        # 表格下沿（箭头起点）

# ---------------- 手算框：一条公式 ----------------
FX, FY, FW, FH = 130, 430, 540, 108
s.rect(FX, FY, FW, FH, BLUE_TINT, BLUE, 4, rx=16)
s.text(FX + FW / 2, FY + 68, "P(X ≥ 3) = 75 / 495 = 0.152", 34, BLUE, "middle", "bold")

# 四格表 → 手算框（居中下行箭头）
s.arrow(400, TABLE_B + 16, 400, FY - 14, GRAY, 5, 16)

# ---------------- 结论（方案原句逐字） ----------------
s.text(400, 606, "前景阳性率对比匹配背景", 32, INK, "middle", "bold")
s.text(400, 662, "超几何检验显著性", 32, BLUE, "middle", "bold")

s.save("18_hypergeom_table.svg")
print(f"check: N/K/n/k = {N}/{K}/{n}/{k}；格 = {CELLS}；P(X≥3) = {P_TAIL:.4f}")

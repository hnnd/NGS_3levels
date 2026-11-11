#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_nucleosome_ladder.py — FIG-M05-14 核小体周期阶梯 vs 过度消化单峰（data-plot）

方案：`reviews/course/M05_FIGP_001.md` §4.2 FIG-M05-14（P34，`.cols` 800×700，data-plot）。
数据入口：`textbook/demos/ch15_atac_fragment_model.py` Part 1 合成算例——
正常 ATAC 直方图 60–99 bp 603、180–219 bp 310、380–419 bp 151（三模式阶梯）；
消化过度 100–139 bp 931（只剩单峰，周期信息丢失）。
本脚本按 demo 同种子、同调用顺序复算两组片段长度直方图并断言上图数字。

画法：左右两个独立面板（同一 40 bp bin、同一纵轴量程、同一 bp 刻度），
不做叠加折线——叠加时两条曲线互相穿越、数字标签压线，正是 u06 阶段返工的同类问题。
图内汉字 29 字：结论行 22（正常呈核小体周期阶梯 9 / 过度消化退化为单峰 9 / 片段分布 4）
＋面板名「正常」「过度」4 ＋纵轴「读段数」3；其余为 bp 刻度与 ~80／~200／~400 等 bin 中心数字。
红只用于过度消化面板（柱合成一条 path 1 处 + ~130 标注 1 处 = 2 处，唯一警示色上限内）。
无网络；随机数仅经 demo 同种子复算。
用法：PYTHONDONTWRITEBYTECODE=1 python3 14_nucleosome_ladder.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]              # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from ch15_atac_fragment_model import SEED, atac_ladder_lognorm_mix   # noqa: E402

from svghelp import *                                    # noqa: F401,F403,E402

N = 1500
rng = np.random.default_rng(SEED)
frag_atac = atac_ladder_lognorm_mix(rng, N)
frag_over = np.clip(np.round(rng.normal(130, 20, N)), 20, 1000).astype(int)
BINS = np.arange(20, 1021, 40)
H_ATAC, _ = np.histogram(frag_atac, bins=BINS)
H_OVER, _ = np.histogram(frag_over, bins=BINS)

# 与 demos --selftest Part 1 的打印值逐一相符
assert H_ATAC[:12].tolist() == [67, 603, 74, 51, 310, 81, 1, 1, 43, 151, 50, 0]
assert H_OVER[:12].tolist() == [0, 89, 931, 471, 8, 1, 0, 0, 0, 0, 0, 0]

K = 12                                        # 只画 20–499 bp：三个阶梯模式都在这一段
YMAX = 960.0
BASE, TOP = 468, 216
s = SVG()

s.text(400, 62, "片段分布", 36, BLUE, "middle", "bold")
s.text(96, 190, "读段数", 30, GRAY, "start")


def panel(x0, x1, hist, color, name, marks):
    """一个面板：柱按共用 YMAX 量程；name 写在面板左上；marks＝(bin, 文本)。"""
    w = (x1 - x0) / K
    bar_w = min(26, w - 12)
    s.line(x0, BASE, x1, BASE, INK, 4)
    s.line(x0, BASE, x0, TOP, INK, 4)
    s.text((x0 + x1) / 2, BASE + 88, name, 32,
           color if color != RED else INK, "middle", "bold")
    scale = (BASE - TOP) / YMAX
    d = " ".join(
        f"M {x0 + w * i + (w - bar_w) / 2} {BASE} "
        f"L {x0 + w * i + (w - bar_w) / 2} {BASE - hist[i] * scale:.1f} "
        f"L {x0 + w * i + (w + bar_w) / 2} {BASE - hist[i] * scale:.1f} "
        f"L {x0 + w * i + (w + bar_w) / 2} {BASE} Z"
        for i in range(K) if hist[i])
    s.path(d, color, 2, fill=color)
    for i, lab in marks:
        s.text(x0 + w * i + w / 2, BASE - hist[i] * scale - 16, lab, 30,
               color, "middle", "bold")


# ---- 左：正常 ATAC 的核小体阶梯（青蓝）----
panel(96, 400, H_ATAC, CYAN_DEEP, "正常",
      ((1, "~80"), (4, "~200"), (9, "~400")))

# ---- 右：过度消化只剩单峰（红：柱 path 1 处 + ~130 标注 1 处）----
panel(432, 736, H_OVER, RED, "过度", ((2, "~130"),))

# ---- bp 刻度（两侧面板共用；标在左面板下沿）----
for bp in (100, 200, 300, 400):
    x = 96 + (400 - 96) * (bp - 20) / (K * 40 - 20)
    s.line(x, BASE, x, BASE + 8, INK, 3)
    s.text(x, BASE + 42, str(bp), 30, GRAY, "middle")
s.text(736 + 8, BASE + 12, "bp", 30, GRAY, "start")

# ---- 结论行（方案原句 22 字，两行）----
s.text(400, 616, "正常呈核小体周期阶梯", 32, BLUE, "middle", "bold")
s.text(400, 668, "过度消化退化为单峰", 32, INK, "middle", "bold")

s.save("14_nucleosome_ladder.svg")
print(f"check: 正常 60–99={H_ATAC[1]} 180–219={H_ATAC[4]} 380–419={H_ATAC[9]}；"
      f"过度消化 100–139={H_OVER[2]}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""24_pipeline_eight_steps.py — FIG-M05-24 分析流程八步骨架（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.3 FIG-M05-24（P45，`.cols` 800×700，new-svg）。
教材依据：§15.6 L411–L422 的八步表（0 下载验收 → 1 比对清洗 → 2 检峰 FRiP →
3 轨道热图 → 4 IDR 重复 → 5 TxDb 注释 → 6 motif 搜索 → 7 多组学交集）。

画法：2 列 × 4 行的蛇形流水线（0→1 向右、1→2 向下、2→3 向左…… 7 落在末行左格），
比 8 行单列更宽裕，箭头逐段可读。盒内只写步骤号与工具名（英文/符号），
中文只承担方案原句——图内汉字 21 字正是方案给的额度：
标题「全流程八步」5 ＋ 结论两行「比对清洗、检峰质控」8、「一致重复、注释联合」8 = 21。
配色：上游 0–2 深蓝、核心 3–5 青蓝、下游 6–7 绿（spec §2 三段语义）。无警示语义，红不上图。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 24_pipeline_eight_steps.py
"""
from svghelp import *

s = SVG()

s.text(400, 62, "全流程八步", 36, BLUE, "middle", "bold")

BW, BH = 300, 76
LX, RX = 76, 424
Y0, PITCH = 132, 100

STEPS = [
    ("0", "FASTQ", BLUE), ("1", "BWA", BLUE),
    ("2", "MACS2", BLUE), ("3", "bigWig", CYAN_DEEP),
    ("4", "IDR", CYAN_DEEP), ("5", "TxDb", CYAN_DEEP),
    ("6", "HOMER", GREEN), ("7", "∩ DEG", GREEN),
]


def cell(i):
    """蛇形位置：行 = i // 2，0/2 行左→右，1/3 行右→左。"""
    row, col = divmod(i, 2)
    x = LX if (row % 2 == 0) == (col == 0) else RX
    return x, Y0 + row * PITCH


for i, (num, lab, color) in enumerate(STEPS):
    x, y = cell(i)
    s.rect(x, y, BW, BH, WHITE, color, 4, rx=14)
    s.circle(x + 44, y + BH / 2, 24, color, color, 3)
    s.text(x + 44, y + BH / 2 + 11, num, 32, WHITE, "middle", "bold")
    s.text(x + 96, y + BH / 2 + 12, lab, 32, color, "start", "bold")

# ---------------- 蛇形箭头 ----------------
for i in range(7):
    x, y = cell(i)
    nx, ny = cell(i + 1)
    if y == ny:                                  # 同一行：水平走一格
        if nx > x:                               # 向右
            s.arrow(x + BW + 4, y + BH / 2, nx - 8, y + BH / 2, GRAY, 5, 14)
        else:                                    # 向左
            s.arrow(x - 4, y + BH / 2, nx + BW + 8, y + BH / 2, GRAY, 5, 14)
    else:                                        # 换行：垂直下行
        cx = x + BW / 2
        s.arrow(cx, y + BH + 4, cx, ny - 8, GRAY, 5, 14)

# ---------------- 结论两行（方案原句逐字） ----------------
s.text(400, 596, "比对清洗、检峰质控", 32, INK, "middle", "bold")
s.text(400, 648, "一致重复、注释联合", 32, INK, "middle", "bold")

s.save("24_pipeline_eight_steps.svg")

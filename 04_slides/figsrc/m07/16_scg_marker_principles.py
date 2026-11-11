#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_scg_marker_principles.py — FIG-M07-18 单拷贝标记基因 SCG 计数原理

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-18（P34，`.cols` 一栏 800×700，new-svg；
文件名按序列号命名为 16_，对应方案图号 FIG-M07-18）。
教材依据：§19.4.5（谱系特异性单拷贝标记基因共 M 个座位：至少检出 1 份的座位比例 = 完整度；
超出单拷贝的副本总数 = 污染度）。
图内汉字 = 方案清单逐字，共 27 字（标记座位覆盖率：完整度 / 超额副本总数：污染度 / 超额标志混箱）。
矩阵只画「座位 × 副本」点阵：绿点 = 首份检出，红点 = 超额副本（×2 / ×3）；座位数与副本数
都是示意，不给百分比（比例没有可复现入口，不写数）。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 16_scg_marker_principles.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 座位 × 副本 点阵 ----------------
MX, MY, DX, DY = 104, 186, 86, 56
NCOL = 4
# 每行（座位）的副本份数：1 = 正常单拷贝；2/3 = 超额副本（混箱迹象）；0 = 座位缺失
COPIES = (1, 1, 0, 3, 2, 1, 1)

s.text(MX - 18, MY - 34, "座位", 30, GRAY, "start", "bold")

for r, n in enumerate(COPIES):
    y = MY + r * DY
    s.rect(MX - 46, y - 20, 40, 40, BLUE_TINT, BLUE, 3, rx=8)   # 座位格
    for c in range(NCOL):
        x = MX + 34 + c * DX
        s.circle(x, y, 15, PANEL)                               # 空槽
        if c < n:
            s.circle(x, y, 15, GREEN if c == 0 else RED)

# ---------------- 右侧：两条判读 ----------------
s.rect(444, 122, 316, 150, GREEN_TINT, GREEN, 4, rx=16)
s.label(602, 197, ["标记座位", "覆盖率：完整度"], 30, GREEN, "middle", "bold")

s.rect(444, 300, 316, 150, RED_TINT, RED, 4, rx=16)
s.label(602, 375, ["超额副本", "总数：污染度"], 30, RED, "middle", "bold")

# ---------------- 警示框 ----------------
s.rect(100, 556, 616, 104, WHITE, RED, 4, rx=16, dash="12 9")
s.text(400, 622, "超额标志混箱", 36, RED, "middle", "bold")

s.save("16_scg_marker_principles.svg")

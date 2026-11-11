#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""23_dual_track_pipeline.py — FIG-M07-26 实践操作双轨路线：主脚本流程与手动扩展

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-26（P45，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.3、§19.6（主脚本一条线五步通：去宿主 → MEGAHIT 组装 → depth/MetaBAT2 出箱 →
CheckM 1.x 验收 → eggNOG-mapper 注释；质控分类共识另走手动轨：fastp / Kraken2 / Bracken /
DAS Tool）。主轨第 3 步把 depth 与 MetaBAT2 合并为一步，故正好五步。
版式：左右两列，中间一条红色虚线为「脚本边界」——左列在脚本内、右列要自己串；
每步一行「序号 + 工具名」，工具名允许英文（字段名），中文只写两轨标题与红字结论。
图内汉字 = 方案清单逐字，共 25 字（主脚本：单样本五步通 / 手动轨：质控分类共识 /
认清脚本边界）。
红色一处：「认清脚本边界」文字 + 中间边界虚线属同一语义组。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 23_dual_track_pipeline.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

COLW, TOP, PITCH, RH = 336, 196, 78, 56
COLS = (
    (32, "主脚本：单样本五步通", BLUE, BLUE_TINT,
     ("host", "MEGAHIT", "depth+MetaBAT2", "CheckM", "emapper")),
    (432, "手动轨：质控分类共识", CYAN_DEEP, CYAN_TINT,
     ("fastp", "Kraken2", "Bracken", "DAS Tool")),
)

for x, cap, edge, tint, steps in COLS:
    s.rect(x, TOP - 72, COLW, 60, tint, edge, 3, rx=14)
    s.text(x + COLW / 2, TOP - 32, cap, 30, edge, "middle", "bold")
    for i, name in enumerate(steps):
        y = TOP + i * PITCH
        s.rect(x, y, COLW, RH, WHITE, edge, 3, rx=10)
        s.rect(x, y, 50, RH, edge, rx=10)              # 序号底色块
        s.text(x + 25, y + RH / 2 + 11, str(i + 1), 30, WHITE, "middle", "bold")
        s.text(x + 72, y + RH / 2 + 11, name, 30, edge, "start", "bold")
        if i:
            s.arrow(x + 25, y - PITCH + RH + 2, x + 25, y - 4, edge, 3, 9)

# ---------------- 红色语义组：中间边界虚线 + 「认清脚本边界」 ----------------
s.line(400, 116, 400, 620, RED, 4, dash="12 10")
s.text(400, 686, "认清脚本边界", 32, RED, "middle", "bold")

s.save("23_dual_track_pipeline.svg")

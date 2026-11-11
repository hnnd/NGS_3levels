#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_reproducibility_crisis_trail.py — FIG-M08-01 可重复性困境与断裂链条（P09，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-01（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.1（审稿人审计 padj 阈值与独立过滤，半年后重跑对不上）。
图内汉字 = 方案原句逐字，共 29 字（审稿人审计质询 / 路径断裂 / 版本漂移 /
参数未留痕 / 历史覆盖 / 重跑对不上）；其余只有 ASCII 路径、版本号与命令行参数。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 01_reproducibility_crisis_trail.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

# 四个断裂点：(图内文字, ASCII 佐证)
BREAKS = [
    ("路径断裂", "/data/old/results"),
    ("版本漂移", "fastp 0.23.4"),
    ("参数未留痕", "--qual 20"),
    ("历史覆盖", ".bash_history"),
]

CW, CH = 350, 124
CELLS = [(30, 214), (420, 214), (30, 360), (420, 360)]


def main():
    s = SVG()

    # 顶部：审稿人质询（深蓝）+ 阈值注记
    s.rect(180, 40, 440, 96, BLUE_TINT, BLUE, 4, rx=16)
    s.text(400, 104, "审稿人审计质询", 34, BLUE, "middle", "bold")
    s.text(400, 176, "padj < 0.05", 30, GRAY, "middle")

    # 质询 → 四个断点（青蓝数据流；避开中央的阈值注记）
    for x, y in ((212, 214), (588, 214)):
        s.arrow(x, 146, x, y - 8, CYAN, 5, 16)
    for x, y in ((205, 360), (595, 360)):
        s.arrow(x, 346, x, y - 8, CYAN, 5, 16)

    # 四个断裂点卡（2×2）：图内文字 + ASCII 佐证
    for (x, y), (txt, ascii_hint) in zip(CELLS, BREAKS):
        s.rect(x, y, CW, CH, WHITE, ORANGE, 4, rx=14)
        s.text(x + CW / 2, y + 52, txt, 32, INK, "middle", "bold")
        s.text(x + CW / 2, y + 100, ascii_hint, 30, GRAY, "middle")

    # 断点 → 后果（青蓝）
    for x in (205, 595):
        s.arrow(x, 492, x, 526, CYAN, 5, 16)

    # 底部红色警示：半年后重跑对不上
    s.rect(140, 534, 520, 96, RED_TINT, RED, 5, rx=16)
    s.text(400, 596, "重跑对不上", 40, RED, "middle", "bold")

    return s.save("01_reproducibility_crisis_trail.svg")


if __name__ == "__main__":
    raise SystemExit(main())

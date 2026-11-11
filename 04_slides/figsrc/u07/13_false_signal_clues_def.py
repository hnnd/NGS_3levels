#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_false_signal_clues_def.py — 生成 13_false_signal_clues_def.svg（FIG-U07-13：三类假信号线索量化定义）

方案：reviews/course/U07_FIGP_001.md §4.2 FIG-U07-13（P36，cols 一栏，viewBox 800×700）。
数据：无量字数字。链偏＝alt 中正链占比偏离 0.5；末端聚集＝变异落入读段两端
5–10 bp 窗口；MAPQ=0＝多重比对位置不唯一（教材 §9.4.7 L286–300）。
卡片标题用英文（汉字预算 28 已满）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 13_false_signal_clues_def.py
"""
from svghelp import *  # noqa: F401,F403

CARDS = [(20, 260, "strand bias"), (280, 520, "end bias"),
         (540, 780, "MAPQ = 0")]


def main():
    s = SVG(800, 700)
    for x0, x1, title in CARDS:
        s.rect(x0, 50, x1 - x0, 520, WHITE, PANEL, 3, rx=16)
        s.text((x0 + x1) / 2, 100, title, 30, BLUE, "middle", "bold")

    # 卡 1：链偏——0.5 参考虚线 + 正链占比条偏离
    for i, c in enumerate((ORANGE, ORANGE, ORANGE, PURPLE)):
        s.rect(90 + i * 42, 160, 34, 60, c, rx=6)
    s.line(140, 150, 140, 330, GRAY, 4, dash="12 10")
    s.text(140, 142, "0.5", 30, GRAY, "middle")
    s.rect(140, 250, 84, 30, ORANGE, rx=6)
    s.text(232, 275, "0.9", 30, GRAY, "start")
    s.text(140, 480, "链偏：", 32, BLUE, "middle", "bold")
    s.text(140, 528, "正链占比偏离", 32, BLUE, "middle", "bold")

    # 卡 2：末端聚集——150 bp 读段，两端 5–10 bp 红色窗口（唯一红色）
    s.rect(298, 210, 204, 48, WHITE, GRAY, 4, rx=10)
    s.rect(298, 210, 32, 48, RED_TINT, RED, 5, rx=10)
    s.rect(470, 210, 32, 48, RED_TINT, RED, 5, rx=10)
    for wx in (312, 324, 482, 494):
        s.line(wx, 222, wx, 246, ORANGE, 5)
    s.text(400, 190, "150 bp", 30, GRAY, "middle")
    s.text(400, 300, "5–10 bp", 30, GRAY, "middle")
    s.text(400, 480, "末端：", 32, BLUE, "middle", "bold")
    s.text(400, 528, "落入端部窗口", 32, BLUE, "middle", "bold")

    # 卡 3：MAPQ=0——白色空心 read 堆叠，箭头指向多处匹配
    for yy in (160, 228, 296):
        s.rect(565, yy, 110, 36, WHITE, GRAY, 4, rx=8, dash="10 8")
        s.arrow(678, yy + 18, 716, yy + 18, GRAY, 4, head=10)
        s.circle(742, yy + 18, 14, PANEL, GRAY, 4)
    s.text(660, 380, "MAPQ = 0", 30, GRAY, "middle")
    s.text(660, 528, "重复区不可信", 32, BLUE, "middle", "bold")

    # 底部统一标注（方案版式行，汉字预算内）
    s.text(400, 640, "量化线索", 34, BLUE, "middle", "bold")

    s.save("13_false_signal_clues_def.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

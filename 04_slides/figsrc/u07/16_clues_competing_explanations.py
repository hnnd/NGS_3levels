#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_clues_competing_explanations.py — 生成 16_clues_competing_explanations.svg（FIG-U07-16：假信号竞争解释矩阵）

方案：reviews/course/U07_FIGP_001.md §4.2 FIG-U07-16（P40，cols 一栏，viewBox 800×700）。
数据：无量字数字。三类线索的非变异技术竞争解释：显示过滤藏起一链 /
微错位致末端假象 / 多重比对非必错；行动＝先降信任补证据
（教材 §9.4.7 L312–324「竞争解释表」、§9.5.3）。汉字恰 30，栏题用英文。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 16_clues_competing_explanations.py
"""
from svghelp import *  # noqa: F401,F403

COLS = [
    (30, 250, "strand bias", CYAN_DEEP, ["显示过滤", "藏起一链"]),
    (290, 510, "end bias", BLUE, ["微错位致", "末端假象"]),
    (550, 770, "MAPQ = 0", PURPLE, ["多重比对", "非必错"]),
]


def main():
    s = SVG(800, 700)
    for x0, x1, title, color, lines in COLS:
        cx = (x0 + x1) / 2
        s.text(cx, 88, title, 30, BLUE, "middle", "bold")
        s.rect(x0, 116, x1 - x0, 200, WHITE, PANEL, 3, rx=14)
        s.rect(x0, 366, x1 - x0, 150, WHITE, color, 6, rx=14)
        for j, ln in enumerate(lines):
            s.text(cx, 426 + j * 46, ln, 32, color, "middle", "bold")

    # 卡 1：显示过滤——过滤带藏起反链读段
    for i in range(3):
        s.rect(52 + i * 34, 150, 28, 52, ORANGE, rx=5)
    s.rect(170, 140, 26, 150, PANEL, GRAY, 4, dash="10 8", rx=6)
    for i in range(2):
        s.rect(206 + i * 30, 150, 24, 52, "none", PURPLE, 4, dash="8 6",
               rx=5)
    s.text(140, 296, "filter", 30, GRAY, "middle")

    # 卡 2：局部微错位——上下两行错位的比对块 + indel tick
    for i in range(4):
        s.rect(306 + i * 46, 156, 40, 40, BLUE_TINT, BLUE, 3, rx=5)
    for i in range(4):
        off = 18 if i >= 2 else 0
        s.rect(306 + i * 46 + off, 226, 40, 40, BLUE_TINT, BLUE, 3, rx=5)
    s.line(398, 146, 398, 282, ORANGE, 5, dash="12 9")
    s.text(400, 296, "indel", 30, GRAY, "middle")

    # 卡 3：多重比对——空心 read 指向两个落点
    s.rect(566, 176, 100, 36, WHITE, GRAY, 4, dash="10 8", rx=8)
    s.arrow(670, 194, 712, 160, GRAY, 4, head=11)
    s.arrow(670, 194, 712, 226, GRAY, 4, head=11)
    s.circle(736, 152, 13, PANEL, GRAY, 4)
    s.circle(736, 234, 13, PANEL, GRAY, 4)
    s.text(660, 296, "multi-map", 30, GRAY, "middle")

    # 底部跨栏红色行动指南（唯一红色）
    s.rect(190, 580, 420, 60, RED, rx=12)
    s.text(400, 622, "先降信任补证据", 34, WHITE, "middle", "bold")

    s.save("16_clues_competing_explanations.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

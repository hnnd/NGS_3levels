#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_markduplicates_key.py — 生成 06_markduplicates_key.svg
（FIG-M03-09：MarkDuplicates 双端判定键与 0x400 打标机制）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-09（P21，cols 一栏，800×700）。
图内中文按方案（两端坐标 插入长度 相同判定 重复打标 保留最优读段）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文，工具名/字段名/
命令/参数保留英文，字数不再按 ≤30 字核验。依据：教材 §10.4.2（L108–121）、
§10.5.1。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def pair(s, y, x1, x2, col, w=76):
    s.line(x1, y + 16, x2 + w, y + 16, PANEL, 10)
    s.rect(x1, y, w, 32, col, None, rx=4)
    s.rect(x2, y, w, 32, col, None, rx=4)
    s.line(x1, y - 10, x1, y + 42, INK, 5)
    s.line(x2 + w, y - 10, x2 + w, y + 42, INK, 5)
    s.polygon([(x1, y + 16), (x1 + 15, y + 5), (x1 + 15, y + 27)], INK)
    s.polygon([(x2 + w, y + 16), (x2 + w - 15, y + 5), (x2 + w - 15, y + 27)],
              INK)


def main():
    s = SVG(800, 700)
    s.text(400, 48, "MarkDuplicates 判定键", 36, INK, "middle", "bold")

    s.line(60, 84, 740, 84, BLUE, 5)
    for i in range(11):
        s.line(72 + i * 62, 76, 72 + i * 62, 92, BLUE, 3)

    # 同文库两对（坐标完全一致）
    s.rect(50, 104, 700, 280, WHITE, PANEL, 3, rx=14)
    s.text(130, 142, "LB:lib1", 30, GREEN, "middle", "bold")
    pair(s, 150, 180, 480, CYAN)
    pair(s, 260, 180, 480, CYAN)
    s.text(115, 224, "两端坐标", 30, BLUE, "middle", "bold")
    s.text(655, 150, "方向一致", 30, BLUE, "middle", "bold")
    s.darrow(196, 222, 556, 222, PURPLE, 5, head=13)
    s.text(376, 250, "插入长度", 30, PURPLE, "middle", "bold")
    s.line(290, 302, 462, 302, RED, 5)
    s.text(376, 338, "相同判定", 32, RED, "middle", "bold")

    # 跨文库不比对
    s.rect(50, 410, 320, 130, WHITE, PANEL, 3, rx=14)
    s.text(140, 448, "LB:lib2", 30, GREEN, "middle", "bold")
    pair(s, 468, 110, 250, ORANGE)
    s.text(215, 506, "跨文库", 30, GRAY, "middle", "bold")
    s.text(215, 538, "不比对", 30, GRAY, "middle", "bold")

    # 动作分流
    s.rect(410, 410, 340, 220, WHITE, PANEL, 3, rx=14)
    s.text(580, 448, "打标不删", 30, RED, "middle", "bold")
    s.rect(430, 460, 300, 66, GREEN_TINT, GREEN, 4, rx=10)
    s.text(580, 503, "保留最优读段", 32, GREEN, "middle", "bold")
    s.rect(430, 540, 300, 78, ORANGE_TINT, ORANGE, 4, rx=10)
    s.text(580, 574, "0x400", 32, ORANGE, "middle", "bold")
    s.text(580, 606, "重复打标", 30, ORANGE, "middle", "bold")

    s.arrow(376, 346, 376, 366, RED, 6)
    s.line(376, 366, 580, 366, GRAY, 5)
    s.arrow(580, 366, 580, 410, GRAY, 6)
    s.arrow(215, 366, 215, 410, GRAY, 6)
    s.line(215, 366, 376, 366, GRAY, 5)
    s.text(400, 668, "判定键 = 两端 5′ 坐标 + 方向 + 插入长度", 30,
           GRAY, "middle")
    s.save("06_markduplicates_key.svg")


if __name__ == "__main__":
    main()

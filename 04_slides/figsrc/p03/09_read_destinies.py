#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_read_destinies.py — 生成 09_read_destinies.svg
（FIG-P03-09：第 21 页 cols 一栏「竞争比对读段有向流与歧义三归宿」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-09（P21，cols，800×700）。
依据：教材 §16.4.2 L141–157（合并参考一次竞争比对后读段有三种出口：唯一比对到
某一侧、因多处命中被过滤、两侧都没比对；顺序归属把歧义全部倾斜给先比的一方且
后端不可见；EM 分摊是概率分摊不是物理归属、仍需 Mock 校准本底）、§16.5.1 L385。
图内中文严格取方案给定 30 字（4 句）。宿主/病原用深蓝/浅橙两条通路表达，非歧义与
歧义的分流用节点颜色区分，不加额外中文。
配色：绿色示唯一比对正常定量与可审计剔除，红色标顺序过滤偏袒（唯一警示），
紫色示软分配；青蓝示歧义多重比对节点。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 09_read_destinies.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["唯一比对正常定量", "竞争剔除可审计", "顺序过滤偏袒先比", "概率分摊带本底"]
TEXT = "".join(PHRASES)


def read(s, x, y):
    """一条读段：短粗棒。"""
    s.rect(x, y, 46, 14, BLUE, None, 0, rx=7)


def main():
    s = SVG(800, 700, "Three destinies of a read", plan=TEXT)

    # ---------- 顶部：双参考复合索引（深蓝宿主 + 浅橙病原）----------
    s.rect(232, 44, 336, 22, BLUE, None, 0, rx=8)
    s.rect(232, 70, 336, 22, ORANGE, None, 0, rx=8)
    read(s, 96, 44)
    s.arrow(152, 66, 224, 66, CYAN, 6, 16)

    # ---------- 分流：左右两支唯一比对 + 中支歧义多重比对 ----------
    s.path("M 300 96 L 190 178", GREEN, 5)
    s.path("M 400 96 L 400 168", CYAN, 5)
    s.path("M 500 96 L 610 178", GREEN, 5)

    for x, col in ((150, BLUE), (592, ORANGE)):
        s.circle(x, 208, 30, WHITE, col, 4)
        s.text(x, 220, "1", 30, col, "middle", "bold")

    s.circle(400, 208, 34, CYAN_TINT, CYAN, 5)
    s.text(400, 220, "2+", 30, CYAN_DEEP, "middle", "bold")

    # ---------- 三个出口：唯一比对定量 / 竞争剔除 / 顺序过滤 ----------
    s.rect(60, 336, 210, 130, GREEN_TINT, GREEN, 4, rx=14)
    s.text(165, 380, PHRASES[0][:4], 30, GREEN, "middle", "bold")
    s.text(165, 426, PHRASES[0][4:], 30, GREEN, "middle", "bold")
    s.arrow(150, 244, 150, 328, GREEN, 6, 16)

    s.rect(292, 336, 216, 130, BLUE_TINT, BLUE, 4, rx=14)
    s.text(400, 380, PHRASES[1][:4], 30, BLUE, "middle", "bold")
    s.text(400, 426, PHRASES[1][4:], 30, BLUE, "middle", "bold")
    s.arrow(400, 248, 400, 328, BLUE, 6, 16)

    s.rect(546, 336, 200, 130, RED_TINT, RED, 4, rx=14)
    s.text(646, 380, PHRASES[2][:4], 30, RED, "middle", "bold")
    s.text(646, 426, PHRASES[2][4:], 30, RED, "middle", "bold")
    s.arrow(610, 240, 646, 328, RED, 6, 16)

    # ---------- 第四个出口：概率分摊（软分配）----------
    s.rect(292, 512, 216, 118, PURPLE_TINT, PURPLE, 4, rx=14)
    s.text(400, 556, PHRASES[3][:4], 30, PURPLE, "middle", "bold")
    s.text(400, 600, PHRASES[3][4:], 30, PURPLE, "middle", "bold")
    for i in range(6):                                   # 概率扇形示意
        s.polygon([(400, 512), (368 + i * 13, 512), (400, 512)], PURPLE, None, 0)
    s.save("09_read_destinies.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())

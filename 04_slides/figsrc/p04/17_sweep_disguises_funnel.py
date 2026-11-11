#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_sweep_disguises_funnel.py — 生成 17_sweep_disguises_funnel.svg
（FIG-P04-17：第 33 页 cols 一栏「四类伪装者与排除规程」）【new-svg】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-17（P33，cols，800×700）。
依据：教材 §20.4.6 的四类伪装者——① 人口历史（瓶颈/扩张让全基因组 D_T 整体
偏移，极值满地）：只用全基因组经验分位数（top 1%）；② 低重组区与背景选择
（π 本底偏低）：按重组率分层或单独标注；③ 隐秘结构（Wahlund 同时抬高 F_ST、
扭曲频谱）：先结构推断，在明确定义的分群内部扫描；④ 软清除（π 不塌、单倍型
不唯一）：转向单倍型多样性与频率时序。
图内中文严格取方案给定 30 字（4 句）；D_T、π、F_ST 与数字属符号。
结构＝四张「假信号（左：图形）→ 排除动作（右：判读句）」的排查卡；
第四张（软清除）的动作用「单倍型补验」四个字承载。
红只标「全基因组用经验分位」这一条核心红线。
无网络；不涉及随机数（图形为示意）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 17_sweep_disguises_funnel.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["全基因组用经验分位", "按重组率分层排查", "明确分群内部扫描", "单倍型补验"]
TEXT = "".join(PHRASES)


def icon_history(s, cx, cy, color):
    """人口历史：整条染色体上到处是极值峰。"""
    s.line(cx - 120, cy + 24, cx + 120, cy + 24, color, 4)
    for dx, h in ((-104, 42), (-62, 30), (-18, 52), (26, 34), (70, 46), (108, 28)):
        s.line(cx + dx, cy + 24, cx + dx, cy + 24 - h, color, 4)
        s.circle(cx + dx, cy + 18 - h, 6, color)


def icon_recomb(s, cx, cy, color):
    """低重组区：一段被压低的 π 本底。"""
    s.line(cx - 120, cy - 10, cx + 120, cy - 10, color, 4)
    s.polyline([(cx - 120, cy - 10), (cx - 60, cy - 10), (cx - 40, cy + 24),
                (cx + 40, cy + 24), (cx + 60, cy - 10), (cx + 120, cy - 10)],
               color, 5)
    for dx in (-40, 40):
        s.line(cx + dx, cy - 26, cx + dx, cy + 38, GRAY, 3, dash="8 7")


def icon_structure(s, cx, cy, color):
    """隐秘结构：合并前的两套分层。"""
    s.circle(cx - 52, cy, 40, WHITE, BLUE, 4)
    s.circle(cx + 52, cy, 40, WHITE, color, 4)
    for dy in (-14, 8):
        s.line(cx - 84, cy + dy, cx - 20, cy + dy, BLUE, 4)
        s.line(cx + 20, cy + dy, cx + 84, cy + dy, color, 4)
    s.arrow(cx - 12, cy - 44, cx + 12, cy - 44, GRAY, 4, 11)


def icon_softhard(s, cx, cy, color):
    """软清除：两条单倍型各自带不同来源的色块。"""
    for i, y in enumerate((cy - 22, cy + 14)):
        s.rect(cx - 110, y, 220, 26, WHITE, GRAY, 3, rx=6)
    for x0, w, c in ((-110, 60, color), (-30, 40, BLUE), (30, 50, ORANGE),
                     (90, 20, color)):
        s.rect(cx + x0, cy - 22, w, 26, c, None, 0, rx=4)
    for x0, w, c in ((-110, 40, BLUE), (-50, 60, color), (30, 30, PURPLE),
                     (80, 30, BLUE)):
        s.rect(cx + x0, cy + 14, w, 26, c, None, 0, rx=4)


def main():
    s = SVG(800, 700, "Four disguises of a sweep signal", plan=TEXT)

    cards = [
        (30, 52, icon_history, BLUE, BLUE_TINT, PHRASES[0], RED),
        (410, 52, icon_recomb, CYAN_DEEP, CYAN_TINT, PHRASES[1], CYAN_DEEP),
        (30, 336, icon_structure, PURPLE, PURPLE_TINT, PHRASES[2], BLUE),
        (410, 336, icon_softhard, ORANGE, ORANGE_TINT, PHRASES[3], INK),
    ]
    for x, y, icon, col, tint, phrase, tcol in cards:
        s.rect(x, y, 360, 268, tint, col, 4, rx=14)
        icon(s, x + 180, y + 96, col)
        s.line(x + 24, y + 186, x + 336, y + 186, PANEL, 3)
        s.text(x + 180, y + 236, phrase, 30, tcol, "middle", "bold")

    s.save("17_sweep_disguises_funnel.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())

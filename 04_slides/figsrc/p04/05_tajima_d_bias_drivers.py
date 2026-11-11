#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_tajima_d_bias_drivers.py — 生成 05_tajima_d_bias_drivers.svg
（FIG-P04-05：第 18 页 cols 一栏「Tajima's D 偏离方向与驱动力」）【new-svg】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-05（P18，cols，800×700）。
依据：教材 §20.4.1 L143–155 的判读表——显著负值＝稀有位点富集（局部正选择后的
新突变积累、全基因组背景纯化选择、近期扩张）；显著正值＝中间频率富集
（局部平衡选择、瓶颈收缩、样本混入分化亚群）；单一统计量分不开机制，
只能放到全基因组分布里取经验分位数。
图内中文严格取方案给定 30 字（4 句）；D_T 与数字属符号；两个驱动力只用图形
象征（局部清除＝区段中心多样性塌陷＋星标，扩张＝同心外扩箭头；平衡选择＝
蜂巢状天平，瓶颈＝收窄漏斗），不再加中文标注，避免超出方案的 30 字上限。
红色只标底部的经验分位数判读一处。
无网络；不涉及随机数（两侧频谱为示意形状）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 05_tajima_d_bias_drivers.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["负值稀有端富集", "清除新突变或扩张", "正值中间频率过量", "经验分位数判读"]
TEXT = "".join(PHRASES)


def spectrum(s, xc, base, heights, color, w=30, gap=15):
    n = len(heights)
    x0 = xc - (n * (w + gap) - gap) / 2
    for i, h in enumerate(heights):
        s.rect(x0 + i * (w + gap), base - h, w, h, WHITE, color, 3, rx=4)


def sweep_icon(s, cx, cy, color):
    """局部清除：区段中心多样性塌陷（V 形坑），坑底一颗星标。"""
    s.line(cx - 52, cy - 8, cx + 52, cy - 8, color, 5, cap="round")
    s.polyline([(cx - 52, cy - 8), (cx - 30, cy - 8), (cx - 14, cy + 26),
                (cx, cy + 26), (cx + 14, cy - 8), (cx + 52, cy - 8)],
               color, 5)
    s.circle(cx, cy + 26, 9, color)


def growth_icon(s, cx, cy, color):
    """扩张：同心外扩箭头。"""
    for r in (14, 28):
        s.circle(cx, cy, r, "none", color, 4)
    s.arrow(cx + 34, cy, cx + 54, cy, color, 5, 12)


def balance_icon(s, cx, cy, color):
    """平衡选择：天平（两盘等重）。"""
    s.line(cx, cy - 30, cx, cy + 26, color, 4)
    s.line(cx - 36, cy - 26, cx + 36, cy - 26, color, 5)
    for dx in (-34, 34):
        x = cx + dx
        s.line(x, cy - 26, x, cy - 6, color, 3)
        s.path(f"M {x - 16} {cy - 6} Q {x} {cy + 12} {x + 16} {cy - 6}",
               color, 4)


def bottleneck_icon(s, cx, cy, color):
    """瓶颈：通道收窄。"""
    s.polygon([(cx - 44, cy - 32), (cx + 44, cy - 32), (cx + 44, cy - 20),
               (cx - 44, cy - 20)], color)
    s.polygon([(cx - 44, cy + 32), (cx + 44, cy + 32), (cx + 44, cy + 20),
               (cx - 44, cy + 20)], color)
    s.arrow(cx, cy - 10, cx, cy + 12, color, 4, 11)


def main():
    s = SVG(800, 700, "Tajima D sign and its confounded drivers", plan=TEXT)

    # ---------- 左右两面板 ----------
    s.panel(30, 48, 350, 470, BLUE_TINT, BLUE, 4)
    s.panel(420, 48, 350, 470, ORANGE_TINT, ORANGE, 4)

    # 左：负值（稀有端富集）
    s.text(205, 108, PHRASES[0], 30, BLUE, "middle", "bold")
    spectrum(s, 205, 300, [150, 96, 58, 34, 22, 16], BLUE)
    sweep_icon(s, 145, 372, BLUE)
    growth_icon(s, 272, 372, BLUE)
    s.text(205, 456, PHRASES[1], 30, CYAN_DEEP, "middle", "bold")

    # 右：正值（中间频率过量）
    s.text(595, 108, PHRASES[2], 30, ORANGE, "middle", "bold")
    spectrum(s, 595, 300, [30, 66, 122, 154, 122, 66, 30], ORANGE)
    balance_icon(s, 535, 372, ORANGE)
    bottleneck_icon(s, 662, 372, ORANGE)

    # ---------- 底部红色判读线 ----------
    s.arrow(400, 546, 400, 574, RED, 5, 13)
    s.band(120, 580, 560, 78, PHRASES[3], RED, WHITE, 32)

    s.save("05_tajima_d_bias_drivers.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())

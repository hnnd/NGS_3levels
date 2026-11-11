#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_sfs_three_statistics.py — 生成 04_sfs_three_statistics.svg
（FIG-P04-04：第 16 页 cols 一栏「SFS 三个读数分工与中性基准」）【new-svg】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-04（P16，cols，800×700）。
依据：教材 §20.4.1 L117–147——位点频谱（SFS）是全章统计量的共同底座：
π 对中间频率加权最重（权重 2p(1−p) 在 p = 0.5 处最大），θ_W 等权数分离位点
（对稀有端极敏感），二者之差标准化后是 Tajima's D；中性恒定期望 π = θ_W，
残差为 0。
图内中文严格取方案给定 30 字（4 句）；p、θ_W、D_T 与数字属符号。
结构＝顶部的零假设天平（期望相等）＋中部频谱柱状图（左端稀有位点橙色高亮、
青蓝包络线示 π 的中间加权）＋底部残差读法。
无网络；不涉及随机数（柱高为示意的 1/i 形状，图内不标具体计数）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 04_sfs_three_statistics.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["多样性权在中间", "分离位点数稀有端", "期望相等中性基准", "残差看偏离方向"]
TEXT = "".join(PHRASES)

X_AT = {"p0": 86, "p5": 740}        # p = 0 与 p = 0.5 的横坐标


def px(p):
    return X_AT["p0"] + p / 0.5 * (X_AT["p5"] - X_AT["p0"])


def main():
    s = SVG(800, 700, "Site frequency spectrum, three readouts", plan=TEXT)

    # ---------- 顶部：中性零假设天平 ----------
    s.line(400, 62, 400, 104, BLUE, 5)
    s.polygon([(400, 30), (376, 66), (424, 66)], BLUE)
    s.line(300, 66, 500, 66, BLUE, 6, cap="round")
    for x in (300, 500):
        s.line(x, 66, x, 92, BLUE, 4)
        s.path(f"M {x - 26} 92 Q {x} 120 {x + 26} 92", BLUE, 4)
    s.text(400, 160, PHRASES[2], 30, GREEN, "middle", "bold")

    # ---------- 中部：频谱柱状图 ----------
    ybase, ytop = 470, 232
    s.arrow(80, ybase, 770, ybase, BLUE, 5, 14)
    s.arrow(80, ybase, 80, ytop, BLUE, 5, 14)
    heights = [220, 150, 112, 90, 74, 62, 52, 45, 39, 35]
    for i, h in enumerate(heights, start=1):
        p = 0.05 * i
        x = px(p)
        rare = i <= 3
        s.rect(x - 22, ybase - h, 44, h, ORANGE if rare else BLUE_TINT,
               ORANGE if rare else BLUE, 3, rx=5)

    # π 的中间频率加权包络（青蓝）：权重 2p(1−p)，峰值在 p = 0.5
    pts = []
    for k in range(0, 51):
        p = k / 100.0
        y = ybase - 210 * (2 * p * (1 - p)) / 0.5
        pts.append((round(px(p), 1), round(y, 1)))
    s.polyline(pts, CYAN, 6)

    # 横轴刻度（p）
    for p in (0.1, 0.2, 0.3, 0.4, 0.5):
        x = px(p)
        s.line(x, ybase, x, ybase + 10, BLUE, 3)
        s.text(x, ybase + 44, f"{p:.1f}", 30, GRAY, "middle")
    s.text(786, ybase + 44, "p", 30, BLUE, "middle", "bold")

    # ---------- 两处读数标注 ----------
    s.text(66, 220, PHRASES[1], 30, ORANGE, "start", "bold")
    s.text(770, 214, PHRASES[0], 30, CYAN_DEEP, "end", "bold")

    # ---------- 底部：残差 ----------
    s.arrow(400, 522, 400, 568, BLUE, 5, 15)
    s.text(432, 550, "D_T", 30, BLUE, "start", "bold")
    s.band(120, 586, 560, 78, PHRASES[3], BLUE, WHITE, 32)

    s.save("04_sfs_three_statistics.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())

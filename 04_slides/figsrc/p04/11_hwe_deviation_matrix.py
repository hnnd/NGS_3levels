#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_hwe_deviation_matrix.py — 生成 11_hwe_deviation_matrix.svg
（FIG-P04-11：第 25 页 cols 一栏「HWE 偏离机制与拓扑判别矩阵」）【new-svg】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-11（P25，cols，800×700）。
依据：教材 §20.4.3 的判别表——偏离方向只有两种（杂合子过量、杂合子缺失），
成因分技术（旁系同源/重复坍缩：孤立散点、集中重复区与低 MAPQ）与生物学
（自交近交：平坦均一；Wahlund：全基因组缺失、分群后消失；平衡选择：局部过量）
两族，判别靠全基因组拓扑与协变量，不靠单个位点的 p 值。
图内中文严格取方案给定 30 字（4 句）；符号与数字属符号。
结构＝两维判别矩阵：横轴偏离方向（左 + 过量／右 − 缺失），纵轴基因组拓扑
（上 散点／下 平坦与分层），四格分别用点阵、平线、局部点簇、层带表示。
左下格（局部过量、平衡选择）只用图形表示——方案的 30 字里没有它的判读句。
红只标「技术坍缩孤立散点」一处，绿标「分层分群后即消失」。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 11_hwe_deviation_matrix.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["技术坍缩孤立散点", "自交近交平坦均一", "分层分群后即消失", "看方向与拓扑"]
TEXT = "".join(PHRASES)

X0, X1 = 92, 760
Y0, Y1 = 96, 536
XM, YM = (X0 + X1) / 2, (Y0 + Y1) / 2


def scattered(s, cx, cy, color, n=14, r=7):
    """技术坍缩：孤独的散点簇（不成带、不铺满）。"""
    offs = [(-92, -46), (-58, 6), (-20, -34), (12, 24), (46, -12), (84, 30),
            (-74, 40), (26, -52), (62, 52), (-30, 48), (96, -44), (-100, 4),
            (2, 62), (110, 8)]
    for dx, dy in offs[:n]:
        s.circle(cx + dx, cy + dy, r, color)


def flat(s, cx, cy, color):
    """自交/近交：全基因组平坦均一的高线。"""
    s.line(cx - 110, cy + 22, cx + 110, cy + 22, color, 5)
    for dx in (-80, -30, 20, 70):
        s.circle(cx + dx, cy + 22, 8, color)


def layered(s, cx, cy, color):
    """Wahlund：分层带来的整段缺失（三条并走的带）。"""
    for i, dy in enumerate((-28, 0, 28)):
        s.line(cx - 112, cy + dy, cx + 112, cy + dy, color, 5)
        s.circle(cx - 60 + i * 24, cy + dy, 8, WHITE, color, 3)


def local(s, cx, cy, color):
    """平衡选择：局部、局限在少数功能位点的过量。"""
    s.line(cx - 112, cy + 26, cx + 112, cy + 26, color, 4, dash="12 9")
    for dx in (-40, -16, 8, 32):
        s.circle(cx + dx, cy + 26, 9, color)
    s.circle(cx + 60, cy + 26, 9, WHITE, color, 3)


def main():
    s = SVG(800, 700, "HWE deviation direction times topology", plan=TEXT)

    # ---------- 矩阵框与两轴 ----------
    s.rect(X0, Y0, X1 - X0, Y1 - Y0, WHITE, BLUE, 4, rx=8)
    s.line(XM, Y0, XM, Y1, PANEL, 3)
    s.line(X0, YM, X1, YM, PANEL, 3)
    s.text(X0 - 20, Y0 + 40, "+", 34, BLUE, "middle", "bold")
    s.text(X0 - 20, Y1 - 28, "−", 34, BLUE, "middle", "bold")

    # ---------- 四格 ----------
    # 左上：技术坍缩（杂合过量 + 孤立散点）
    scattered(s, (X0 + XM) / 2, Y0 + 104, RED)
    s.text((X0 + XM) / 2, Y0 + 196, PHRASES[0], 30, RED, "middle", "bold")

    # 右上：自交/近交（杂合缺失 + 平坦均一）
    flat(s, (XM + X1) / 2, Y0 + 92, BLUE)
    s.text((XM + X1) / 2, Y0 + 196, PHRASES[1], 30, BLUE, "middle", "bold")

    # 左下：平衡选择（局部过量，仅图形 + 杂合过量的符号）
    local(s, (X0 + XM) / 2 - 24, YM + 84, ORANGE)
    s.text(232, 378, "Aa", 32, ORANGE, "middle", "bold")
    s.text(292, 378, "↑", 32, ORANGE, "middle", "bold")

    # 右下：Wahlund（缺失 + 分层，分群后消失）
    layered(s, (XM + X1) / 2, YM + 76, GREEN)
    s.text((XM + X1) / 2, YM + 168, PHRASES[2], 30, GREEN, "middle", "bold")

    s.band(120, 578, 560, 78, PHRASES[3], BLUE, WHITE, 32)

    s.save("11_hwe_deviation_matrix.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())

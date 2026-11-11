#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""03_phenotype_transform_tree.py — 生成 03_phenotype_transform_tree.svg
（FIG-P05-03：P16「表型：成败在第一条命令之前」，cols 左栏）【new-svg】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-03（800×700，中文共 27 字）。
依据：教材 §21.4.2——先看表型分布形态再决定变换：轻度偏态用对数／Box-Cox，
保留厘米、克这类物理单位；极端偏态或零膨胀用秩次逆正态（RINT），QQ 图会变
漂亮，但极端个体的离群信息被抹平、β 变成无量纲的秩分，不能再解释成物理效应。
图内中文严格取方案给定三句（7 + 8 + 12 = 27 字）；柱形与曲线为示意分布形态，
不含实测数值。
配色：绿色＝对数／Box-Cox 分支，橙色＝RINT 分支；红色只标「抹平离群、失去
物理单位」这一处代价。
无网络；不涉及随机数（柱高为写死的示意形态）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 03_phenotype_transform_tree.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["轻度偏态用对数",        # 7
           "极端分布用逆正态",      # 8
           "抹平极端离群失去物理单位"]  # 12
TEXT = "".join(PHRASES)

# 右偏分布示意柱高（无单位、非实测）：长尾向右，最后两根标为极端离群
BARS = [30, 70, 110, 140, 132, 112, 88, 66, 48, 34, 24, 17, 12, 8]


def main():
    s = SVG(800, 700, "Phenotype distribution decides the transform",
            plan=TEXT)

    # ---------- 上部：原始表型分布（右偏，尾部有几根极端个体）----------
    x0, x1, ybase, ytop = 70.0, 730.0, 210.0, 46.0
    s.line(x0, ybase, x1 + 10, ybase, INK, 5)
    s.line(x0, ybase, x0, ytop - 8, INK, 5)
    n = len(BARS)
    slot = (x1 - x0) / n
    bw = slot * 0.68
    for i, h in enumerate(BARS):
        bx = x0 + i * slot + (slot - bw) / 2
        col = ORANGE if i >= 11 else BLUE
        tint = ORANGE_TINT if i >= 11 else BLUE_TINT
        s.rect(bx, ybase - h, bw, h, tint, col, 3, rx=4)

    # ---------- 二叉分流 ----------
    mid = (x0 + x1) / 2
    s.line(mid, ybase, mid, 244, CYAN_DEEP, 5)
    s.line(190, 244, 610, 244, CYAN_DEEP, 5)
    s.arrow(190, 244, 190, 292, CYAN_DEEP, 5)
    s.arrow(610, 244, 610, 292, CYAN_DEEP, 5)

    # ---------- 分支 1（左，绿）：对数／Box-Cox ----------
    s.rect(30, 296, 320, 160, GREEN_TINT, GREEN, 5, rx=16)
    s.curve([(60, 348), (92, 326), (124, 314), (156, 308), (200, 304)],
            GREEN, 5)
    s.text(190, 412, PHRASES[0], 32, GREEN, "middle", "bold")

    # ---------- 分支 2（右，橙）：秩次逆正态 RINT ----------
    s.rect(450, 296, 320, 160, ORANGE_TINT, ORANGE, 5, rx=16)
    s.polyline([(480, 348), (506, 348), (506, 334), (532, 334), (532, 320),
                (558, 320), (558, 308), (584, 308)], ORANGE, 5)
    s.text(610, 412, PHRASES[1], 32, ORANGE, "middle", "bold")

    # ---------- 底部：RINT 的代价（唯一红色警示）----------
    s.rect(30, 496, 740, 128, RED_TINT, RED, 5, rx=16)
    s.stamp(96, 560, 88, 88, "!", RED, RED, 34)
    s.text(400, 574, PHRASES[2], 32, RED, "middle", "bold")

    s.save("03_phenotype_transform_tree.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())

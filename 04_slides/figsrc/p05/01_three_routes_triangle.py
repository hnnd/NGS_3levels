#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_three_routes_triangle.py — 生成 01_three_routes_triangle.svg
（FIG-P05-01：P10「三条路线是三角，不是替代关系」，cols 左栏）【new-svg】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-01（800×700，中文共 29 字）。
依据：教材 §21.4.1——双亲分离群体连锁定位（高功效、Mb 级精度、受限于重组）、
极端表型混池分组分析（低成本、周期短、只测主效）、自然群体全基因组关联
（kb 级精度、要大样本、须防分层）；现代做法是把三者串起来：自然群体初筛锁定
区间 → 分离群体或编辑确证。
图内中文严格取方案给定三句（12 + 7 + 10 = 29 字），英文只有路线名缩写
（BCS / BSA / GWAS），不写出处标签（COURSE_SYNC §7 第 10 条）。
配色：深蓝＝双亲连锁、橙＝混池分组、绿＝自然群体关联；红色只标三角内部
那个共同陷阱一处（结构分层与多重检验惩罚）。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 01_three_routes_triangle.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["双亲连锁功效高精度兆碱基",   # 12
           "混池极端测主效",             # 7
           "自然群体达几十千碱基"]        # 10
TEXT = "".join(PHRASES)
A1, A2 = "双亲连锁功效高", "精度兆碱基"          # 合起来＝PHRASES[0]
B1 = PHRASES[1]
C1, C2 = "自然群体达", "几十千碱基"              # 合起来＝PHRASES[2]


def main():
    s = SVG(800, 700, "Three routes as a triangle", plan=TEXT)

    # ---------- 三角骨架（青蓝细线，画在卡片之下）----------
    va, vb, vc = (200.0, 232.0), (600.0, 232.0), (400.0, 470.0)
    s.polygon([va, vb, vc], "none", CYAN, 5, dash="16 10")

    # 串联回路：自然群体先筛 → 分离群体／编辑确证（青蓝虚线箭头，沿左侧上返）
    s.path("M 200 600 C 96 570 70 380 86 252", CYAN_DEEP, 5, dash="14 9")
    s.polygon([(86, 252), (106, 274), (68, 278)], CYAN_DEEP)

    # ---------- 顶点 1（左上）：双亲连锁定位 ----------
    s.rect(40, 62, 320, 170, BLUE_TINT, BLUE, 5, rx=16)
    s.text(200, 128, A1, 32, BLUE, "middle", "bold")
    s.text(200, 176, A2, 32, BLUE, "middle", "bold")
    s.text(200, 216, "BCS", 30, GRAY, "middle")

    # ---------- 顶点 2（右上）：混池极端分组 ----------
    s.rect(440, 62, 320, 170, ORANGE_TINT, ORANGE, 5, rx=16)
    s.text(600, 140, B1, 32, ORANGE, "middle", "bold")
    s.text(600, 216, "BSA", 30, GRAY, "middle")

    # ---------- 顶点 3（下中）：自然群体关联 ----------
    s.rect(200, 470, 400, 170, GREEN_TINT, GREEN, 5, rx=16)
    s.text(400, 532, C1, 32, GREEN, "middle", "bold")
    s.text(400, 580, C2, 32, GREEN, "middle", "bold")
    s.text(400, 622, "GWAS", 30, GRAY, "middle")

    # ---------- 三角内部：三条路线共同的陷阱（唯一红色警示）----------
    s.polygon([(400, 330), (430, 392), (370, 392)], RED_TINT, RED, 4)
    s.text(400, 382, "!", 34, RED, "middle", "bold")

    s.save("01_three_routes_triangle.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    assert A1 + A2 == PHRASES[0] and C1 + C2 == PHRASES[2]
    raise SystemExit(main())

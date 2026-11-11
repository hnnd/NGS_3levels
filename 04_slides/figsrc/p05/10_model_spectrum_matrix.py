#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_model_spectrum_matrix.py — 生成 10_model_spectrum_matrix.svg
（FIG-P05-10：P25「模型谱系：按「吸收什么」来记」，cols 左栏）【new-svg】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-10（800×700，中文共 28 字）。
依据：教材 §21.4.3——模型谱系按两个维度演化：横轴是宏观分层吸收（Q 矩阵／
主成分），纵轴是微观亲缘吸收（K 亲缘矩阵）。OLS 两个维度都不吸收（系统性
假阳性）；GLM+Q 只吸收宏观；MLM（Q+K）两个都吸收；EMMAX 把方差组分固定以
提速；FarmCPU／BLINK 用固定效应迭代求多位点，改善多基因性状的功效。
图内中文严格取方案给定两句（13 + 15 = 28 字）；坐标轴与模型名用 Q／K 与
英文缩写，不占汉字预算。配色：深蓝＝坐标轴，绿＝MLM，紫＝多位点迭代模型；
红色只标 OLS 这个「两个维度都不吸收」的起点一处。
无网络；不涉及随机数（纯结构示意，无计算结果）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 10_model_spectrum_matrix.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["宏观靠主成分微观靠亲缘矩阵",          # 13
           "固定效应迭代求解多基因性状功效"]       # 15
TEXT = "".join(PHRASES)

# (名称, x, y, 颜色, 标签相对点的 y 偏移)
NODES = [("OLS", 180, 556, RED, -26),
         ("GLM+Q", 470, 556, CYAN_DEEP, -26),   # 标签特殊：画在点的右侧
         ("EMMAX", 380, 340, BLUE, -26),
         ("MLM (Q+K)", 470, 236, GREEN, -28),
         ("FarmCPU/BLINK", 616, 150, PURPLE, -30)]


def main():
    s = SVG(800, 700, "Model spectrum on two absorption axes", plan=TEXT)

    # ---------- 标题句 ----------
    s.text(400, 58, PHRASES[0], 32, BLUE, "middle", "bold")

    # ---------- 二维坐标 ----------
    ox, oy = 130.0, 600.0
    s.axis(ox, oy, 744, oy, BLUE, 5)
    s.axis(ox, oy, ox, 104, BLUE, 5)
    s.text(736, 590, "Q", 34, BLUE, "start", "bold")
    s.text(104, 116, "K", 34, BLUE, "end", "bold")

    # ---------- 模型节点 ----------
    for name, x, y, col, dy in NODES:
        if col == RED:
            s.cross(x, y, 17, RED)
        else:
            s.circle(x, y, 15, WHITE, col, 5)
            s.circle(x, y, 7, col)
        if name == "GLM+Q":
            s.text(x + 24, y + 10, name, 30, col, "start", "bold")
        else:
            s.text(x, y + dy, name, 30, col, "middle", "bold")

    # MLM 的「两个维度都吸收」提示：到两轴的虚线
    s.line(130, 236, 470, 236, GREEN, 3, dash="10 8")
    s.line(470, 600, 470, 236, GREEN, 3, dash="10 8")

    # ---------- 底部纪律句 ----------
    s.text(400, 664, PHRASES[1], 32, PURPLE, "middle", "bold")

    s.save("10_model_spectrum_matrix.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())

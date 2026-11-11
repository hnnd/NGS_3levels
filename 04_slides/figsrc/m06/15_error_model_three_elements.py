#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_error_model_three_elements.py — FIG-M06-15 单 run 错误模型三要素

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-15（P28，cols 一栏
800×700，new-svg）。
教材依据：§18.4.4（err_F.pdf 的三要素：观测黑点随 Q 上升下行、拟合黑线紧贴观测、
红色理论期望线单调递减；三者对照才能看出模型学得对不对）。
图内汉字 = 方案原句逐字，共 19 字（黑点随质量下降 / 黑线贴合实测 / 红线理论期望）；
其余标注为 err_F.pdf、Q 刻度与图例色键。
无网络、无随机数（观测点由解析式确定性生成）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 15_error_model_three_elements.py
"""
import sys
import math

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403
from svghelp import BLUE, GRAY, INK, RED, SVG, WHITE

QS = [10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40]
PX0, PX1, PYT, PYB = 112, 744, 158, 468
LOG_HI, LOG_LO = -0.7, -4.9           # y 轴：错误率 10⁻¹ 量级 → 10⁻⁵ 量级


def Y(logp):
    return PYB - (logp - LOG_LO) / (LOG_HI - LOG_LO) * (PYB - PYT)


def X(q):
    return PX0 + (q - 10) / 30 * (PX1 - PX0)


def main():
    s = SVG(800, 700)

    s.text(60, 108, "err_F.pdf", 32, INK, "start", "bold")

    # 坐标框
    s.line(PX0, PYB, PX1, PYB, BLUE, 4)
    s.line(PX0, PYB, PX0, PYT, BLUE, 4)
    for q in (10, 20, 30, 40):
        s.line(X(q), PYB, X(q), PYB + 9, BLUE, 3)
        s.text(X(q), PYB + 38, str(q), 30, GRAY, "middle")
    s.text(PX1, PYB - 18, "Q", 30, GRAY, "end", "bold")

    # 红线：理论期望（全图唯一警示）
    s.polyline([(X(q), Y(-q / 10)) for q in QS], RED, 6, dash="12 8")

    # 黑点：观测（确定性解析式，略高于理论）
    dots = []
    for i, q in enumerate(QS):
        lp = -q / 10 + 0.10 + 0.05 * math.sin(i * 0.9)
        dots.append((X(q), Y(lp)))
        s.circle(X(q), Y(lp), 8, INK)

    # 黑线：拟合（穿过观测点）
    s.polyline(dots, INK, 5)

    # 图例：三行，左侧色键 + 右侧原句
    KEY_X, TXT_X = 136, 200
    for i, (lab, kind) in enumerate([("黑点随质量下降", "dot"),
                                     ("黑线贴合实测", "line"),
                                     ("红线理论期望", "red")]):
        y = 552 + i * 56
        if kind == "dot":
            s.line(KEY_X, y, KEY_X + 46, y, INK, 4)
            s.circle(KEY_X + 23, y, 7, INK)
        elif kind == "line":
            s.line(KEY_X, y, KEY_X + 46, y, INK, 6)
        else:
            s.line(KEY_X, y, KEY_X + 46, y, RED, 6, dash="12 8")
        s.text(TXT_X, y + 10, lab, 30, INK, "start", "bold")

    s.save("15_error_model_three_elements.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

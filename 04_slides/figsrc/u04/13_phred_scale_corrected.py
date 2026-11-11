#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_phred_scale_corrected.py — 生成 13_phred_scale_corrected.svg
（FIG-U04-16：Q 标尺重构，重绘 F06-05 合规版【标尺/判据】）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-16（P34，cols 一栏，viewBox 800×700）。
垂直标尺自下而上：Q10（红，错百分之十）、Q20（橙，错百分之一）、
Q30（绿，错千分之一）、Q40（深蓝）；底部红字「两档不必然上升」。
数据来源：Q = -10·log10(P)（教材 §6.4.4 L132–136）。
依据：教材 §6.4.4 L134；彻底替换 hold_redraw 的 F06-05（D055）。
图内汉字 27，红色 2 处。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 13_phred_scale_corrected.py
"""
from svghelp import *


def main():
    s = SVG(800, 700)
    XR, WT = 250, 100            # 标尺左缘、宽
    QLO, QHI = 5, 40
    YTOP, YBOT = 120, 560

    def yq(q):
        return YBOT - (q - QLO) * (YBOT - YTOP) / (QHI - QLO)

    # 四段色带
    bands = [(QLO, 10, RED), (10, 20, ORANGE), (20, 30, GREEN), (30, QHI, BLUE)]
    for q1, q2, color in bands:
        s.rect(XR, yq(q2), WT, yq(q1) - yq(q2), color)
    s.rect(XR - 6, yq(QHI), WT + 12, 8, INK, rx=4)

    # Q 刻度（左，拉丁）+ 错误率直觉（右）
    marks = [(10, "Q10", RED, "十：错百分之十"),
             (20, "Q20", ORANGE_DEEP, "二十：错百分之一"),
             (30, "Q30", GREEN_DEEP, "三十：错千分之一"),
             (40, "Q40", BLUE, None)]
    for q, qlab, ctext, hanzi in marks:
        s.line(XR - 4, yq(q), XR + WT + 4, yq(q), WHITE, sw=4)
        s.text(XR - 18, yq(q) + 11, qlab, 30, GRAY, "end", "bold")
        if hanzi:
            s.text(XR + WT + 22, yq(q) + 11, hanzi, 30, ctext, "start",
                   "bold")

    # 底部红字（第二处红色）
    s.text(400, 645, "两档不必然上升", 32, RED, "middle", "bold")

    s.save("13_phred_scale_corrected.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

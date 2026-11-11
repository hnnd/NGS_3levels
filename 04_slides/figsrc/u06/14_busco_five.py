#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_busco_five.py — 生成 14_busco_five.svg（FIG-U06-14：BUSCO 五个数一起读）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-14（P36，cols 一栏，800×700）。
数据：结构等式 C=S+D、C+F+M=100%（教材 §8.4.8 L282）；设例数字（123/65/58/0/1）
留在 deck P37 文字演算，图内不放（避免抢课堂演算）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 14_busco_five.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    X0, X1, Y0, Y1 = 60, 740, 230, 320
    # 比例：S 50% / D 25% / F 10% / M 15%（示意占比，非设例数值）
    b_s, b_d, b_f = X0, X0 + 340, X0 + 510   # 400, 570
    b_m = X0 + 578                            # 638
    s.rect(b_s, Y0, 340, 90, CYAN)
    s.rect(b_d, Y0, 170, 90, PURPLE)
    s.rect(b_f, Y0, 68, 90, ORANGE)
    s.rect(b_m, Y0, 102, 90, PANEL)
    s.text(b_s + 24, Y0 + 58, "S 单拷贝", 30, WHITE, "start", "bold")
    s.text(b_d + 24, Y0 + 58, "D 多拷贝", 30, WHITE, "start", "bold")
    s.text(b_m + 51, Y0 + 58, "M 缺失", 30, GRAY, "middle", "bold")

    # F 段太窄：标签放条下，带引线
    cx_f = b_f + 34
    s.line(cx_f, Y1, cx_f, Y1 + 28, GRAY, 3)
    s.text(cx_f, Y1 + 60, "F 碎片", 30, INK, "middle", "bold")

    # C 外层绿色括注（S+D 整体 = 完整）
    s.line(b_s, 196, b_s + 510, 196, GREEN, 5)
    s.line(b_s, 196, b_s, 216, GREEN, 5)
    s.line(b_s + 510, 196, b_s + 510, 216, GREEN, 5)
    s.text(b_s + 255, 180, "C 完整", 32, GREEN, "middle", "bold")

    # 两个等式徽章
    s.rect(50, 410, 200, 70, WHITE, PANEL, 3, rx=12)
    s.text(150, 456, "C = S + D", 32, BLUE, "middle", "bold")
    s.rect(280, 410, 270, 70, WHITE, PANEL, 3, rx=12)
    s.text(415, 456, "C + F + M = 100%", 32, BLUE, "middle", "bold")

    # 红色分母框（唯一红色：易错点＝忘看分母；框加宽容纳 30 字标签）
    s.rect(580, 410, 180, 70, WHITE, RED, 5, rx=12)
    s.text(670, 456, "n = 分母", 30, RED, "middle", "bold")

    s.save("14_busco_five.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

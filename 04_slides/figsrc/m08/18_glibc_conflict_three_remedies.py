#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_glibc_conflict_three_remedies.py — FIG-M08-18 宿主 glibc 过旧与三阶梯处置（P37，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-18（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.4（集群 CentOS 7 宿主 glibc 2.18，新构建要求 `__glibc >=2.28` 报
UnsatisfiableError；处置代价从低到高三条，三条都不必改代码）。
图内汉字 = 方案原句逐字，共 29 字（宿主系统库过旧 / 一找旧构建 / 二用单规则容器 /
三换新节点 / 严禁改代码）；报错与版本号用 ASCII。红色只作两处语义组：
顶部报错边框、底部「严禁改代码」卡（阶梯三级用绿/橙/紫区分代价）。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 18_glibc_conflict_three_remedies.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

STEPS = [("一找旧构建", GREEN, GREEN_TINT, 250),
         ("二用单规则容器", ORANGE, ORANGE_TINT, 356),
         ("三换新节点", PURPLE, PURPLE_TINT, 462)]


def main():
    s = SVG()

    # 顶部报错卡（红 1/2 语义组：边框 + 标题）
    s.rect(46, 28, 708, 118, WHITE, RED, 4, rx=14)
    s.text(400, 72, "宿主系统库过旧", 32, RED, "middle", "bold")
    s.text(230, 122, "glibc 2.18", 30, GRAY, "middle")
    s.text(570, 122, "__glibc >=2.28", 30, GRAY, "middle")
    s.line(330, 108, 470, 108, GRAY, 3, dash="8 6")

    # 三级处置阶梯（代价由低到高）
    for han, ink, tint, y in STEPS:
        s.rect(110, y, 580, 76, tint, ink, 4, rx=12)
        s.text(374, y + 47, han, 32, ink, "middle", "bold")
        s.text(668, y + 47, "ok", 30, GREEN, "end")

    for y in (326, 432, 538):
        s.arrow(390, y, 390, y + 18, CYAN, 4, 10)

    # 底部警示（红 2/2）：问题不在代码里
    s.rect(146, 574, 508, 92, RED_TINT, RED, 5, rx=14)
    s.text(400, 628, "严禁改代码", 36, RED, "middle", "bold")

    return s.save("18_glibc_conflict_three_remedies.svg")


if __name__ == "__main__":
    raise SystemExit(main())

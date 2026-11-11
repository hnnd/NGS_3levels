#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_duplication_100k_cap.py — 生成 06_duplication_100k_cap.svg
（FIG-U04-06：重复与过表达 100,000 登记上限机制【算法】）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-06（P19，cols 一栏，viewBox 800×700）。
数据流：读段输入（深蓝）→ 前 50 bp 截断过滤器（青蓝）→ 容量 100,000 的哈希登记槽（橙）；
满额冻结红闸「满额后只数不增」；绿色计算框「分母为全文件读段」。
机制来源：FastQC v0.12.1 OverRepresentedSeqs（demos/ch06_amplicon_redlight.py 复刻）。
依据：教材 §6.4.2 L80–84；纠正讲义「只用文件前 10 万条 read」口径（W13）。
图内汉字 26，红色 1 处。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 06_duplication_100k_cap.py
"""
from svghelp import *


def main():
    s = SVG(800, 700)

    # 读段输入（三条示意读段）
    for i, y in enumerate((232, 282, 332)):
        s.rect(40, y, 130, 34, BLUE, rx=8)
        for k in range(4):
            s.rect(48 + k * 30, y + 7, 24, 20,
                   [GREEN, CYAN, ORANGE, PURPLE][(i + k) % 4], rx=4)
    s.text(105, 206, "reads", 30, GRAY, "middle")

    # 截断过滤器（青蓝闸门）
    s.arrow(176, 300, 252, 300, BLUE, sw=7)
    s.rect(252, 216, 130, 168, CYAN, rx=14)
    for yy in (250, 292, 334):
        s.polygon([(282, yy), (306, yy + 14), (282, yy + 28)], WHITE)
    s.text(317, 424, "截取前 50 位", 30, CYAN_DEEP, "middle", "bold")

    # 哈希登记槽（橙）：上点阵 + 下标签
    s.arrow(388, 300, 462, 300, CYAN, sw=7)
    s.rect(462, 200, 200, 200, ORANGE, rx=16)
    s.rect(478, 216, 168, 168, WHITE, rx=10)
    for r in range(3):
        for c in range(4):
            s.circle(499 + c * 42, 232 + r * 36, 10,
                     [BLUE, CYAN, GREEN, PURPLE][(r + c) % 4])
    s.text(562, 340, "登记上限", 30, INK, "middle", "bold")
    s.text(562, 376, "十万个", 30, INK, "middle", "bold")

    # 满额冻结红闸（唯一红色处）
    s.rect(664, 188, 24, 224, RED, rx=8)
    s.text(600, 446, "满额后只数不增", 30, RED, "middle", "bold")

    # 分母计算（绿）：箭头从槽左下角下行
    s.arrow(470, 404, 470, 484, ORANGE_DEEP, sw=7)
    s.rect(392, 492, 340, 84, GREEN, rx=16)
    s.text(562, 546, "分母为全文件读段", 30, WHITE, "middle", "bold")

    s.save("06_duplication_100k_cap.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

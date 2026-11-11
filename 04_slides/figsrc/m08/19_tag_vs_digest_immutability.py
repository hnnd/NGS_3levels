#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_tag_vs_digest_immutability.py — FIG-M08-19 标签（可变指针）vs 摘要（不可变指纹）（P38，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-19（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.4（标签是可变指针，维护者可把同一标签重新指向新构建；
摘要是内容寻址哈希，内容一变摘要就变；长期存档要记摘要）。
图内汉字 = 方案原句逐字，共 28 字（标签是可变指针会漂移 / 摘要是内容密码学指纹 /
永久锁定不可篡改）；镜像名、哈希与重推示意用 ASCII。红只 1 处（指针漂移）。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 19_tag_vs_digest_immutability.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402


def main():
    s = SVG()

    # 左：浮动标签（橙）——同一 tag 可被重新指向
    s.rect(40, 72, 330, 340, WHITE, ORANGE, 4, rx=16)
    s.text(205, 132, "fastp:0.23.4", 30, ORANGE_DEEP, "middle", "bold")
    s.text(205, 210, "push build A", 30, GRAY, "middle")
    s.arrow(205, 228, 205, 280, ORANGE, 4, 14)
    s.text(205, 324, "push build B", 30, GRAY, "middle")
    s.text(205, 392, "标签是可变指针会漂移", 30, RED, "middle", "bold")

    # 右：内容摘要（绿）——内容变则哈希必变
    s.rect(430, 72, 330, 340, WHITE, GREEN, 4, rx=16)
    s.text(595, 132, "fastp@sha256", 30, GREEN, "middle", "bold")
    s.text(595, 210, "3f2a...c19b", 30, GRAY, "middle")
    s.arrow(595, 228, 595, 280, GREEN, 4, 14)
    s.text(595, 324, "sha256:9c7d...", 30, GRAY, "middle")
    s.text(595, 392, "永久锁定不可篡改", 30, GREEN, "middle", "bold")

    # 中部语义注记（贯通两栏）
    s.rect(120, 448, 560, 152, CYAN_TINT, CYAN, 4, rx=14)
    s.text(400, 504, "摘要是内容密码学指纹", 30, BLUE, "middle", "bold")
    s.text(400, 562, "digest = archive lock", 30, GRAY, "middle")

    return s.save("19_tag_vs_digest_immutability.svg")


if __name__ == "__main__":
    raise SystemExit(main())

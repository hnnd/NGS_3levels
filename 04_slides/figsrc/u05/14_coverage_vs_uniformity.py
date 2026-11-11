#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_coverage_vs_uniformity.py — 生成 14_coverage_vs_uniformity.svg（FIG-U05-14：覆盖度≠均匀性）

方案：reviews/course/U05_FIGP_001.md §4 FIG-U05-14（P47，cols 一栏，viewBox 800×700）。
20,000 bp 条带：19,924 bp 绿覆盖 + 76 bp 红缺口（示意放大，非等比）；
大字 99.62%（=19924÷20000）；缺口两问「深度多少？不知道」「缺口在哪？不知道」；
底部灰行＝均匀性要看深度分位数。数字＝教材 §7.4.6 L256 设例（正文算术，手算可复核）；
对应教材「常见误用」第三条。
注：方案底部一行原文 18 字，加两问 14 字共 32 字超 ≤30 上限，灰行压缩为
「深度中位数与分位数才说均匀性」（14 字，总 28 字），语义与 L256 一致。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 14_coverage_vs_uniformity.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    # 数据自检（教材 §7.4.6 L256 正文算术）
    assert 19924 + 76 == 20000
    assert abs(19924 / 20000 * 100 - 99.62) < 0.005
    print("check: 19924+76=20000；19924/20000=99.62%")

    s = SVG(800, 700)

    # 缺口两问的引线 + 标签（放在条带上方右侧）
    s.line(648, 296, 648, 176, GRAY, 4)
    s.line(672, 296, 672, 224, GRAY, 4)
    s.text(660, 160, "深度多少？不知道", 30, INK, "middle", "bold")
    s.text(660, 208, "缺口在哪？不知道", 30, INK, "middle", "bold")

    # 大字 99.62%
    s.text(320, 232, "99.62%", 72, BLUE, "middle", "bold")
    s.text(320, 272, "= 19924 / 20000", 30, GRAY, "middle", "bold")

    # 条带：绿 19,924 bp + 红缺口 76 bp（缺口示意放大）
    s.rect(60, 300, 580, 56, GREEN, rx=8)
    s.rect(640, 300, 100, 56, RED, rx=8)
    s.rect(60, 300, 680, 56, "none", BLUE, 4, rx=8)
    s.text(350, 338, "19,924 bp", 30, WHITE, "middle", "bold")
    s.text(690, 338, "76 bp", 30, WHITE, "middle", "bold")
    s.text(60, 392, "0", 30, GRAY, "start", "bold")
    s.text(740, 392, "20,000 bp", 30, GRAY, "end", "bold")

    # 底部灰行（唯一信息行，灰）
    s.text(400, 620, "深度中位数与分位数才说均匀性", 30, GRAY, "middle",
           "bold")

    s.save("14_coverage_vs_uniformity.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

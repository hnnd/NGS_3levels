#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_halfpeak_checks.py — 生成 18_halfpeak_checks.svg（FIG-U06-18：半深度峰四检查）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-18（P57，cols 一栏，800×700）。
数据：无量字数字；四条检查措辞照教材 §8.4.3 L157（换 k / 回贴分档 / 总长对账 /
纯化重测；两条同向才算证据，L155 峰是证据不是诊断）。mini 频谱为概念示意。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 18_halfpeak_checks.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 左：mini 频谱（主峰深蓝；½× 处红色小峰＝关键异常）
    s.line(70, 120, 70, 480, INK, 3)
    s.line(70, 480, 380, 480, INK, 3)
    pts = [(75, 140), (95, 300), (115, 385), (140, 430), (165, 452),
           (200, 458), (235, 445), (270, 200), (300, 320), (330, 395),
           (360, 435), (378, 452)]
    s.curve(pts, BLUE, 6)
    half = [(150, 452), (172, 322), (198, 452)]
    s.curve(half, RED, 6)
    s.text(172, 296, "半深度峰", 30, RED, "middle", "bold")
    s.line(174, 306, 172, 322, RED, 3)

    # 右：四条检查分支
    checks = ["① 换 k", "② 回贴分档", "③ 总长对账", "④ 纯化重测"]
    for i, c in enumerate(checks):
        y = 110 + i * 108
        s.rect(420, y, 340, 84, WHITE, PANEL, 3, rx=12)
        s.rect(420, y, 12, 84, BLUE, rx=4)
        s.text(456, y + 55, c, 32, INK, "start", "bold")

    # 底部红色结论条（红色处 2：半峰 + 结论）
    s.rect(110, 586, 580, 66, RED, rx=12)
    s.text(400, 631, "两条同向才算证据", 36, WHITE, "middle", "bold")

    s.save("18_halfpeak_checks.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

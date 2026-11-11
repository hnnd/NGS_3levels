#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""21_killed_sources.py — 生成 21_killed_sources.svg
（FIG-U01-21：Killed 的三种来源——先核对，别先加核）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-21（P64，cols 一栏，800×700）。
数据：无数字（h_vmem 按 slot 计量与换算不上图——硕士细节，deck 文字已限定）。
依据：教材 §1.5.5 L295–302（至少三种来源、各自区分证据、槽位≠内存）；
ALN §4-B2 上屏口径。
层级控制：§1.5.5 标〔硕〕，本图只画 deck 已上屏的三来源＋察觉。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 21_killed_sources.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 标题与副标题
    s.text(400, 56, "Killed 只说被终止", 38, BLUE, "middle", "bold")
    s.text(400, 104, "三种来源查三处", 32, INK, "middle", "bold")

    # 顶部灰底终端条
    s.rect(280, 132, 240, 60, "#4A4A46", rx=10)
    s.text(400, 172, "$ Killed", 30, WHITE, "middle", "bold", family=MONO)

    # 三分支卡：来源 → 证据槽（拉丁探测命令 + 放大镜图标，0 汉字）
    cards = [
        (40, "内存耗尽", BLUE, "free -h"),
        (290, "超限额", ORANGE, "qstat -j"),
        (540, "登录节点", PURPLE, "hostname"),
    ]
    for cx, name, col, probe in cards:
        s.rect(cx, 236, 220, 250, WHITE, col, 5, rx=14)
        s.text(cx + 110, 290, name, 32, col, "middle", "bold")
        s.line(cx + 30, 318, cx + 190, 318, PANEL, 3)
        s.circle(cx + 110, 372, 20, "none", GRAY, 4)
        s.line(cx + 124, 388, cx + 140, 404, GRAY, 5, cap="round")
        s.rect(cx + 26, 418, 168, 52, BLUE_TINT, col, 3, rx=8)
        s.text(cx + 110, 454, probe, 30, INK, "middle", "bold", family=MONO)

    # 分支连接线
    for tx in (150, 400, 650):
        s.line(400, 192, tx, 230, PANEL, 4)

    # 底部红色横幅
    s.rect(170, 560, 460, 70, RED_TINT, RED, 4, rx=12)
    s.text(400, 606, "先核对，别先加核", 36, RED, "middle", "bold")

    s.save("21_killed_sources.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

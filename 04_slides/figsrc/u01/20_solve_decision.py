#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_solve_decision.py — 生成 20_solve_decision.svg
（FIG-U01-20：Solving environment 三岔口）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-20（P63，cols 一栏，800×700）。
数据：无数字（pin 示例写 python= 不带版本号；「课程 16 环境」等数字不进图）。
依据：教材 §2.4.6 L239（排错顺序固定下来）、§2.5.4；讲义 ⑨9.3（ALN-U01-07/18 口径）。
取舍：不选 l0_03 02_channel_solver.svg（整页海报挤占决策文字）。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 20_solve_decision.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 顶部灰底错误横幅
    s.rect(120, 40, 560, 64, GRAY, rx=12)
    s.text(400, 82, "Solving environment…", 32, WHITE, "middle", "bold",
           family=MONO)

    # 第一岔：先读冲突输出
    s.rect(280, 140, 240, 64, WHITE, BLUE, 5, rx=12)
    s.text(400, 182, "先读冲突输出", 34, BLUE, "middle", "bold")

    # 连接岔口的细线（先画，分支标题压线可读）
    for tx in (150, 400, 650):
        s.line(400, 204, tx, 258, PANEL, 4)

    # 三岔分支标题（卡外上方，30px 防溢出）
    s.text(150, 246, "互斥→换版本或拆", 30, GREEN, "middle", "bold")
    s.text(400, 246, "只是慢→先试 pin", 30, "#C96F4A", "middle", "bold")
    s.text(650, 246, "核渠道", 30, BLUE, "middle", "bold")

    # 三岔分支卡
    # ① 有互斥 → 绿块（mini 互斥对示意：同一包两个版本，拉丁）
    s.rect(40, 262, 220, 226, GREEN_TINT, GREEN, 5, rx=14)
    s.rect(66, 300, 168, 56, WHITE, GREEN, 3, rx=8)
    s.text(150, 338, "pkgA=1.0", 30, INK, "middle", "bold", family=MONO)
    s.line(136, 372, 164, 400, RED, 5, cap="round")
    s.line(164, 372, 136, 400, RED, 5, cap="round")
    s.rect(66, 402, 168, 56, WHITE, GREEN, 3, rx=8)
    s.text(150, 440, "pkgA=2.0", 30, INK, "middle", "bold", family=MONO)

    # ② 只是慢 → 橙块（沙漏 + pin 示例）
    s.rect(290, 262, 220, 226, ORANGE_TINT, ORANGE, 5, rx=14)
    s.polygon([(400, 300), (378, 336), (422, 336)], ORANGE)
    s.polygon([(400, 408), (378, 372), (422, 372)], ORANGE)
    s.line(374, 300, 426, 300, ORANGE, 5, cap="round")
    s.line(374, 408, 426, 408, ORANGE, 5, cap="round")
    s.rect(320, 426, 160, 52, WHITE, ORANGE, 3, rx=8)
    s.text(400, 462, "python=", 30, INK, "middle", "bold", family=MONO)

    # ③ 核渠道 strict → 深蓝块（渠道顺序示意，拉丁 sans 防溢出）
    s.rect(540, 262, 220, 226, BLUE_TINT, BLUE, 5, rx=14)
    chans = ["conda-forge", "bioconda", "defaults"]
    for i, ch in enumerate(chans):
        cy = 286 + i * 54
        s.rect(562, cy, 176, 44, WHITE, BLUE, 3, rx=8)
        s.text(650, cy + 31, ch, 30, INK, "middle")
        if i < 2:
            s.line(650, cy + 46, 650, cy + 52, GRAY, 3)
    s.rect(580, 444, 140, 40, BLUE, rx=8)
    s.text(650, 472, "strict", 30, WHITE, "middle", "bold", family=MONO)

    # 底部红色横幅
    s.rect(140, 560, 520, 70, RED_TINT, RED, 4, rx=12)
    s.text(400, 606, "别把慢当冲突乱拆", 36, RED, "middle", "bold")

    s.save("20_solve_decision.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

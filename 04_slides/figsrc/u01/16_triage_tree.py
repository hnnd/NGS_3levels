#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_triage_tree.py — 生成 16_triage_tree.svg
（FIG-U01-16：结果不对时先做什么——症状→第一动作分诊四行）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-16（P51，cols 一栏，800×700）。
数据：无数字。
依据：教材 §1.5.1 L263–270、§1.5.2 L271–278、§1.4.8 L201（Eqw 不会自己恢复）、§1.5.4；
与 deck P51 表逐行对应（P52 另四行不进本图）。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 16_triage_tree.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 标题
    s.text(400, 56, "症状对号，先做一步", 40, BLUE, "middle", "bold")

    # 左列症状徽章（灰底问句）→ 右列第一动作块（深蓝），Eqw 行红描边
    rows = [
        (100, "断链？", "ls -lL 回源", False),
        (225, "伪激活？", "conda list", False),
        (350, "Eqw？", "qstat -j", True),
        (475, "秒退？", "补激活两行", False),
    ]
    bw, bh = 270, 86
    for by, sym, act, eqw in rows:
        s.rect(60, by, bw, bh, PANEL, GRAY, 4, rx=12)
        s.text(60 + bw / 2, by + 56, sym, 32, INK, "middle", "bold")
        edge = RED if eqw else BLUE
        s.rect(440, by, 300, bh, BLUE if not eqw else RED_TINT,
               edge, 5 if eqw else 4, rx=12)
        fam = MONO if all(ord(c) < 0x2000 for c in act) else None
        s.text(590, by + 56, act, 32, edge if eqw else WHITE, "middle",
               "bold", family=fam)
        s.arrow(336, by + bh / 2, 432, by + bh / 2, GRAY, 4)
    # Eqw 角标（红色第 2 处；贴 Eqw 行右上角，不压上一行）
    s.rect(530, 334, 210, 46, RED, rx=8)
    s.text(635, 366, "Eqw 不会自己好", 30, WHITE, "middle", "bold")

    s.save("16_triage_tree.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

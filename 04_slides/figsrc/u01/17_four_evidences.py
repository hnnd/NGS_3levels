#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_four_evidences.py — 生成 17_four_evidences.svg
（FIG-U01-17：四条证据，缺一条都不能算做成）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-17（P54，cols 一栏，800×700）。
数据：无数字。
依据：教材 §1.4.8 L203–211（四件互相独立的证据）、§1.4.11 L251–258（端到端验收）。
边界：与 FIG-U01-14 是两个概念（环境能不能跑 vs 这次作业做没做成）。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 17_four_evidences.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 标题
    s.text(400, 56, "四条证据缺一不可", 40, BLUE, "middle", "bold")

    # 四张证据卡 2×2（节点/时间/路径/产物 + 拉丁探测命令）
    cards = [
        (90, 110, "节点", "hostname", BLUE, BLUE_TINT),
        (450, 110, "时间", "qstat 起止行", CYAN_DEEP, "#D8EEF4"),
        (90, 380, "路径", "command -v", PURPLE, PURPLE_TINT),
        (450, 380, "产物", "wc -l", ORANGE, ORANGE_TINT),
    ]
    cw, chh = 260, 180
    for cx, cy, name, probe, col, tint in cards:
        s.rect(cx, cy, cw, chh, tint, col, 5, rx=14)
        s.text(cx + cw / 2, cy + 76, name, 40, col, "middle", "bold")
        fam = MONO if all(ord(c) < 0x2000 for c in probe) else None
        s.text(cx + cw / 2, cy + 136, probe, 30, INK, "middle", family=fam)

    # 中心红色徽章
    s.circle(400, 335, 78, RED_TINT, RED, 5)
    s.text(400, 322, "日志成功", 30, RED, "middle", "bold")
    s.text(400, 362, "≠做成", 30, RED, "middle", "bold")

    s.save("17_four_evidences.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

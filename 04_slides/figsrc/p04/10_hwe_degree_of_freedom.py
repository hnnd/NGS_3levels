#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_hwe_degree_of_freedom.py — 生成 10_hwe_degree_of_freedom.svg
（FIG-P04-10：第 23 页 cols 一栏「HWE 自由度 1 与低频卡方失效」）【new-svg】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-10（P23，cols，800×700）。
依据：教材 §20.4.3——自由度 3 − 1 − 1 = 1（三类基因型减总数约束、减数据内生的
等位频率 p）；n = 50、MAF = 0.05 时稀有纯合子期望频数 50 × 0.05² = 0.125，
远低于卡方渐近要求的 5，低频端被成批判成偏离；全基因组改用 Wigginton 等
2005 的网络精确检验（固定等位总数、枚举杂合子构型）。
数字入口：教材 §20.4.3 手算（50 × 0.05² = 0.125，可计算器复核）。
图内中文严格取方案给定 30 字（4 句）；数字、AA/Aa/aa 与 HWE 属符号。
结构＝左侧自由度分解卡（三类基因型 → 两次减项 → 1）、右上卡方失效区
（期望 0.125 < 5）、右下精确检验的枚举格点；底部一句提醒。
红只标「低频稀有卡方失效」一处。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 10_hwe_degree_of_freedom.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["自由度唯一看杂合", "低频稀有卡方失效", "网络精确枚举残差", "检验非质量分"]
TEXT = "".join(PHRASES)

N, MAF, MIN_CELL = 50, 0.05, 5


def numbers():
    expect = N * MAF ** 2
    if abs(expect - 0.125) > 1e-12:
        raise SystemExit(f"期望频数应为 0.125，实际 {expect}")
    if expect >= MIN_CELL:
        raise SystemExit("0.125 应低于卡方经验门槛 5")
    return expect


def main():
    expect = numbers()
    s = SVG(800, 700, "HWE has one degree of freedom", plan=TEXT)

    # ---------- 左：自由度分解 ----------
    s.panel(28, 60, 304, 440, BLUE_TINT, BLUE, 4)
    for i, geno in enumerate(("AA", "Aa", "aa")):
        y = 96 + i * 66
        s.rect(68, y, 224, 54, WHITE, BLUE, 3, rx=10)
        s.text(180, y + 38, geno, 32, BLUE, "middle", "bold")
    s.text(80, 328, "− 1", 34, BLUE, "start", "bold")
    s.text(80, 374, "− 1", 34, BLUE, "start", "bold")
    s.line(60, 402, 300, 402, BLUE, 3, dash="10 8")
    s.text(180, 448, "= 1", 44, BLUE, "middle", "bold")
    s.text(180, 490, PHRASES[0], 30, BLUE, "middle", "bold")

    # ---------- 右上：卡方失效 ----------
    s.panel(352, 60, 420, 196, RED_TINT, RED, 4)
    s.text(562, 122, f"{N} × {MAF}² = {expect:.3f}", 34, INK, "middle", "bold")
    s.text(562, 178, f"< {MIN_CELL}", 30, INK, "middle", "bold")
    s.text(562, 232, PHRASES[1], 30, RED, "middle", "bold")

    # ---------- 右下：精确检验枚举 ----------
    s.panel(352, 272, 420, 228, GREEN_TINT, GREEN, 4)
    for r in range(3):
        for c in range(7):
            cx, cy = 396 + c * 47, 316 + r * 34
            on = (r == 1 and c <= 4)
            s.circle(cx, cy, 9, GREEN if on else WHITE, GREEN, 3)
    s.polyline([(396, 350), (443, 350), (490, 350), (537, 350), (584, 350)],
               GREEN, 4)
    s.text(562, 470, PHRASES[2], 30, GREEN, "middle", "bold")

    # ---------- 底部 ----------
    s.band(120, 546, 560, 78, PHRASES[3], BLUE, WHITE, 32)

    s.save("10_hwe_degree_of_freedom.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())

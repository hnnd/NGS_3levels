#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_haploid_parameter_reconstruction.py — 生成 01_haploid_parameter_reconstruction.svg
（FIG-P04-01：第 10 页 cols 一栏「单倍体 vs 二倍体四参数重构」）【new-svg】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-01（P10，cols，800×700）。
依据：教材 §20.1 L18–27——单倍体没有杂合状态（基因型只有 0/1）、突变参数
θ = 4Nₑμ 换成 2Nₑμ、HWE 失去检验对象、无连锁时 r² 基线由染色体数定
（本章主线 40 条 → 1/40 = 0.025，教材 §20.4.4 手算）。
图内中文严格取方案给定 30 字（5 句）；符号与数字不计汉字。
结构＝四行双栏对照：左栏二倍体（2n）常规读数，右栏单倍体（1n）主线读数，
右栏外侧一句判读。红色只标「突变参数减半」一处。
无网络；不涉及随机数（0.025 = 1/40 为手算，可计算器复核）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 01_haploid_parameter_reconstruction.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["单倍体重构四参数", "无杂合状态", "突变参数减半", "平衡无对象", "染色体定基线"]
TEXT = "".join(PHRASES)

ROWS = [
    ("AA / Aa / aa", "0 / 1", PHRASES[1], INK),
    ("θ = 4Neμ", "θ = 2Neμ", PHRASES[2], RED),
    ("HWE", "—", PHRASES[3], INK),
    ("1/(2n−1)", "1/n = 0.025", PHRASES[4], INK),
]


def numbers():
    """基线读数 0.025 与教材 §20.4.4 的单倍体 40 条染色体手算一致。"""
    if abs(1 / 40 - 0.025) > 1e-12:
        raise SystemExit("1/40 ≠ 0.025")
    return 0.025


def main():
    numbers()
    s = SVG(800, 700, "Haploid parameter reconstruction", plan=TEXT)

    # ---------- 顶部标题带 ----------
    s.band(60, 36, 680, 78, PHRASES[0], BLUE, WHITE, 32)

    # ---------- 两栏表头 ----------
    s.text(175, 152, "2n", 32, GRAY, "middle", "bold")
    s.text(460, 152, "1n", 32, GRAY, "middle", "bold")

    # ---------- 四行双栏对照 ----------
    tops = (178, 296, 414, 532)
    for y, (left, right, phrase, pcol) in zip(tops, ROWS):
        s.rect(60, y, 230, 88, BLUE_TINT, BLUE, 4, rx=12)
        s.text(175, y + 56, left, 30, BLUE, "middle", "bold")
        s.arrow(304, y + 44, 348, y + 44, GRAY, 5, 13)
        s.rect(360, y, 200, 88, CYAN_TINT, CYAN_DEEP, 4, rx=12)
        s.text(460, y + 56, right, 30, CYAN_DEEP, "middle", "bold")
        s.text(580, y + 56, phrase, 30, pcol, "start", "bold")

    s.save("01_haploid_parameter_reconstruction.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())

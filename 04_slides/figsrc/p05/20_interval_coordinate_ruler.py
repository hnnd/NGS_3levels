#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_interval_coordinate_ruler.py — 生成 20_interval_coordinate_ruler.svg
（FIG-P05-20：P39「区间换算手算：1-based → 0-based」，cols 左栏）【new-svg】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-20（800×700，中文共 26 字）。
依据：教材 §21.4.6 的手算例——先导 SNP `ps` = 12,345,678（1-based），
半衰距离 HALF = 150,000 bp：左端 s = 12,195,678，BED 起点取 s−1 =
12,195,677；右端 12,345,678 + 150,000 = 12,495,678（半开区间的 end 直接
用 1-based 闭区间终点，不减 1），长度 300,001 bp。左端算得 ≤ 0 时按脚本
钳位到 1，BED 起点为 0。
本脚本用同一条算式重算四个数并断言（`check_interval()`），因此图上的数字与
教材手算一致。图内中文严格取方案给定两句（14 + 12 = 26 字）。
配色：青蓝＝1-based 坐标，绿＝BED 0-based 正确区间；红色只标端粒边界钳位一处。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 20_interval_coordinate_ruler.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["闭区间换半开左端减一右端不减",     # 14
           "端粒边界钳位为零防负坐标"]          # 12
TEXT = "".join(PHRASES)

LEAD, HALF = 12345678, 150000


def check_interval():
    left = LEAD - HALF
    right = LEAD + HALF
    bed_start = left - 1
    assert (left, right, bed_start) == (12195678, 12495678, 12195677)
    assert right - bed_start == 300001
    return left, right, bed_start


def main():
    left, right, bed_start = check_interval()
    s = SVG(800, 700, "1-based closed to 0-based half-open interval",
            plan=TEXT)

    def px(pos):
        return 90.0 + (pos - 12100000) / 500000.0 * 620.0

    # ---------- 上：1-based 闭区间 ----------
    s.text(px(left), 96, f"{left:,}", 30, CYAN_DEEP, "middle", "bold")
    s.text(px(right), 96, f"{right:,}", 30, CYAN_DEEP, "middle", "bold")
    s.rect(px(left), 116, px(right) - px(left), 36, CYAN_TINT, CYAN, 4, rx=6)
    s.line(px(left), 108, px(left), 160, CYAN, 4)
    s.line(px(right), 108, px(right), 160, CYAN, 4)

    # 先导 SNP
    s.line(px(LEAD), 152, px(LEAD), 186, INK, 4)
    s.text(px(LEAD), 216, f"{LEAD:,}", 30, INK, "middle", "bold")
    s.text(px(LEAD) + 6, 246, "lead SNP", 30, GRAY, "middle")

    # ---------- 换算箭头 ----------
    s.arrow(px(left), 268, px(left), 306, GREEN, 5, 13)
    s.text(px(left) - 10, 296, "−1", 32, CYAN_DEEP, "end", "bold")
    s.arrow(px(right), 268, px(right), 306, GREEN, 5, 13)
    s.text(px(right) + 10, 296, "±0", 32, GREEN, "start", "bold")

    # ---------- 下：BED 0-based 半开区间 ----------
    s.rect(px(left), 316, px(right) - px(left), 36, GREEN_TINT, GREEN, 4,
           rx=6)
    s.line(px(bed_start), 306, px(bed_start), 358, GREEN, 4)
    s.line(px(right), 306, px(right), 358, GREEN, 4)
    s.text(px(bed_start), 392, f"{bed_start:,}", 30, GREEN, "middle", "bold")
    s.text(px(right), 392, f"{right:,}", 30, GREEN, "middle", "bold")

    s.text(400, 446, f"{right - bed_start:,} bp", 32, INK, "middle", "bold")

    # ---------- 结论句 ----------
    s.text(400, 506, PHRASES[0], 32, CYAN_DEEP, "middle", "bold")

    # ---------- 端粒边界：钳位到 0（唯一红色警示）----------
    s.rect(40, 546, 720, 134, RED_TINT, RED, 5, rx=14)
    s.text(400, 606, PHRASES[1], 32, RED, "middle", "bold")
    s.text(400, 656, "max(1, s) − 1 → 0", 30, GRAY, "middle")

    s.save("20_interval_coordinate_ruler.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 26, TEXT
    raise SystemExit(main())

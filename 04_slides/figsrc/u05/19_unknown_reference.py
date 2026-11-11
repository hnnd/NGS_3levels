#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_unknown_reference.py — 生成 19_unknown_reference.svg（FIG-U05-19：区间查询空结果）

方案：reviews/course/U05_FIGP_001.md §4 FIG-U05-19（P61，cols 一栏，viewBox 800×700）。
query chr1:1-100（红框）vs @SQ 真名 1（深蓝框）逐字比对 ✗ → 终端灰警告
unknown reference ... Continue anyway → 返回 0 条、退出码 0（橙）→ 红框错误结论
「这个区间没有变异」（划线）；底部绿条＝view -H | grep '^@SQ' 逐字核对。
依据教材 §7.5.3 L377（「本机实测，非课程 pin」口径由 deck 页面 ref 承载）。
判据命令与 deck P61/P51 现有一致。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 19_unknown_reference.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 左：两张名牌对照
    s.rect(40, 60, 310, 100, WHITE, RED, 5, rx=12)
    s.text(60, 102, "query", 30, GRAY, "start", "bold")
    s.text(60, 142, "chr1:1-100", 34, RED, "start", "bold")
    s.rect(40, 210, 310, 100, WHITE, BLUE, 5, rx=12)
    s.text(60, 252, "@SQ name", 30, BLUE, "start", "bold")
    s.text(60, 292, "1", 38, INK, "start", "bold")
    s.text(185, 196, "逐字比对", 30, INK, "middle", "bold")
    s.line(264, 184, 284, 204, INK, 5)
    s.line(284, 184, 264, 204, INK, 5)
    # 左下注释（英文，避免汉字预算超支；语义＝教材 L377「名字写错」）
    s.text(195, 452, "0 rows ≠", 30, GRAY, "middle", "bold")
    s.text(195, 490, "no variants", 30, GRAY, "middle", "bold")

    s.arrow(352, 158, 386, 158, GRAY, 6, head=16)

    # 中：终端警告（深底）
    s.rect(390, 90, 390, 230, INK, rx=14)
    s.text(410, 142, "samtools view", 30, PAPER, "start", "bold")
    s.text(410, 182, "x.bam chr1:1-100", 30, PAPER, "start", "bold")
    s.line(410, 202, 760, 202, GRAY, 3)
    s.text(410, 242, "unknown reference", 30, ORANGE, "start", "bold")
    s.text(410, 282, "Continue anyway", 30, ORANGE, "start", "bold")

    s.arrow(585, 322, 585, 366, GRAY, 6, head=16)

    # 右下：结果卡（橙）＋错误结论（红框划线，2/2 红）
    s.rect(390, 370, 390, 108, ORANGE, rx=12)
    s.text(430, 414, "返回 0 条", 32, INK, "start", "bold")
    s.text(430, 456, "rc = 0", 32, INK, "start", "bold")
    s.text(380, 424, "不报错", 30, INK, "end", "bold")
    s.rect(390, 506, 390, 96, WHITE, RED, 6, rx=12)
    s.text(585, 560, "这个区间没有变异", 32, RED, "middle", "bold")
    s.line(478, 547, 692, 547, RED, 4)

    # 底部绿条：判据
    s.rect(40, 640, 740, 54, GREEN, rx=12)
    s.text(410, 676, "view -H | grep '^@SQ'  逐字核对", 30, WHITE, "middle",
           "bold")

    s.save("19_unknown_reference.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_local_vs_endtoend.py — 生成 05_local_vs_endtoend.svg（FIG-U05-05：局部 vs 端到端）

方案：reviews/course/U05_FIGP_001.md §4 FIG-U05-05（P24，cols 一栏，viewBox 800×700）。
上：bwa mem 局部，中段贴上（绿）、两端剪下（橙 S）；下：bowtie2 端到端，整条压上、
末端红描边（整条计分，贴不上的整条丢弃）。图内不写 MAPQ/比对率数字（锚点 60/42/44
在 P32 表，避免复旧口径）。依据教材 §7.4.3 L150。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 05_local_vs_endtoend.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # ---- 上面板：bwa mem（局部） ----
    s.rect(30, 30, 640, 300, PANEL, rx=16)
    s.text(60, 86, "局部：剪末端", 34, INK, "start", "bold")
    s.text(640, 86, "bwa mem", 30, GRAY, "end", "bold")

    s.text(320, 182, "150 bp", 30, GRAY, "middle", "bold")
    s.rect(80, 195, 90, 40, ORANGE, rx=6)    # 左端剪下
    s.rect(170, 195, 300, 40, GREEN, rx=6)   # 中段贴上
    s.rect(470, 195, 90, 40, ORANGE, rx=6)   # 右端剪下
    s.text(125, 222, "S", 30, INK, "middle", "bold")
    s.text(515, 222, "S", 30, INK, "middle", "bold")

    s.line(60, 275, 580, 275, BLUE, 8)
    s.text(60, 312, "ref", 30, GRAY, "start", "bold")
    s.arrow(615, 255, 615, 215, GRAY, 6, head=16)
    s.text(648, 242, "高", 30, INK, "middle", "bold")

    # ---- 下面板：bowtie2（端到端） ----
    s.rect(30, 360, 640, 300, PANEL, rx=16)
    s.text(60, 416, "端到端：整条计分", 34, INK, "start", "bold")
    s.text(640, 416, "bowtie2", 30, GRAY, "end", "bold")

    s.text(320, 508, "150 bp", 30, GRAY, "middle", "bold")
    s.rect(80, 525, 480, 40, GREEN, rx=6)        # 整条参与
    s.rect(80, 525, 56, 40, "none", RED, 5, rx=6)   # 末端计分格（红描边 1/2）
    s.rect(504, 525, 56, 40, "none", RED, 5, rx=6)  # 末端计分格（红描边 2/2）

    s.line(60, 605, 580, 605, BLUE, 8)
    s.text(60, 642, "ref", 30, GRAY, "start", "bold")
    # 贴不上 → 整条丢弃
    s.rect(150, 622, 170, 22, "none", CYAN, 4, rx=6, dash="12 8")
    s.line(180, 624, 290, 642, RED, 4)
    s.line(290, 624, 180, 642, RED, 4)
    s.text(360, 640, "丢弃", 30, INK, "start", "bold")
    s.arrow(615, 545, 615, 590, GRAY, 6, head=16)
    s.text(648, 572, "低", 30, INK, "middle", "bold")

    # ---- 右侧竖排结论 ----
    chars = ["都", "不", "更", "准，", "代", "价", "记", "处", "不", "同"]
    y = 150
    for ch in chars:
        s.text(735, y, ch, 32, INK, "middle", "bold")
        y += 44

    s.save("05_local_vs_endtoend.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

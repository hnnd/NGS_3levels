#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_silent_empty_bam.py — 生成 18_silent_empty_bam.svg（FIG-U05-18：管道成功 BAM 是空的）

方案：reviews/course/U05_FIGP_001.md §4 FIG-U05-18（P59，cols 一栏，viewBox 800×700）。
环节视图：FASTQ（N 条）→ bwa mem 中途死亡（红叉）→ samtools sort 把残流当正常结束
→ BAM 0 条记录、rc=0（橙）；灰支线 index/flagstat 照常成功；
红条 rc=0 ≠ 完整，破绽只有记录数。数字（0 条、rc=0）带教材 §7.5.2 L365–369 入口
（「本机实测，非课程 pin」口径由 deck 页面 ref 承载）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 18_silent_empty_bam.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    y0, bh = 150, 110
    boxes = [(25, CYAN, "FASTQ"), (215, BLUE, "bwa mem"),
             (405, BLUE, "samtools sort"), (595, ORANGE, "BAM")]

    for x, color, _ in boxes:
        s.rect(x, y0, 160, bh, color, rx=14)
    for x in (187, 377, 567):
        s.arrow(x + 3, 205, x + 24, 205, GRAY, 6, head=16)

    # ① FASTQ（N 条）
    s.text(105, 192, "FASTQ", 30, WHITE, "middle", "bold")
    s.text(105, 232, "N reads", 30, WHITE, "middle", "bold")

    # ② bwa mem 中途死亡（红叉，2/2 红）
    s.text(295, 184, "bwa mem", 30, WHITE, "middle", "bold")
    s.line(238, 198, 352, 252, RED, 6)
    s.line(352, 198, 238, 252, RED, 6)
    s.text(295, 300, "中途死亡", 30, RED, "middle", "bold")
    s.text(295, 340, "(OOM / killed)", 30, GRAY, "middle", "bold")

    # ③ samtools sort 把残流当正常结束
    s.text(485, 190, "samtools", 30, WHITE, "middle", "bold")
    s.text(485, 228, "sort", 30, WHITE, "middle", "bold")
    s.text(485, 302, "把残流当正常结束", 30, INK, "middle", "bold")

    # ④ BAM：0 条记录，rc=0（橙格）
    s.text(675, 185, "BAM", 30, INK, "middle", "bold")
    s.text(675, 222, "0 条记录", 30, INK, "middle", "bold")
    s.text(675, 252, "rc = 0", 30, INK, "middle", "bold")

    # 灰色支线：index / flagstat 照常成功
    s.line(675, 262, 675, 392, GRAY, 4, dash="10 8")
    s.rect(585, 396, 180, 52, PANEL, rx=10)
    s.text(675, 432, "index ✓", 30, GRAY, "middle", "bold")
    s.rect(585, 456, 180, 52, PANEL, rx=10)
    s.text(675, 492, "flagstat ✓", 30, GRAY, "middle", "bold")
    s.text(675, 548, "照常成功", 30, INK, "middle", "bold")

    # 底部红条
    s.rect(25, 592, 730, 64, RED, rx=12)
    s.text(390, 633, "rc=0 ≠ 完整——破绽只有记录数", 32, WHITE, "middle",
           "bold")

    s.save("18_silent_empty_bam.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

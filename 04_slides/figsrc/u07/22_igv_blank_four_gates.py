#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""22_igv_blank_four_gates.py — 生成 22_igv_blank_four_gates.svg（FIG-U07-22：IGV 空白排查四步闸门）

方案：reviews/course/U07_FIGP_001.md §4.2 FIG-U07-22（P65，cols 一栏，viewBox 800×700）。
数据：无量字数字。四步闸门：seqid 逐字一致 → 窗口缩至三十 kb 内 →
切尾免挂起 → @SQ 头行对齐（教材 §9.4.6 L268–282、§9.5.2、§9.5.3；
30 kb 为常见默认显示设置，非永久硬限制）。闸门细则用英文标注不占汉字预算。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 22_igv_blank_four_gates.py
"""
from svghelp import *  # noqa: F401,F403

GATES = [
    ("代号逐字一致", "seqid == FASTA header"),
    ("窗口缩至三十内", "window < 30 kb"),
    ("切尾免挂起", "cut ##FASTA"),
    ("头行对齐", "@SQ SN/LN == FASTA"),
]


def main():
    s = SVG(800, 700)

    for i, (name, sub) in enumerate(GATES):
        y = 70 + i * 128
        if i < 3:
            s.line(78, y + 68, 78, y + 128 + 12, GRAY, 4)
        s.circle(78, y + 40, 32, BLUE)
        s.text(78, y + 51, str(i + 1), 32, WHITE, "middle", "bold")
        s.rect(130, y, 510, 96, GREEN_TINT, GREEN, 5, rx=14)
        s.text(160, y + 42, name, 32, BLUE, "start", "bold")
        s.text(160, y + 80, sub, 30, GRAY, "start")

    # 底部红色排查结论条（唯一红色）
    s.rect(240, 606, 320, 58, RED, rx=12)
    s.text(400, 647, "四步排空白", 34, WHITE, "middle", "bold")

    s.save("22_igv_blank_four_gates.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

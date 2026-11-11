#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_three_gates.py — 生成 15_three_gates.svg（FIG-U03-15：格式排查三道只读闸门）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-15（P41，cols 一栏，800×700）。
教材依据：chapters/ch05/manuscript.qmd §5.4.1。
闸门 1 `file` 看真实类型 → 闸门 2 查魔数 1f 8b → 闸门 3 安全取首行看 >/@ 与四行结构。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 15_three_gates.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 50, "排查三道闸门", 36, BLUE, "middle", "bold")
    s.text(400, 92, "类型魔数首字符，解压看结构", 30, GRAY, "middle", "bold")

    def gate(y, num, cmd, out, out_color):
        s.rect(50, y, 700, 128, "#F0F9FF", BLUE, 4, rx=16)
        s.circle(100, y + 64, 30, BLUE)
        s.text(100, y + 75, num, 32, WHITE, "middle", "bold")
        s.rect(150, y + 18, 560, 48, "#1E293B", rx=8)
        s.text(170, y + 52, cmd, 30, WHITE, "start", "bold")
        s.text(170, y + 108, out, 30, out_color, "start", "bold")

    gate(130, "1", 'file "$F"', "→ ASCII text ｜ gzip compressed", GREEN)
    gate(290, "2", 'head -c 2 "$F" | od -An -tx1',
         "→ 1f 8b = gzip ｜ 其他", GREEN)
    gate(450, "3", 'zcat "$F" | head -1 ｜ head -1 "$F"',
         "→ 首字符 > 或 @", CYAN_DEEP)

    # 红色焦点：非 gzip 直接 zcat 的报错
    s.rect(40, 606, 720, 60, RED, rx=12)
    s.text(400, 646, "非 gzip 直接 zcat：必报 not in gzip format", 28,
           WHITE, "middle", "bold")

    s.save("15_three_gates.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_cigar_accounting.py — 生成 18_cigar_accounting.svg（FIG-U03-18：CIGAR 双向对账）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-18（P45，cols 一栏，800×700）。
教材依据：chapters/ch05/manuscript.qmd §5.4.6、§5.5.3；demos/ch05_flag_cigar.py。
查询消耗 = M+I+S（读段长度）；参考跨度 = M+D。算例 50M2D10M 与 10S130M2I8M。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 18_cigar_accounting.py
"""
from svghelp import *  # noqa: F401,F403

M_COL, I_COL, D_COL, S_COL = "#2563EB", "#D97706", "#9333EA", "#6B7280"


def seg_bar(s, x, y, total_w, segs, h=44):
    """按比例画 CIGAR 区段条；窄区段（D/I）标签放到条上方避免溢出。"""
    total = sum(n for _, n in segs)
    cx = x
    for op, n in segs:
        w = total_w * n / total
        color = {"M": M_COL, "I": I_COL, "D": D_COL, "S": S_COL}[op]
        if op == "D":
            s.rect(cx, y + h + 8, max(w, 18), 16, color, rx=4)
            s.text(cx + max(w, 18) / 2, y - 10, f"{n}{op}", 26, color,
                   "middle", "bold")
        else:
            s.rect(cx, y, w, h, color, rx=4)
            if w >= 34:
                sz = 28 if w >= 60 else 24
                s.text(cx + w / 2, y + h / 2 + 10, f"{n}{op}", sz, WHITE,
                       "middle", "bold")
            else:
                s.text(cx + w / 2, y - 10, f"{n}{op}", 26, color, "middle",
                       "bold")
        cx += w


def example(s, y, cigar, segs, qry, ref):
    s.text(70, y - 28, cigar, 32, BLUE, "start", "bold")
    seg_bar(s, 70, y + 6, 660, segs)
    s.text(70, y + 108, f"Qry {qry} bp", 30, INK, "start", "bold")
    s.text(420, y + 108, f"Ref {ref} bp", 30, INK, "start", "bold")


def main():
    s = SVG(800, 700)
    s.text(400, 48, "查询消耗比参考跨度", 34, BLUE, "middle", "bold")
    s.text(400, 88, "删除占参考，编辑距离非错配", 30, GRAY, "middle", "bold")

    # 两条对账算式
    s.rect(50, 116, 340, 66, BLUE_TINT, BLUE, 4, rx=12)
    s.text(220, 160, "查询消耗 = M + I + S", 30, BLUE, "middle", "bold")
    s.rect(420, 116, 330, 66, BLUE_TINT, BLUE, 4, rx=12)
    s.text(585, 160, "参考跨度 = M + D", 30, BLUE, "middle", "bold")

    example(s, 250, "50M2D10M", [("M", 50), ("D", 2), ("M", 10)], 60, 62)
    example(s, 450, "10S130M2I8M", [("S", 10), ("M", 130), ("I", 2), ("M", 8)],
            150, 138)

    # 红色焦点：NM 的口径
    s.rect(170, 622, 460, 56, RED, rx=12)
    s.text(400, 660, "NM 含 indel", 30, WHITE, "middle", "bold")

    s.save("18_cigar_accounting.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_n50_cumulative.py — 生成 11_n50_cumulative.svg（FIG-U06-11：N50/L50 累计算法）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-11（P32，cols 一栏，viewBox 800×700）【data-plot】。
数据（与 demos 现跑一致）：demos/ch08_n50_vs_completeness.py --example 1（设例）：
contigs = 100/80/50/40/30 kb → 总长 300 kb、50% 阈值 150 kb、N50=80 kb、L50=2。
"达到或超过"即停（不是"首次超过"，教材 §8.4.7 L250 边界例 50/30/20）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 11_n50_cumulative.py
"""
import html
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from ch08_n50_vs_completeness import n50_l50  # noqa: E402

OUT = ROOT / "04_slides" / "undergraduate" / "imgs" / "06_assembly_basics"
OUT.mkdir(parents=True, exist_ok=True)

FONT = 'Noto Sans CJK SC, PingFang SC, sans-serif'
PAPER = "#FAFAF7"
WHITE = "#FFFFFF"
INK = "#33332E"
GRAY = "#6B6B66"
PANEL = "#E9E9E5"
BLUE = "#3C5488"
CYAN = "#4DBBD5"
GREEN = "#00A087"
ORANGE = "#F39B7F"
PURPLE = "#8491B4"
RED = "#E64B35"


class SVG:
    def __init__(self, w=800, h=700):
        self.w, self.h = w, h
        self.parts = []

    def raw(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill="none", stroke=None, sw=4, rx=0, dash=None):
        a = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"')
        if rx:
            a += f' rx="{rx}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        self.raw(a + "/>")

    def line(self, x1, y1, x2, y2, stroke, sw=4, dash=None, cap="butt"):
        a = (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
             f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}"')
        if dash:
            a += f' stroke-dasharray="{dash}"'
        self.raw(a + "/>")

    def polyline(self, pts, stroke, sw=4, fill="none", dash=None):
        p = " ".join(f"{x},{y}" for x, y in pts)
        a = (f'<polyline points="{p}" fill="{fill}" stroke="{stroke}" '
             f'stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"')
        if dash:
            a += f' stroke-dasharray="{dash}"'
        self.raw(a + "/>")

    def polygon(self, pts, fill, stroke=None, sw=4):
        p = " ".join(f"{x},{y}" for x, y in pts)
        a = f'<polygon points="{p}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        self.raw(a + "/>")

    def path(self, d, stroke=None, sw=4, fill="none", dash=None):
        a = f'<path d="{d}" fill="{fill}"'
        if stroke:
            a += (f' stroke="{stroke}" stroke-width="{sw}" '
                  f'stroke-linejoin="round" stroke-linecap="round"')
        if dash:
            a += f' stroke-dasharray="{dash}"'
        self.raw(a + "/>")

    def circle(self, cx, cy, r, fill="none", stroke=None, sw=4, dash=None):
        a = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        self.raw(a + "/>")

    def text(self, x, y, s, size=32, fill=INK, anchor="start", weight=None):
        a = (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
             f'fill="{fill}" text-anchor="{anchor}"')
        if weight:
            a += f' font-weight="{weight}"'
        self.raw(a + f">{html.escape(s)}</text>")

    def arrow(self, x1, y1, x2, y2, color, sw=6, head=18):
        ang = math.atan2(y2 - y1, x2 - x1)
        self.line(x1, y1, x2, y2, color, sw, cap="round")
        self.polygon([
            (x2, y2),
            (x2 - head * math.cos(ang - 0.42), y2 - head * math.sin(ang - 0.42)),
            (x2 - head * math.cos(ang + 0.42), y2 - head * math.sin(ang + 0.42)),
        ], color)

    def save(self, name):
        doc = (f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {self.w} {self.h}">\n'
               f'<rect width="{self.w}" height="{self.h}" fill="{PAPER}"/>\n'
               + "\n".join(self.parts) + "\n</svg>\n")
        (OUT / name).write_text(doc, encoding="utf-8")
        print(f"wrote {OUT / name}")


def main():
    # 与 demos --example 1 相同的设例（教材 §8.4.7 L252 手算例）
    contigs = [100, 80, 50, 40, 30]
    n50, l50, total = n50_l50(contigs)
    assert (n50, l50, total) == (80, 2, 300)
    half = total / 2
    print(f"check: 总长 {total} kb，阈值 {half:g} kb，N50={n50} kb，L50={l50}")

    s = SVG(800, 700)
    X0, SCALE = 110, 2.1  # px/kb；累计 300 kb → 740
    s.text(70, 76, "从长到短累计", 32, INK, "start", "bold")
    s.text(425, 76, "一半 = 150", 32, BLUE, "middle", "bold")
    s.text(740, 76, "\"达到\"就停", 32, RED, "end", "bold")

    # 阈值竖虚线（深蓝色，"达到或超过"即停）
    tx = X0 + half * SCALE
    s.line(tx, 96, tx, 476, BLUE, 4, dash="14 10")

    # 五根条（长到短）+ 右端累计刻度
    cum = 0
    for i, ln in enumerate(contigs):
        y = 110 + i * 75
        cum += ln
        color = GREEN if i == l50 - 1 else BLUE
        s.rect(X0, y, ln * SCALE, 56, color, rx=6)
        s.text(X0 + 14, y + 38, str(ln), 32, WHITE, "start", "bold")
        cx = X0 + cum * SCALE
        s.line(cx, 484, cx, 496, INK, 3)
        s.text(cx, 532, str(cum), 30, GRAY, "middle")

    # N50 角标（第二条右端）+ 说明
    s.rect(X0 + 80 * SCALE + 8, 191, 74, 44, GREEN, rx=8)
    s.text(X0 + 80 * SCALE + 45, 223, "N50", 30, WHITE, "middle", "bold")
    s.text(320, 592, "第二条恰好越阈", 30, INK, "middle", "bold")

    # 底部结果条
    s.rect(170, 624, 460, 62, BLUE, rx=12)
    s.text(400, 668, "N50 = 80，L50 = 2", 36, WHITE, "middle", "bold")

    s.save("11_n50_cumulative.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

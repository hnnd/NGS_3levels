#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""03_kmer_slicing.py — 生成 03_kmer_slicing.svg（FIG-U06-03：k-mer 滑窗切分与计数）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-03（P12，cols 一栏，viewBox 800×700）。
数据：算术 L−k+1（L=100：k=21→80、k=31→70；少了 (80−70)/80 = 12.5%），
教材 §8.4.3 L127、§8.4.4 L167。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 03_kmer_slicing.py
"""
import html
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # NGS_3Levels/
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
    # 数据自检（算术，教材 §8.4.3 L127 / §8.4.4 L167）
    L = 100
    n21, n31 = L - 21 + 1, L - 31 + 1
    drop = (n21 - n31) / n21
    assert (n21, n31) == (80, 70) and abs(drop - 0.125) < 1e-12
    print(f"check: L-k+1 → k=21:{n21} k=31:{n31}; (80-70)/80={drop:.1%}")

    PX_PER_BP = 6.4  # 100 bp → 640 px
    s = SVG(800, 700)

    s.text(400, 60, "一条读段，滑窗切 k-mer", 36, INK, "middle", "bold")

    # read 条（青蓝，序列）+ 右端 100 bp
    s.rect(80, 100, 640, 36, CYAN, rx=6)
    s.text(720, 92, "100 bp", 30, GRAY, "end")

    # k=21 滑窗（深蓝）与 k=31 滑窗（橙），上下错开，各带右移箭头
    w21, w31 = 21 * PX_PER_BP, 31 * PX_PER_BP
    # k=21 滑窗（深蓝）与 k=31 滑窗（橙），上下错开，各带右移箭头；
    # 窗后垫淡青 read 参照条（同一条读段的两个窗口位置）
    s.raw(f'<rect x="80" y="200" width="640" height="34" rx="6" fill="{CYAN}" '
          f'opacity="0.28"/>')
    s.raw(f'<rect x="80" y="344" width="640" height="34" rx="6" fill="{CYAN}" '
          f'opacity="0.28"/>')
    s.rect(140, 178, w21, 78, "none", BLUE, 6, rx=8)
    s.text(140, 168, "k=21：80 个", 32, BLUE, "start", "bold")
    s.arrow(140 + w21 + 10, 217, 140 + w21 + 76, 217, BLUE, 6)

    s.rect(220, 322, w31, 78, "none", ORANGE, 6, rx=8)
    s.text(220, 312, "k=31：70 个", 32, INK, "start", "bold")
    s.arrow(220 + w31 + 10, 361, 220 + w31 + 76, 361, ORANGE, 6)

    # 公式条
    s.rect(230, 452, 340, 84, WHITE, PANEL, 3, rx=12)
    s.text(400, 508, "L − k + 1", 44, BLUE, "middle", "bold")

    # 红色结论条（唯一红色：k 变大的代价）
    s.rect(230, 586, 340, 72, RED, rx=12)
    s.text(400, 634, "少了 12.5%", 38, WHITE, "middle", "bold")

    s.save("03_kmer_slicing.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_flye_repeat_graph.py — 生成 10_flye_repeat_graph.svg（FIG-U06-10：Flye 重复图）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-10（P31，cols 一栏，viewBox 800×700）。
机制示意（无量字数字）：压缩长片段 → 重复单元标在图上 → 分叉点靠长读段定向（红色跨越弧）。
图内不得出现提速倍数（ALN W6）；circ. 判读留在 deck P41 文字。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 10_flye_repeat_graph.py
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
    s = SVG(800, 700)

    # 第一行：基因组条（两处橙块＝重复拷贝）
    s.rect(80, 70, 220, 36, CYAN, rx=6)      # U1
    s.rect(300, 70, 80, 36, ORANGE, rx=6)    # R1
    s.rect(380, 70, 140, 36, CYAN, rx=6)     # U2
    s.rect(520, 70, 80, 36, ORANGE, rx=6)    # R2
    s.rect(600, 70, 120, 36, CYAN, rx=6)     # U3
    s.text(400, 148, "先把重叠压成长片段", 32, INK, "middle", "bold")
    s.arrow(400, 168, 400, 212, CYAN, 7)

    # 第二行：三条深蓝长片段 + 中央共享橙节点 R（虚线对齐上下片段）
    s.rect(120, 236, 560, 26, BLUE, rx=6)
    s.rect(120, 290, 560, 26, BLUE, rx=6)
    s.rect(120, 344, 560, 26, BLUE, rx=6)
    s.line(400, 262, 400, 290, ORANGE, 4, dash="10 8")
    s.line(400, 344, 400, 370, ORANGE, 4, dash="10 8")
    s.rect(370, 262, 60, 82, ORANGE, rx=10)
    s.text(400, 414, "重复单元标在图上", 32, INK, "middle", "bold")
    s.arrow(400, 434, 400, 478, CYAN, 7)

    # 第三行：分叉点靠红色长读段弧定向
    s.rect(120, 502, 190, 26, BLUE, rx=6)
    s.rect(490, 502, 190, 26, BLUE, rx=6)
    s.rect(378, 490, 44, 56, ORANGE, rx=8)
    s.path("M 160 502 C 280 448, 520 448, 640 502", RED, 7)
    s.arrow(400, 449, 400, 484, RED, 7)
    s.text(400, 580, "分叉点靠长读段定向", 32, INK, "middle", "bold")

    s.save("10_flye_repeat_graph.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

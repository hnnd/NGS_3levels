#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_k_tradeoff.py — 生成 07_k_tradeoff.svg（FIG-U06-07：k 太小碰撞 / 太大含错）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-07（P19，cols 一栏，viewBox 800×700）。
数据：4^11=4,194,304（demos/ch08_kmer_spectrum.py 打印的空间容量）；
19.0% = 1−0.99^21、26.8% = 1−0.99^31（算术，教材 §8.4.4 L167）；
read 条切剩 70 = L−k+1（100−31+1，教材 §8.4.3 L127）。
图内不写「重复高估、大小低估、主峰右移」方向句（ALN W8）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 07_k_tradeoff.py
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
    # 数据自检
    assert 4 ** 11 == 4194304
    p21 = 1 - 0.99 ** 21
    p31 = 1 - 0.99 ** 31
    assert abs(p21 - 0.190) < 5e-4 and abs(p31 - 0.268) < 5e-4
    assert 100 - 31 + 1 == 70
    print(f"check: 4^11={4**11:,}；1−0.99^21={p21:.1%}；1−0.99^31={p31:.1%}；"
          f"L−k+1=70")

    s = SVG(800, 700)

    # 上面板：k 太小 → 碰撞（面板底灰）
    s.rect(40, 40, 720, 300, PANEL, rx=16)
    s.text(70, 100, "k=11：空间不够", 34, BLUE, "start", "bold")

    # 空间数字牌
    s.rect(70, 130, 280, 110, WHITE, PANEL, 3, rx=12)
    s.text(95, 178, "4^11", 40, BLUE, "start", "bold")
    s.text(95, 218, "= 4,194,304 种", 34, INK, "start", "bold")

    # 两个不同位点（青蓝方块 / 紫方块）被同一引力圈吸到一起
    s.rect(470, 140, 64, 64, CYAN, rx=8)
    s.rect(620, 140, 64, 64, PURPLE, rx=8)
    s.arrow(536, 190, 566, 246, RED, 6)
    s.arrow(618, 190, 588, 246, RED, 6)
    s.circle(577, 288, 52, "none", RED, 6, dash="16 12")
    # 碰撞闪光
    cx, cy = 577, 288
    for ang in (0.6, 2.2, 3.8, 5.4):
        s.line(cx + 20 * math.cos(ang), cy - 20 * math.sin(ang),
               cx + 38 * math.cos(ang), cy - 38 * math.sin(ang), RED, 6,
               cap="round")
    s.text(400, 326, "不同位点互相撞", 30, INK, "middle", "bold")

    # 下面板：k 太大 → 含错（左 read 切片示意，右两根并列竖柱）
    s.rect(40, 366, 720, 250, PANEL, rx=16)
    # read 条被切剩 70 的碎片（左）
    s.text(70, 418, "read", 30, GRAY, "start", "bold")
    s.rect(70, 436, 160, 30, CYAN, rx=6)
    s.rect(150, 424, 90, 54, "none", ORANGE, 5, rx=8)
    s.arrow(248, 451, 286, 451, ORANGE, 6)
    s.rect(292, 436, 78, 30, CYAN, rx=6)
    s.text(331, 505, "70", 30, GRAY, "middle", "bold")

    # 右：含错概率两根并列竖柱（柱上方标值、柱下方标 k）
    s.text(405, 408, "含错", 30, INK, "start", "bold")
    s.line(425, 560, 685, 560, GRAY, 4)
    base = 560
    h21, h31 = 99, 140                       # 19.0 : 26.8 同比缩放
    s.rect(440, base - h21, 90, h21, ORANGE, rx=6)
    s.rect(570, base - h31, 90, h31, RED, rx=6)
    s.text(485, base - h21 - 12, "19.0%", 30, INK, "middle", "bold")
    s.text(615, base - h31 - 12, "26.8%", 30, INK, "middle", "bold")
    s.text(485, base + 42, "k=21", 30, INK, "middle", "bold")
    s.text(615, base + 42, "k=31", 30, INK, "middle", "bold")

    # 底部结论条（深蓝）
    s.rect(150, 642, 500, 54, BLUE, rx=12)
    s.text(400, 680, "k=21 是起点，不是最优", 32, WHITE, "middle", "bold")

    s.save("07_k_tradeoff.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

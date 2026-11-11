#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_kminus1_boundary.py — 生成 08_kminus1_boundary.svg 与 08_kminus1_boundary_wide.svg
（FIG-U06-08：de Bruijn 图 k−1 与重复长度 R 的三种关系，FT08-02 落地）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-08（P27，cols）；editor_notes Q2：
同时给 cols 用 800×700 与 figure 用 1600×900（文件名加 _wide）。
数据（与 demos 现跑一致）：demos/ch08_debruijn_repeat.py --selftest
（R=100、侧翼 300、种子 20261102）：k−1=96→分叉 2；k−1=100→共享 k-mer 0、
多拷贝节点 1、分叉 1；k−1=101→全 0。本脚本直接调用该 demos 的函数复算并断言。
无网络；种子固定。用法：PYTHONDONTWRITEBYTECODE=1 python3 08_kminus1_boundary.py
"""
import html
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]  # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch08_debruijn_repeat as demo  # noqa: E402

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
    def __init__(self, w, h):
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

    def arrow(self, x1, y1, x2, y2, color, sw=7, head=20):
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


def check_data():
    """复算 demos 的三情形数字（R=100、flank=300、种子 20261102）。"""
    rng = np.random.default_rng(20261102)
    genome, rep1, rep2 = demo.build_genome(rng, 300, 100)
    cases = {}
    for k in (97, 101, 102):
        cases[k - 1] = demo.dbg_stats(genome, k)
    assert cases[96] == (4, 5, 2), cases[96]
    assert cases[100] == (0, 1, 1), cases[100]
    assert cases[101] == (0, 0, 0), cases[101]
    print(f"check: k−1=96→共享/多拷贝/分叉 {cases[96]}；k−1=100→{cases[100]}；"
          f"k−1=101→{cases[101]}")
    return {96: 2, 100: 1, 101: 0}


def genome_bar(s, x0, y, w, h, annot_size):
    """U1–R–U2–R–U3 基因组条（300/100/300/100/300 bp 等比）。"""
    scale = w / 1100.0
    u, r = 300 * scale, 100 * scale
    segs = [("U1", x0, u, CYAN), ("R", x0 + u, r, ORANGE),
            ("U2", x0 + u + r, u, CYAN), ("R", x0 + 2 * u + r, r, ORANGE),
            ("U3", x0 + 2 * u + 2 * r, u, CYAN)]
    for name, sx, sw, color in segs:
        s.rect(sx, y, sw, h, color, rx=4)
        tcol = WHITE if color == CYAN else INK
        s.text(sx + sw / 2, y + h / 2 + annot_size * 0.36, name,
               annot_size, tcol, "middle", "bold")
    # R=100 bp 标注（第一处 R 上方）
    rcx = x0 + u + r / 2
    s.line(rcx, y - 6, rcx, y - 22, GRAY, 3)
    s.text(rcx, y - 30, "R=100 bp", annot_size, INK, "middle", "bold")


def panel(s, x, y, w, h, title, tsize):
    s.rect(x, y, w, h, WHITE, PANEL, 3, rx=14)
    s.text(x + w / 2, y + 52, title, tsize, BLUE, "middle", "bold")


def branch_badge(s, x_right, y, num, lab_size, num_size, fill=BLUE):
    s.text(x_right, y, "分叉", lab_size, GRAY, "end", "bold")
    s.text(x_right, y + num_size * 1.15, str(num), num_size, fill, "end",
           "bold")


def draw_narrow(branch):
    """cols 版：viewBox 800×700。"""
    s = SVG(800, 700)
    genome_bar(s, 80, 88, 641, 36, 30)

    pw, ph, py = 225, 396, 150
    xs = [40, 287, 534]
    titles = ["k−1 < R", "k−1 = R", "k−1 > R"]
    caps = [(152, ["两个出口：", "路径不唯一"]),
            (400, ["重复 R 达到 k−1：", "共享节点"]),
            (646, ["单链：无歧义"])]
    for x, t in zip(xs, titles):
        panel(s, x, py, pw, ph, t, 32)
    for (cx, lines) in caps:
        for j, ln in enumerate(lines):
            s.text(cx, 585 + j * 42, ln, 30, INK, "middle", "bold")

    # (a) k−1 < R：两拷贝汇入共享区，红色两个出口
    xa = xs[0]
    s.arrow(xa + 22, 340, xa + 82, 348, BLUE, 7)
    s.arrow(xa + 22, 430, xa + 82, 388, BLUE, 7)
    s.rect(xa + 84, 336, 52, 84, ORANGE, rx=8)
    s.arrow(xa + 138, 358, xa + 196, 318, RED, 7)
    s.arrow(xa + 138, 392, xa + 196, 442, RED, 7)
    branch_badge(s, xa + pw - 14, py + 78, branch[96], 30, 56)

    # (b) k−1 = R：单个 2 进 2 出共享节点（红描边），保守组装器仍断
    xb = xs[1]
    s.arrow(xb + 22, 300, xb + 78, 306, BLUE, 7)
    s.arrow(xb + 22, 400, xb + 78, 370, BLUE, 7)
    s.rect(xb + 80, 296, 62, 84, ORANGE, RED, 6, rx=8)
    s.arrow(xb + 144, 306, xb + 203, 300, BLUE, 7)
    s.arrow(xb + 144, 370, xb + 203, 400, BLUE, 7)
    branch_badge(s, xb + pw - 14, py + 78, branch[100], 30, 56)

    # (c) k−1 > R：绿色单链贯通
    xc = xs[2]
    s.arrow(xc + 22, 338, xc + 203, 338, GREEN, 8)
    s.circle(xc + 82, 338, 7, GREEN)
    s.circle(xc + 142, 338, 7, GREEN)
    branch_badge(s, xc + pw - 14, py + 78, branch[101], 30, 56)

    s.save("08_kminus1_boundary.svg")


def draw_wide(branch):
    """figure 整页版：viewBox 1600×900（editor_notes Q2 裁定）。"""
    s = SVG(1600, 900)
    genome_bar(s, 160, 110, 1280, 48, 34)

    pw, ph, py = 430, 480, 210
    xs = [60, 585, 1110]
    titles = ["k−1 < R", "k−1 = R", "k−1 > R"]
    caps = [(275, ["两个出口：", "路径不唯一"]),
            (800, ["重复 R 达到 k−1：", "共享节点"]),
            (1325, ["单链：无歧义"])]
    for x, t in zip(xs, titles):
        panel(s, x, py, pw, ph, t, 40)
    for (cx, lines) in caps:
        for j, ln in enumerate(lines):
            s.text(cx, 760 + j * 52, ln, 36, INK, "middle", "bold")

    # (a)
    xa = xs[0]
    s.arrow(xa + 40, 380, xa + 148, 396, BLUE, 9)
    s.arrow(xa + 40, 520, xa + 148, 452, BLUE, 9)
    s.rect(xa + 154, 380, 100, 140, ORANGE, rx=10)
    s.arrow(xa + 258, 412, xa + 300, 340, RED, 9)
    s.arrow(xa + 258, 488, xa + 300, 590, RED, 9)
    branch_badge(s, xa + pw - 24, py + 96, branch[96], 34, 80)

    # (b)
    xb = xs[1]
    s.arrow(xb + 40, 380, xb + 128, 388, BLUE, 9)
    s.arrow(xb + 40, 520, xb + 128, 472, BLUE, 9)
    s.rect(xb + 146, 380, 108, 140, ORANGE, RED, 8, rx=10)
    s.arrow(xb + 258, 392, xb + 300, 384, BLUE, 9)
    s.arrow(xb + 258, 468, xb + 300, 516, BLUE, 9)
    branch_badge(s, xb + pw - 24, py + 96, branch[100], 34, 80)

    # (c)
    xc = xs[2]
    s.arrow(xc + 40, 450, xc + 396, 450, GREEN, 10)
    s.circle(xc + 150, 450, 10, GREEN)
    s.circle(xc + 270, 450, 10, GREEN)
    branch_badge(s, xc + pw - 24, py + 96, branch[101], 34, 80)

    s.save("08_kminus1_boundary_wide.svg")


def main():
    branch = check_data()
    draw_narrow(branch)
    draw_wide(branch)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

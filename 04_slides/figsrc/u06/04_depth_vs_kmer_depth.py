#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_depth_vs_kmer_depth.py — 生成 04_depth_vs_kmer_depth.svg（FIG-U06-04：D_k 与 D 的关系）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-04（P14，cols 一栏，viewBox 800×700）【data-plot】。
数据（与 demos 现跑一致）：demos/ch08_kmer_spectrum.py --selftest 场景一
（G=40,000、D=30×、L=100、k=21、e=0.01、种子 20261102）：
  理论期望 D_k ≈ 30×(80/100)×0.99^21 ≈ 19.4×；脚本主峰 19×。
无网络；种子固定（20261102）。用法：PYTHONDONTWRITEBYTECODE=1 python3 04_depth_vs_kmer_depth.py
"""
import html
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]  # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch08_kmer_spectrum as demo  # noqa: E402

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
    # 与 demos 场景一完全相同的合成流程（固定种子），取主峰深度
    rng = np.random.default_rng(20261102)
    genome = demo.random_genome(rng, 40000)
    reads = demo.simulate_reads(genome, 30, 100, 0.01, rng)
    hashes = demo.canonical_kmer_hashes(reads, 21)
    _, counts = np.unique(hashes, return_counts=True)
    hist = np.bincount(counts, minlength=int(counts.max()) + 1)
    sm = demo.smooth(hist.astype(float))
    body = sm[4:]
    sig = [4 + p for p in demo.local_maxima(body, min_height=0.08 * body.max())]
    peak = max(sig)
    depth, L, k, e = 30, 100, 21, 0.01
    expect = depth * (L - k + 1) / L * (1 - e) ** k
    assert peak == 19, f"主峰应为 19×（demos 现跑），得 {peak}"
    assert abs(expect - 19.4) < 0.05, f"理论期望应 ≈19.4×，得 {expect}"
    print(f"check: 主峰 {peak}×，理论期望 {expect:.1f}×（demos 场景一复算）")

    s = SVG(800, 700)

    # 输入框：测序深度 D（深蓝）
    s.rect(250, 76, 300, 92, BLUE, rx=14)
    s.text(400, 118, "测序深度 D", 34, WHITE, "middle", "bold")
    s.text(400, 156, "D = 30×", 36, WHITE, "middle", "bold")

    # 两个算子环（青蓝，数据流）
    s.arrow(360, 172, 300, 196, CYAN, 7)
    s.arrow(440, 172, 500, 196, CYAN, 7)
    s.circle(270, 270, 80, CYAN)
    s.text(270, 263, "× 0.80", 36, WHITE, "middle", "bold")
    s.text(270, 301, "(L−k+1)/L", 30, WHITE, "middle", "bold")
    s.circle(530, 270, 80, CYAN)
    s.text(530, 263, "× 0.81", 36, WHITE, "middle", "bold")
    s.text(530, 301, "(1−e)^k", 30, WHITE, "middle", "bold")

    # 结果框（绿，正常态）
    s.arrow(300, 354, 365, 420, CYAN, 7)
    s.arrow(500, 354, 435, 420, CYAN, 7)
    s.rect(250, 424, 300, 96, GREEN, rx=14)
    s.text(400, 468, "k-mer 深度 D_k", 34, WHITE, "middle", "bold")
    s.text(400, 510, "≈ 19.4×", 40, WHITE, "middle", "bold")

    # 现跑主峰角标（D_k 框正下方，四周 ≥24 单位空白）
    s.rect(260, 544, 280, 48, GREEN, rx=12)
    s.text(400, 580, "主峰 19×（现跑）", 30, WHITE, "middle", "bold")

    # 红色警示条（唯一红色）
    s.rect(170, 616, 460, 56, RED, rx=12)
    s.text(400, 654, "当 D 用→低估", 34, WHITE, "middle", "bold")

    s.save("04_depth_vs_kmer_depth.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

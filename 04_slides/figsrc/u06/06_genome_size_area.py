#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_genome_size_area.py — 生成 06_genome_size_area.svg（FIG-U06-06：基因组大小＝面积÷主峰）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-06（P17，cols 一栏，viewBox 800×700）【data-plot】。
数据（与 demos 场景一现跑一致）：主峰 19×、G_est=40,976 bp（偏差 2.4%）、i_min=4；
谱形与面积直接用 demos/ch08_kmer_spectrum.py 的函数复算（种子 20261102）。
纵轴为对数示意（角注「对数示意」），不标实测刻度。无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 06_genome_size_area.py
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
GREEN_TINT = "#D8EEE9"
RED_TINT = "#F6D8D2"


class SVG:
    def __init__(self, w=800, h=700):
        self.w, self.h = w, h
        self.parts = []
        self.defs = []

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

    def polygon(self, pts, fill, stroke=None, sw=4, opacity=None):
        p = " ".join(f"{x},{y}" for x, y in pts)
        a = f'<polygon points="{p}" fill="{fill}"'
        if opacity:
            a += f' opacity="{opacity}"'
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

    def curve(self, pts, color, sw=5):
        if len(pts) < 3:
            self.polyline(pts, color, sw)
            return
        d = f"M {pts[0][0]} {pts[0][1]}"
        n = len(pts)
        for i in range(n - 1):
            p0 = pts[max(i - 1, 0)]
            p1 = pts[i]
            p2 = pts[i + 1]
            p3 = pts[min(i + 2, n - 1)]
            # 端点切线压平（p3 钳位会让尾端上翘）
            c1 = p1 if i == 0 else (p1[0] + (p2[0] - p0[0]) / 6,
                                    p1[1] + (p2[1] - p0[1]) / 6)
            c2 = p2 if i == n - 2 else (p2[0] - (p3[0] - p1[0]) / 6,
                                        p2[1] - (p3[1] - p1[1]) / 6)
            d += (f" C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} "
                  f"{p2[0]} {p2[1]}")
        self.path(d, color, sw)

    def clip(self, cid, pts):
        p = " ".join(f"{x},{y}" for x, y in pts)
        self.defs.append(f'<clipPath id="{cid}"><polygon points="{p}"/></clipPath>')
        return f"url(#{cid})"

    def save(self, name):
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        doc = (f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {self.w} {self.h}">\n'
               f'<rect width="{self.w}" height="{self.h}" fill="{PAPER}"/>\n'
               + defs + "\n" + "\n".join(self.parts) + "\n</svg>\n")
        (OUT / name).write_text(doc, encoding="utf-8")
        print(f"wrote {OUT / name}")


def main():
    # 与 demos --selftest 场景一完全相同的合成流程（固定种子 20261102）
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
    g_est = float(sum(i * hist[i] for i in range(4, len(hist)))) / peak
    assert peak == 19, f"主峰应为 19×，得 {peak}"
    assert abs(g_est - 40976) < 1, f"G_est 应为 40,976 bp，得 {g_est:.0f}"
    print(f"check: 主峰 {peak}×，G_est={g_est:,.0f} bp（偏差 "
          f"{abs(g_est - 40000) / 40000:.1%}）")

    # 画布坐标：深度 0–dmax → x 90–700；log10(1+N) → y 100–470
    X0, X1, Y0, Y1 = 90, 700, 100, 470
    dmax = len(sm) - 1  # 实测最大深度（场景一 ≈ 41×）
    disp = hist.astype(float)  # 显示用原始直方（对数坐标下已足够平滑）
    ymax = math.log10(1 + disp[1:dmax + 1].max())

    def px(i):
        return X0 + (X1 - X0) * i / dmax

    def py(v):
        return Y1 - (Y1 - Y0) * math.log10(1 + v) / ymax

    pts = [(px(i), py(disp[i])) for i in range(1, dmax + 1)]

    s = SVG(800, 700)
    s.text(700, 62, "对数示意", 30, GRAY, "end")

    # 坐标轴（不标实测刻度）
    s.line(X0, Y0, X0, Y1, INK, 3)
    s.line(X0, Y1, X1 + 10, Y1, INK, 3)

    # 主峰右侧曲线下面积（绿，淡纹）
    area = [(px(4), Y1)] + [(px(i), py(disp[i])) for i in range(4, dmax + 1)] \
        + [(px(dmax), Y1)]
    s.polygon(area, GREEN_TINT)

    # 错误尾（深度 1–3）红色淡底 + 斜纹（裁剪到曲线下）
    err = [(px(1), Y1), (px(1), py(disp[1])), (px(2), py(disp[2])),
           (px(3), py(disp[3])), (px(4), py(disp[4])), (px(4), Y1)]
    s.polygon(err, RED_TINT)
    cid = s.clip("errtail", err)
    s.raw(f'<g clip-path="{cid}">')
    x = px(1) - 40
    while x < px(4) + 40:
        s.line(x, Y1 + 20, x + 90, Y0 - 40, RED, 3)
        x += 22
    s.raw("</g>")

    # 频谱曲线（深蓝）
    s.curve(pts, BLUE, 6)

    # i_min=4 红色剔除虚线（红色处 2：斜纹区 + 本线）
    s.line(px(4), Y0, px(4), Y1, RED, 5, dash="14 10")
    s.text(px(4) + 12, Y0 + 34, "错误尾 i<4：剔除", 30, RED, "start", "bold")

    # 主峰标注
    pk = (px(peak), py(disp[peak]))
    s.circle(pk[0], pk[1], 9, BLUE)
    s.text(pk[0] + 6, pk[1] - 20, "主峰 19×", 32, BLUE, "start", "bold")

    # 底部算式条（三列等距，互不重叠）
    s.rect(60, 540, 680, 84, WHITE, PANEL, 3, rx=12)
    s.text(100, 594, "G ≈ 面积÷19", 34, INK, "start", "bold")
    s.text(335, 594, "= 40,976 bp", 34, BLUE, "start", "bold")
    s.text(560, 594, "偏差 2.4%", 32, GRAY, "start", "bold")


    s.save("06_genome_size_area.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

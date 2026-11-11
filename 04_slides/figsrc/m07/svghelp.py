#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""svghelp.py — M07 幻灯片配图脚本的共享 SVG 写出辅助（多彩生物教学配色）

约束来源
--------
* 配色与字体栈：`.scratch/illustrations/spec.md` §2（多彩生物教学版）
* 画布与文字：`04_slides/README.md`「幻灯片插图（D125）」＋ `M07_FIGP_001.md` §4
  —— `.cols` 一栏 `viewBox="0 0 800 700"`；字号 ≥ 30；图内汉字 ≤ 30；红 `#E64B35`
  只作唯一警示色（每图 ≤ 2 处）；图内不写出处标签、不写整句英文（D134/D135）。
* 版心：主题 `.cols img` 最高 400px，故画布 800×700 按宽度缩放到 ~457×400，
  即 1 个 viewBox 单位 ≈ 0.57 屏幕像素；字号 30 ≈ 17px 屏幕字，仍可读。

`save()` 阶段逐条审计：① 文字框越出画布 ② 任意两段文字重叠 ③ 汉字总数
④ 最小字号 ⑤ 红色用量，前三项不过就抛 SaveError，不允许把出画布/压字的图落盘。

`python3 svghelp.py --audit ../../master/imgs/07_metagenome/*.svg`
可对已落盘的 SVG 做同一套审计（不需要重跑生成脚本）。
"""
from __future__ import annotations

import html
import math
import re
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]                # NGS_3Levels/
OUT = ROOT / "04_slides" / "master" / "imgs" / "07_metagenome"

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
CYAN_DEEP = "#3C8DAD"
ORANGE_DEEP = "#C0623F"
GREEN_TINT = "#D8EEE9"
RED_TINT = "#F6D8D2"
BLUE_TINT = "#E3E8F2"
ORANGE_TINT = "#FBE3D8"
PURPLE_TINT = "#E6E9F0"
CYAN_TINT = "#D6EFF4"

# ---- 字体度量（Noto Sans CJK SC = ttc 内 index 2）----
_FONT_TTC = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
_HAN = re.compile(r"[\u4e00-\u9fff]")

ASCENT, DESCENT = 0.88, 0.24          # 相对 font-size 的上下伸出量（CJK 字体实测）


@lru_cache(maxsize=64)
def _pil_font(size: int):
    try:
        from PIL import ImageFont
    except Exception:                  # 没有 PIL 时退化为启发式
        return None
    for idx in (2, 0):
        try:
            return ImageFont.truetype(_FONT_TTC, size, index=idx)
        except Exception:
            continue
    return None


@lru_cache(maxsize=8192)
def text_width(s: str, size: int, bold: bool = False) -> float:
    """文字外框宽度（viewBox 单位）。真字体度量，粗体加 4% 余量。"""
    f = _pil_font(size)
    if f is not None:
        w = float(f.getlength(s))
    else:                              # 兜底：汉字 1.0×size、ASCII 0.56×size
        w = sum(size if _HAN.match(ch) else 0.56 * size for ch in s)
    if bold:
        w = w * 1.04 + 1.0
    return w


def han_count(s: str) -> int:
    return len(_HAN.findall(s))


_BREAK = "、，：；（）·"


def wrap(s: str, size: int, max_w: float, bold: bool = False) -> list[str]:
    """按真实字宽把一句中文拆成不超过 max_w 的行；断点优先落在标点后。"""
    lines, cur = [], ""
    for ch in s:
        cand = cur + ch
        if text_width(cand, size, bold) > max_w and cur:
            if ch in _BREAK:
                lines.append(cand)
                cur = ""
                continue
            cut = max(cur.rfind(c) for c in _BREAK if c in cur) if any(
                c in cur for c in _BREAK) else -1
            if cut >= 0 and cut >= len(cur) // 3:
                lines.append(cur[:cut + 1])
                cur = cur[cut + 1:] + ch
            else:
                lines.append(cur)
                cur = ch
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines


class SaveError(RuntimeError):
    pass


class SVG:
    def __init__(self, w=800, h=700, han_limit=30, red_limit=2):
        self.w, self.h = w, h
        self.parts: list[str] = []
        self.defs: list[str] = []
        self.texts: list[dict] = []     # 审计用：逐条文字外框
        self.han_limit = han_limit
        self.red_limit = red_limit

    # ---------------- 基础图元 ----------------
    def raw(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill="none", stroke=None, sw=4, rx=0, dash=None):
        a = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"'
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
             f'stroke-width="{sw}" stroke-linejoin="round" '
             f'stroke-linecap="round"')
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

    def ellipse(self, cx, cy, rx, ry, fill="none", stroke=None, sw=4):
        a = f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        self.raw(a + "/>")

    def cross(self, cx, cy, r, color, sw=8):
        """警示叉：两笔对角线（用于「不可行」「不通过」）。"""
        self.line(cx - r, cy - r, cx + r, cy + r, color, sw, cap="round")
        self.line(cx + r, cy - r, cx - r, cy + r, color, sw, cap="round")

    # ---------------- 文字 ----------------
    def text(self, x, y, s, size=32, fill=INK, anchor="start", weight=None):
        a = (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
             f'fill="{fill}" text-anchor="{anchor}"')
        if weight:
            a += f' font-weight="{weight}"'
        self.raw(a + f">{html.escape(s)}</text>")
        w = text_width(s, size, bool(weight))
        x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
        self.texts.append({
            "s": s, "size": size, "fill": fill, "weight": weight,
            "x0": x0, "x1": x0 + w,
            "y0": y - ASCENT * size, "y1": y + DESCENT * size,
        })

    def label(self, x, y, lines, size=32, fill=INK, anchor="middle",
              weight=None, leading=1.35):
        """多行文字块（垂直以 y 为块中心）。lines 可含 (文本, 颜色) 二元组。"""
        n = len(lines)
        h = size * leading
        y0 = y - (n - 1) * h / 2
        for i, ln in enumerate(lines):
            s, c = ln if isinstance(ln, tuple) else (ln, fill)
            self.text(x, y0 + i * h + size * 0.35, s, size, c, anchor, weight)

    # ---------------- 版面构件 ----------------
    def title(self, s, y=64, size=36, fill=BLUE):
        self.text(self.w / 2, y, s, size, fill, "middle", "bold")

    def subtitle(self, s, y=110, size=30, fill=GRAY):
        self.text(self.w / 2, y, s, size, fill, "middle")

    def bottom(self, lines, y=626, gap=52, size=32):
        """底部 takeaway：最多两行，第一行深蓝/第二行可指定颜色。"""
        for i, ln in enumerate(lines):
            s, c, w = (ln if isinstance(ln, tuple) else (ln, INK, None))
            self.text(self.w / 2, y + i * gap, s, size, c, "middle", w)

    def panel(self, x, y, w, h, caption=None, cap_size=30,
              fill=WHITE, stroke=PANEL, cap_fill=GRAY, cap_y=None):
        """白底圆角面板；caption 居中写在下沿之上（默认贴面板顶部内边）。"""
        self.rect(x, y, w, h, fill, stroke, 3, rx=14)
        if caption:
            self.text(x + w / 2, cap_y if cap_y is not None else y + 44,
                      caption, cap_size, cap_fill, "middle", "bold")
        return (x, y, w, h)

    def chip(self, cx, cy, s, size=30, fill=WHITE, stroke=None, ink=None,
             padx=16, pady=11, sw=3, rx=10, bold=True):
        """胶囊标签：底色块 + 居中文字（fill 与文字色可分离）。"""
        w = text_width(s, size, bold) + 2 * padx
        h = size * (ASCENT + DESCENT) + 2 * pady
        self.rect(cx - w / 2, cy - h / 2, w, h, fill, stroke, sw, rx=rx)
        self.text(cx, cy + size * 0.32, s, size, ink or INK, "middle",
                  "bold" if bold else None)
        return (cx - w / 2, cy - h / 2, w, h)

    def badge(self, cx, cy, s, size=34, fill=RED, box=WHITE, padx=18, pady=12):
        """数字/结论徽标：底色块 + 居中粗体文字。"""
        w = text_width(s, size, True) + 2 * padx
        h = size * (ASCENT + DESCENT) + 2 * pady
        self.rect(cx - w / 2, cy - h / 2, w, h, box, fill, 4, rx=10)
        self.text(cx, cy + size * 0.33, s, size, fill, "middle", "bold")

    def arrow(self, x1, y1, x2, y2, color, sw=6, head=18):
        ang = math.atan2(y2 - y1, x2 - x1)
        self.line(x1, y1, x2, y2, color, sw, cap="round")
        self.polygon([
            (x2, y2),
            (x2 - head * math.cos(ang - 0.42), y2 - head * math.sin(ang - 0.42)),
            (x2 - head * math.cos(ang + 0.42), y2 - head * math.sin(ang + 0.42)),
        ], color)

    def curve(self, pts, color, sw=5, dash=None):
        """Catmull-Rom 平滑曲线（数据点较多时的频谱/剖面形态）。"""
        if len(pts) < 3:
            self.polyline(pts, color, sw, dash=dash)
            return
        d = f"M {pts[0][0]} {pts[0][1]}"
        n = len(pts)
        for i in range(n - 1):
            p0, p1, p2, p3 = (pts[max(i - 1, 0)], pts[i], pts[i + 1],
                              pts[min(i + 2, n - 1)])
            c1 = p1 if i == 0 else (p1[0] + (p2[0] - p0[0]) / 6,
                                    p1[1] + (p2[1] - p0[1]) / 6)
            c2 = p2 if i == n - 2 else (p2[0] - (p3[0] - p1[0]) / 6,
                                        p2[1] - (p3[1] - p1[1]) / 6)
            d += (f" C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} "
                  f"{p2[0]} {p2[1]}")
        self.path(d, color, sw, dash=dash)

    def star(self, cx, cy, r, fill, stroke=None, sw=4, points=5):
        pts = []
        for i in range(2 * points):
            rr = r if i % 2 == 0 else r * 0.42
            a = -math.pi / 2 + i * math.pi / points
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        self.polygon(pts, fill, stroke, sw)

    # ---------------- 数据图构件 ----------------
    def axes(self, l, b, r, t, xlab=None, ylab=None, ylab_at=None,
             ticks=None, tick_len=8):
        """直角坐标框：左/下实线，可选刻度（[(pos, 文本, 轴)]）。"""
        self.line(l, b, r, b, INK, 4)
        self.line(l, b, l, t, INK, 4)
        if xlab:
            self.text(r + 6, b + 10, xlab, 30, GRAY, "start")
        if ylab:
            x, y = (ylab_at if ylab_at else (l - 12, t - 4))
            self.text(x, y, ylab, 30, GRAY, "end" if not ylab_at else "start")
        for pos, s_, ax in (ticks or []):
            if ax == "x":
                self.line(pos, b, pos, b + tick_len, INK, 3)
                self.text(pos, b + 34, s_, 30, GRAY, "middle")
            else:
                self.line(l, pos, l - tick_len, pos, INK, 3)
                self.text(l - 14, pos + 10, s_, 30, GRAY, "end")

    def bar(self, x, b, w, v, color, label=None, sub=None, cap=30,
            label_fill=INK, sub_fill=GRAY, rx=6, gap_up=16, gap_dn=38):
        """竖直条形；v 为像素高度。label 写在条顶，sub 写在基线下。"""
        self.rect(x, b - v, w, v, color, rx=rx)
        if label:
            self.text(x + w / 2, b - v - gap_up, label, cap, label_fill,
                      "middle", "bold")
        if sub:
            self.text(x + w / 2, b + gap_dn, sub, 30, sub_fill, "middle")

    def hbar(self, x, y, w, h, frac, color, track=None):
        """横向进度条：w 为满格宽，frac ∈ [0,1]。"""
        if track:
            self.rect(x, y, w, h, track, rx=h // 2)
        if frac > 0:
            self.rect(x, y, max(w * frac, 4), h, color, rx=h // 2)

    def clip(self, cid, pts):
        p = " ".join(f"{x},{y}" for x, y in pts)
        self.defs.append(f'<clipPath id="{cid}"><polygon points="{p}"/></clipPath>')
        return f"url(#{cid})"

    # ---------------- 审计与落盘 ----------------
    def audit(self, canvas=True, overlap=True, han=True, font=True):
        probs = []
        W, H = self.w, self.h
        for t in self.texts:
            if canvas and (t["x0"] < 0 or t["x1"] > W or t["y0"] < 0
                           or t["y1"] > H):
                probs.append(
                    f"出画布：{t['s']!r} x=[{t['x0']:.1f},{t['x1']:.1f}] "
                    f"y=[{t['y0']:.1f},{t['y1']:.1f}]（画布 {W}×{H}）")
            if font and t["size"] < 30:
                probs.append(f"字号不足 30：{t['s']!r} = {t['size']}")
        if han:
            total = sum(han_count(t["s"]) for t in self.texts)
            if total > self.han_limit:
                probs.append(f"图内汉字 {total} > {self.han_limit}")
        if overlap:
            n = len(self.texts)
            for i in range(n):
                for j in range(i + 1, n):
                    a, b = self.texts[i], self.texts[j]
                    ow = min(a["x1"], b["x1"]) - max(a["x0"], b["x0"])
                    oh = min(a["y1"], b["y1"]) - max(a["y0"], b["y0"])
                    if ow > 3 and oh > 3:
                        probs.append(f"文字重叠：{a['s']!r} × {b['s']!r} "
                                     f"重叠 {ow:.0f}×{oh:.0f}px")
        # 红色统计：红是一个「警示语义组」（弧线+箭头+标签算一处），故只统计不设硬门槛，
        # 逐图在回执里人工判读（spec §2「每图 ≤ 1–2 处」）。
        reds = sum(1 for p in self.parts if RED in p)
        return probs, reds

    def save(self, name, verbose=True):
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        doc = (f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {self.w} {self.h}">\n'
               f'<rect width="{self.w}" height="{self.h}" fill="{PAPER}"/>\n'
               + defs + "\n" + "\n".join(self.parts) + "\n</svg>\n")
        probs, reds = self.audit()
        if probs:
            raise SaveError("；".join(probs))
        out = OUT / name
        OUT.mkdir(parents=True, exist_ok=True)
        out.write_text(doc, encoding="utf-8")
        if verbose:
            han = sum(han_count(t["s"]) for t in self.texts)
            print(f"wrote {out}  [{len(self.texts)} 条文字 / {han} 汉字 / 红 {reds} 处]")
        return reds


# ---------------- 对已落盘 SVG 的独立审计 ----------------
def audit_file(path: Path, han_limit=30):
    import xml.etree.ElementTree as ET
    ns = "{http://www.w3.org/2000/svg}"
    root = ET.parse(path).getroot()
    vb = root.get("viewBox", "0 0 800 700").split()
    W, H = float(vb[2]), float(vb[3])
    probs, boxes, sizes = [], [], []
    for el in root.iter(ns + "text"):
        s = "".join(el.itertext())
        size = float(el.get("font-size", 32))
        sizes.append(size)
        anchor = el.get("text-anchor", "start")
        bold = el.get("font-weight") in ("bold", "600", "700")
        try:
            x, y = float(el.get("x")), float(el.get("y"))
        except (TypeError, ValueError):
            probs.append(f"坐标非数字：{s!r}")
            continue
        w = text_width(s, int(size), bold)
        x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
        boxes.append((s, x0, x0 + w, y - ASCENT * size, y + DESCENT * size))
    for s, x0, x1, y0, y1 in boxes:
        if x0 < 0 or x1 > W or y0 < 0 or y1 > H:
            probs.append(f"出画布：{s!r} x=[{x0:.0f},{x1:.0f}] y=[{y0:.0f},{y1:.0f}]")
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            ow = min(a[2], b[2]) - max(a[1], b[1])
            oh = min(a[4], b[4]) - max(a[3], b[3])
            if ow > 3 and oh > 3:
                probs.append(f"文字重叠：{a[0]!r} × {b[0]!r} {ow:.0f}×{oh:.0f}px")
    han = sum(han_count(t[0]) for t in boxes)
    if han > han_limit:
        probs.append(f"图内汉字 {han} > {han_limit}")
    if sizes and min(sizes) < 30:
        probs.append(f"最小字号 {min(sizes)} < 30")
    if (W, H) != (800.0, 700.0):
        probs.append(f"画布 {W}×{H} 非 800×700")
    raw = path.read_text(encoding="utf-8")
    for bad in ("demo:", "--selftest", "schematic", "textbook §"):
        if bad in raw:
            probs.append(f"图内出处标签：{bad}")
    return probs, {"n": len(boxes), "han": han, "min_size": min(sizes) if sizes else 0,
                   "reds": sum(1 for line in raw.splitlines() if RED in line)}


def main(argv):
    if len(argv) < 2 or argv[1] != "--audit":
        print(__doc__)
        return 0
    paths = []
    for pat in argv[2:]:
        p = Path(pat)
        paths.extend(sorted(p.parent.glob(p.name)) if "*" in pat else [p])
    bad = 0
    for f in paths:
        probs, stat = audit_file(f)
        flag = "OK  " if not probs else "FAIL"
        print(f"{flag} {f.name:44s} 文字{stat['n']:3d} 汉字{stat['han']:3d} "
              f"最小字号{stat['min_size']:.0f} 红{stat['reds']}")
        for x in probs:
            bad += 1
            print("      -", x)
    print(f"\n共 {len(paths)} 张，问题 {bad} 条")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

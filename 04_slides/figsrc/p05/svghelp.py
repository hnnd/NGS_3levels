#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""svghelp.py — P05 幻灯片配图脚本的共享 SVG 写出辅助（多彩生物教学配色）

配色与字体栈：`.scratch/illustrations/spec.md` §2；画布约定：`04_slides/README.md`
「幻灯片插图（D125）」＋ `reviews/course/P05_FIGP_001.md` §1／§4
（cols 一栏 viewBox 800×700；字号 ≥ 30 viewBox 单位；图内文字一律中文且
总汉字 ≤ 30；红 #E64B35 每图 ≤ 2 处）。

各 <NN>_<概念>.py 用

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from svghelp import *

引入。save() 前做四项近似自检（只用标准库，不依赖第三方字体库）：
① 任何 <text> 的估计外框不得出画布；② 任意两段 <text> 的估计外框不得重叠
（交叠 > 4 px 才算）；③ 图内汉字总数 ≤ 30；④ 用到的汉字必须都来自方案
给定的整句（multiset 比对，防止自造文案）。
近似字宽按等宽 CJK + 拉丁比例估计，保守取宽，宁可多报不可漏报；真实渲染由
`textbook/tasks/logs/P05_FIGS_png/` 的 PNG 目检兜底。

文字压轴线／压卡片边框的盲区由 tasks/logs/audit_p05_overlap.py 单独查。
"""
import html
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]        # NGS_3Levels/
OUT = ROOT / "04_slides" / "phd" / "imgs" / "05_gwas"
OUT.mkdir(parents=True, exist_ok=True)

FONT = "Noto Sans CJK SC, PingFang SC, sans-serif"
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
GREEN_TINT = "#D8EEE9"
RED_TINT = "#F6D8D2"
BLUE_TINT = "#E3E8F2"
ORANGE_TINT = "#FBE6DF"
PURPLE_TINT = "#E7EAF1"
CYAN_TINT = "#E7F5F8"

CJK_MIN = 0x2E80


def _chw(ch, size, bold):
    if ch == " ":
        w = 0.30
    elif ord(ch) >= CJK_MIN:
        w = 1.00
    elif ch in "().,:;'\"":
        w = 0.34
    elif ch.isdigit():
        w = 0.56
    elif ch.isupper():
        w = 0.64
    elif ch.islower():
        w = 0.52
    else:
        w = 0.62
    return w * size * (1.04 if bold else 1.0)


def tw(s, size=30, bold=False):
    """估计文本宽度（viewBox 单位），保守取宽。"""
    return sum(_chw(c, size, bold) for c in s)


class SVG:
    def __init__(self, w=800, h=700, title="", plan=""):
        self.w, self.h = w, h
        self.title = title
        self.plan = plan          # 方案给定的图内全部中文（汉字须全部来自它）
        self.parts = []
        self.defs = []
        self._texts = []          # (x0, y0, x1, y1, s)

    # ---------- 基本图元 ----------
    def raw(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill="none", stroke=None, sw=4, rx=0,
             dash=None, opacity=None):
        a = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"'
        if rx:
            a += f' rx="{rx}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            a += f' fill-opacity="{opacity}"'
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

    def polygon(self, pts, fill, stroke=None, sw=4, dash=None):
        p = " ".join(f"{x},{y}" for x, y in pts)
        a = f'<polygon points="{p}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
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

    def wedge(self, x, ytop, wtop, wbot, h, fill, stroke=None, sw=4):
        """梯形（漏斗／金字塔层）：上边居中宽 wtop、下边居中宽 wbot。"""
        cx = x
        self.polygon([(cx - wtop / 2, ytop), (cx + wtop / 2, ytop),
                      (cx + wbot / 2, ytop + h), (cx - wbot / 2, ytop + h)],
                     fill, stroke, sw)

    def curve(self, pts, color, sw=5, dash=None):
        """Catmull-Rom 平滑曲线（数据点较多时用）。"""
        if len(pts) < 3:
            self.polyline(pts, color, sw, dash=dash)
            return
        d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
        n = len(pts)
        for i in range(n - 1):
            p0 = pts[max(i - 1, 0)]
            p1 = pts[i]
            p2 = pts[i + 1]
            p3 = pts[min(i + 2, n - 1)]
            c1 = p1 if i == 0 else (p1[0] + (p2[0] - p0[0]) / 6,
                                    p1[1] + (p2[1] - p0[1]) / 6)
            c2 = p2 if i == n - 2 else (p2[0] - (p3[0] - p1[0]) / 6,
                                        p2[1] - (p3[1] - p1[1]) / 6)
            d += (f" C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} "
                  f"{p2[0]:.1f} {p2[1]:.1f}")
        self.path(d, color, sw, dash=dash)

    def clip(self, cid, pts):
        p = " ".join(f"{x},{y}" for x, y in pts)
        self.defs.append(
            f'<clipPath id="{cid}"><polygon points="{p}"/></clipPath>')
        return f"url(#{cid})"

    def hatch(self, hid, color, angle=45, gap=10, sw=3):
        """斜纹图案（禁用／异常区底纹）；返回 fill url。"""
        self.defs.append(
            f'<pattern id="{hid}" width="{gap}" height="{gap}" '
            f'patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate({angle})">'
            f'<line x1="0" y1="0" x2="0" y2="{gap}" stroke="{color}" '
            f'stroke-width="{sw}"/></pattern>')
        return f"url(#{hid})"

    # ---------- 文字 ----------
    def _register(self, x, y, wdt, size, s):
        x0 = x
        box = (x0, y - 0.80 * size, x0 + wdt, y + 0.24 * size, s)
        self._texts.append(box)
        return box

    def text(self, x, y, s, size=30, fill=INK, anchor="start", weight=None):
        if size < 30:
            raise SystemExit(f"[{self.title}] 字号 {size} < 30：{s!r}")
        bold = weight == "bold"
        wdt = tw(s, size, bold)
        x0 = x - (0 if anchor == "start" else wdt / 2 if anchor == "middle"
                  else wdt)
        self._register(x0, y, wdt, size, s)
        a = (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
             f'fill="{fill}" text-anchor="{anchor}"')
        if weight:
            a += f' font-weight="{weight}"'
        self.raw(a + f">{html.escape(s)}</text>")

    def seg(self, x, y, parts, size=30, anchor="start", weight=None):
        """同一行内多段不同颜色的文字（如「…但压缩方差」把末词标红）。

        parts = [(文字, 颜色), ...]；返回整行宽度（viewBox 单位）。
        """
        full = "".join(p[0] for p in parts)
        bold = weight == "bold"
        wdt = tw(full, size, bold)
        x0 = x - (0 if anchor == "start" else wdt / 2 if anchor == "middle"
                  else wdt)
        self._register(x0, y, wdt, size, full)
        out = []
        cur = x0
        for s, col in parts:
            out.append(f'<tspan x="{cur:.1f}" fill="{col}">{html.escape(s)}'
                       f'</tspan>')
            cur += tw(s, size, bold)
        a = (f'<text y="{y}" font-family="{FONT}" font-size="{size}" '
             f'text-anchor="start"')
        if weight:
            a += f' font-weight="{weight}"'
        self.raw(a + ">" + "".join(out) + "</text>")
        return wdt

    def sci(self, x, y, base, sup, size=32, fill=INK, anchor="start",
            weight=None):
        """带上标的文字（如 1×10⁻⁷）：上标用 tspan 的 dy 抬升，不用 Unicode
        上标字符（本机字体缺 ⁷/⁹ 字形，直写会渲染成方块），也不用
        baseline-shift（cairosvg 忽略它，渲染出来与正文同基线）。
        实测注意：tspan 同时带 x 与 dy 时 cairosvg 会丢掉上标的首字符
        （负号消失，`5×10⁻⁸` 渲染成 `5×10⁸`）；因此这里只给 tspan 设 dy，
        父 text 用 text-anchor=start 且 x 取已算好的左端，三个 anchor 都安全。"""
        sup_size = int(size * 0.72)
        bold = weight == "bold"
        wb = tw(base, size, bold)
        wdt = wb + tw(sup, sup_size, bold)
        x0 = x - (0 if anchor == "start" else wdt / 2 if anchor == "middle"
                  else wdt)
        self._register(x0, y - size * 0.36, wdt, size, base + sup)
        a = (f'<text x="{x0:.1f}" y="{y}" font-family="{FONT}" '
             f'font-size="{size}" fill="{fill}" text-anchor="start"')
        if weight:
            a += f' font-weight="{weight}"'
        self.raw(a + f'>{html.escape(base)}<tspan dy="-{size * 0.36:.0f}" '
                 f'font-size="{sup_size}">{html.escape(sup)}</tspan></text>')

    def chip(self, x, cy, s, size=30, fill=WHITE, stroke=BLUE, tc=INK,
             pad=18, h=None, anchor="start", sw=4, dash=None):
        """圆角标签：x 为左边界（anchor=start）或中心（anchor=middle）。"""
        h = h or size + 26
        wdt = tw(s, size, False) + 2 * pad
        left = x if anchor == "start" else (x - wdt / 2 if anchor == "middle"
                                            else x - wdt)
        self.rect(left, cy - h / 2, wdt, h, fill, stroke, sw, rx=h / 2,
                  dash=dash)
        self.text(left + wdt / 2, cy + size * 0.35, s, size, tc, "middle")
        return wdt

    def badge(self, x, cy, s, fill, tc=WHITE, size=30, anchor="start", sw=4):
        h = size + 30
        wdt = tw(s, size, True) + 30
        left = x if anchor == "start" else x - wdt / 2
        self.rect(left, cy - h / 2, wdt, h, fill, None, sw, rx=8)
        self.text(left + wdt / 2, cy + size * 0.35, s, size, tc, "middle",
                  "bold")
        return wdt

    # ---------- 组合件 ----------
    def arrow(self, x1, y1, x2, y2, color, sw=6, head=16, dash=None):
        ang = math.atan2(y2 - y1, x2 - x1)
        self.line(x1, y1, x2, y2, color, sw, dash, cap="round")
        self.polygon([
            (x2, y2),
            (x2 - head * math.cos(ang - 0.42),
             y2 - head * math.sin(ang - 0.42)),
            (x2 - head * math.cos(ang + 0.42),
             y2 - head * math.sin(ang + 0.42)),
        ], color)

    def darrow(self, x1, y1, x2, y2, color, sw=5, head=14):
        """双向箭头（跨度标注）。"""
        self.arrow(x1, y1, x2, y2, color, sw, head)
        ang = math.atan2(y1 - y2, x1 - x2)
        self.polygon([
            (x1, y1),
            (x1 - head * math.cos(ang - 0.42),
             y1 - head * math.sin(ang - 0.42)),
            (x1 - head * math.cos(ang + 0.42),
             y1 - head * math.sin(ang + 0.42)),
        ], color)

    def check(self, cx, cy, r, color=GREEN, sw=8):
        self.polyline([(cx - 0.62 * r, cy + 0.02 * r),
                       (cx - 0.12 * r, cy + 0.50 * r),
                       (cx + 0.66 * r, cy - 0.46 * r)], color, sw)

    def cross(self, cx, cy, r, color=RED, sw=9):
        self.line(cx - r, cy - r, cx + r, cy + r, color, sw, cap="round")
        self.line(cx - r, cy + r, cx + r, cy - r, color, sw, cap="round")

    def lock(self, cx, cy, r=26, color=RED):
        """挂锁图标：锁体 + 锁梁（关闭状态的过滤器）。"""
        self.rect(cx - 0.80 * r, cy - 0.10 * r, 1.60 * r, 1.20 * r, color,
                  None, 0, rx=6)
        self.path(f"M {cx - 0.48 * r} {cy - 0.10 * r} "
                  f"L {cx - 0.48 * r} {cy - 0.62 * r} "
                  f"Q {cx} {cy - 1.10 * r} {cx + 0.48 * r} {cy - 0.62 * r} "
                  f"L {cx + 0.48 * r} {cy - 0.10 * r}",
                  color, max(5, r * 0.22), fill="none")

    def stamp(self, cx, cy, w, h, s, color=RED, tc=RED, size=30, dash="10 7"):
        """印章：双线框 + 居中文字（与 chip 同一文字坐标系）。"""
        self.rect(cx - w / 2, cy - h / 2, w, h, WHITE, color, 4, rx=10,
                  dash=dash)
        self.rect(cx - w / 2 + 7, cy - h / 2 + 7, w - 14, h - 14, "none",
                  color, 2, rx=7)
        self.text(cx, cy + size * 0.35, s, size, tc, "middle", "bold")

    def band(self, x, y, w, h, s, fill=BLUE, tc=WHITE, size=30, rx=12,
             stroke=None, sw=4):
        """整条横幅：色底 + 居中一行文字。"""
        self.rect(x, y, w, h, fill, stroke, sw, rx=rx)
        self.text(x + w / 2, y + h / 2 + size * 0.35, s, size, tc, "middle",
                  "bold")

    def caption(self, lines, colors=None, size=30, wbox=None, pad_top=24,
                gap=44, top=None):
        """底部结论条：白底 + 居中逐行文字（≤ 3 行）。"""
        n = len(lines)
        hbox = pad_top + n * gap + 12
        t = top if top is not None else self.h - 22 - hbox
        wbox = wbox or (self.w - 64)
        self.rect((self.w - wbox) / 2, t, wbox, hbox, WHITE, PANEL, 3, rx=14)
        for i, line in enumerate(lines):
            col = INK if not colors else colors[i]
            self.text(self.w / 2, t + pad_top + 26 + i * gap, line, size, col,
                      "middle")
        return t

    def card(self, x, y, w, h, stroke, tint, head, lines=(), size=34,
             tsize=30, gap=46, pad=22):
        """标准卡片：粗描边 + 淡底 + 标题行（色）+ 若干内容行（正文色）。"""
        self.rect(x, y, w, h, tint, stroke, 4, rx=12)
        self.text(x + pad, y + size + 14, head, size, stroke, "start", "bold")
        for i, ln in enumerate(lines):
            self.text(x + pad, y + size + 14 + gap + i * gap, ln, tsize, INK)

    def panel(self, x, y, w, h, tint, stroke=None, sw=3, rx=14, dash=None,
              fill_first=True):
        self.rect(x, y, w, h, tint if fill_first else "none", stroke, sw,
                  rx=rx, dash=dash)

    def axis(self, x0, y0, x1, y1, color=BLUE, sw=5):
        """带箭头的坐标轴（x 轴水平、y 轴垂直）。"""
        self.arrow(x0, y0, x1, y0, color, sw, 14)
        self.arrow(x0, y0, x0, y1, color, sw, 14)

    def dot(self, cx, cy, r=10, fill=BLUE, stroke=None):
        self.circle(cx, cy, r, fill, stroke, 3)

    # ---------- 落盘与自检 ----------
    def cjk(self):
        return sum(len(re.findall(r"[\u4e00-\u9fff]", b[4]))
                   for b in self._texts)

    def validate(self):
        bad = []
        n = self.cjk()
        if n > 30:
            bad.append(f"图内汉字 {n} > 30（方案上限）")
        if self.plan:
            from collections import Counter
            want = Counter(c for c in self.plan if "\u4e00" <= c <= "\u9fff")
            got = Counter(c for b in self._texts for c in b[4]
                          if "\u4e00" <= c <= "\u9fff")
            extra = got - want
            if extra:
                bad.append("图内出现方案句以外的汉字："
                           + "".join(extra.elements()))
        for x0, y0, x1, y1, s in self._texts:
            if x0 < -0.5 or y0 < -0.5 or x1 > self.w + 0.5 or y1 > self.h + 0.5:
                bad.append(f"出画布 {s!r} box="
                           f"{tuple(round(v, 1) for v in (x0, y0, x1, y1))}")
        names = list(self._texts)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                dx = min(a[2], b[2]) - max(a[0], b[0])
                dy = min(a[3], b[3]) - max(a[1], b[1])
                if dx > 4 and dy > 6:
                    bad.append(f"文字重叠 {a[4]!r} vs {b[4]!r} "
                               f"(dx={dx:.1f}, dy={dy:.1f})")
        if bad:
            raise SystemExit(f"[{self.title}] 自检失败：\n  "
                             + "\n  ".join(bad))

    def save(self, name):
        self.validate()
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        doc = ('<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {self.w} {self.h}">\n'
               f'<title>{html.escape(self.title)}</title>\n'
               f'<rect width="{self.w}" height="{self.h}" fill="{PAPER}"/>\n'
               + defs + "\n" + "\n".join(self.parts) + "\n</svg>\n")
        (OUT / name).write_text(doc, encoding="utf-8")
        print(f"wrote {OUT / name}  (CJK {self.cjk()})")

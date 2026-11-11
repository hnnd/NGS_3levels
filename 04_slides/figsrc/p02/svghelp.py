#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""svghelp.py — P02 幻灯片配图脚本的共享 SVG 写出辅助（多彩生物教学配色）

配色与字体栈：.scratch/illustrations/spec.md §2；画布与文字约定：
reviews/course/P02_FIGP_001.md §4「统一绘图技术约定」（cols 一栏 viewBox 800×700；
字号 ≥ 30 viewBox 单位；`<text>` 不转路径）。各 `<NN>_<概念>.py` 用

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from svghelp import *

引入。save() 前做三项近似自检（只用标准库，不依赖任何字体库）：

① 图内汉字总数 ≤ `cjk_max`（默认 30），且每个汉字都来自方案指定的整句
   或该图登记的中文译标签（`extra`）——两者合起来构成该图的汉字白名单；
② 任何 `<text>` 的估计外框不得出画布；
③ 任意两段 `<text>` 的估计外框不得重叠（交叠 > 4×6 px 才算）。

说明性英文标签一律译成中文（COURSE_SYNC §7 第 10 条 / D135：图内英文说明占比 ≤6%，
只留工具名与字段名）。需要中文译标签的图把译标签的汉字写进 `extra`、把实测汉字总数
写进 `cjk_max`，两处都在脚本顶层显式声明，便于审计复算。

估计字宽按等宽 CJK + 拉丁比例取宽（宁可多报不可漏报），真实渲染由
textbook/tasks/logs/P02_FIGS_png/ 的 PNG 目检兜底。

配色语义（spec §2，每图红 ≤ 2 处）：
深蓝 #3C5488 结构 / 青蓝 #4DBBD5 数据流 / 绿 #00A087 正常达标 /
橙 #F39B7F 与紫 #8491B4 辅助对比 / 红 #E64B35 唯一警示色。
"""
import html
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]        # NGS_3Levels/
OUT = ROOT / "04_slides" / "phd" / "imgs" / "02_scrnaseq_spatial"
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
    def __init__(self, w=800, h=700, title="", plan="", extra="", cjk_max=None):
        self.w, self.h = w, h
        self.title = title
        self.plan = plan          # 方案指定的图内整句（汉字须全部来自它）
        self.extra = extra        # 方案整句外来字：该图元素标签的中文译文（白名单）
        if cjk_max is None:       # 默认预算 = 白名单（整句 + 译标签）的汉字总数
            import re
            cjk_max = len(re.findall(r"[\u4e00-\u9fff]", plan + extra))
        self.cjk_max = cjk_max    # 该图声明的汉字预算
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

    def polygon(self, pts, fill, stroke=None, sw=4, dash=None, opacity=None):
        p = " ".join(f"{x},{y}" for x, y in pts)
        a = f'<polygon points="{p}" fill="{fill}"'
        if opacity is not None:
            a += f' fill-opacity="{opacity}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{sw}"'
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

    # ---------- 文字 ----------
    def text(self, x, y, s, size=30, fill=INK, anchor="start", weight=None,
             bg=False):
        if size < 30:
            raise SystemExit(f"[{self.title}] 字号 {size} < 30：{s!r}")
        bold = weight == "bold"
        wdt = tw(s, size, bold)
        x0 = x - (0 if anchor == "start" else wdt / 2 if anchor == "middle" else wdt)
        box = (x0, y - 0.80 * size, x0 + wdt, y + 0.24 * size, s)
        self._texts.append(box)
        if bg:                                  # 数据标签垫纸底，避免压曲线
            self.rect(x0 - 8, box[1] - 2, wdt + 16, box[3] - box[1] + 4, PAPER)
        a = (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
             f'fill="{fill}" text-anchor="{anchor}"')
        if weight:
            a += f' font-weight="{weight}"'
        self.raw(a + f">{html.escape(s)}</text>")

    def chip(self, x, cy, s, size=30, fill=WHITE, stroke=BLUE, tc=INK,
             pad=16, h=None, anchor="start", sw=4, dash=None):
        """圆角标签：x 为左边界（anchor=start）或中心（anchor=middle）。"""
        h = h or size + 24
        wdt = tw(s, size, False) + 2 * pad
        left = x if anchor == "start" else (x - wdt / 2 if anchor == "middle"
                                            else x - wdt)
        self.rect(left, cy - h / 2, wdt, h, fill, stroke, sw, rx=10, dash=dash)
        self.text(left + wdt / 2, cy + size * 0.35, s, size, tc, "middle")
        return wdt

    def badge(self, x, cy, s, fill, tc=WHITE, size=30, anchor="start", sw=4):
        h = size + 28
        wdt = tw(s, size, True) + 28
        left = x if anchor == "start" else x - wdt / 2
        self.rect(left, cy - h / 2, wdt, h, fill, None, sw, rx=8)
        self.text(left + wdt / 2, cy + size * 0.35, s, size, tc, "middle",
                 "bold")
        return wdt

    # ---------- 组合件 ----------
    def arrow(self, x1, y1, x2, y2, color, sw=6, head=16):
        ang = math.atan2(y2 - y1, x2 - x1)
        self.line(x1, y1, x2, y2, color, sw, cap="round")
        self.polygon([
            (x2, y2),
            (x2 - head * math.cos(ang - 0.42),
             y2 - head * math.sin(ang - 0.42)),
            (x2 - head * math.cos(ang + 0.42),
             y2 - head * math.sin(ang + 0.42)),
        ], color)

    def double_arrow(self, x1, y1, x2, y2, color, sw=5, head=14):
        self.arrow(x1, y1, x2, y2, color, sw, head)
        self.arrow(x2, y2, x1, y1, color, sw, head)

    def check(self, cx, cy, r, color=GREEN, sw=8):
        self.polyline([(cx - 0.62 * r, cy + 0.02 * r),
                       (cx - 0.12 * r, cy + 0.50 * r),
                       (cx + 0.66 * r, cy - 0.46 * r)], color, sw)

    def cross(self, cx, cy, r, color=RED, sw=9):
        self.line(cx - r, cy - r, cx + r, cy + r, color, sw, cap="round")
        self.line(cx - r, cy + r, cx + r, cy - r, color, sw, cap="round")

    def bracket(self, x1, x2, y, depth=12, color=BLUE, sw=5):
        """水平大括号（向下张开）：两端 y 处引线，中点在 y+depth。"""
        xm = (x1 + x2) / 2
        self.path(f"M {x1} {y - depth} L {x1} {y} Q {x1} {y + depth} "
                  f"{x1 + 14} {y + depth} L {xm - 10} {y + depth} "
                  f"Q {xm} {y + depth} {xm} {y + 2 * depth} "
                  f"Q {xm} {y + depth} {xm + 10} {y + depth} "
                  f"L {x2 - 14} {y + depth} Q {x2} {y + depth} {x2} {y} "
                  f"L {x2} {y - depth}", color, sw, fill="none")

    def caption(self, lines, colors=None, size=30, wbox=None, pad_top=22,
                gap=46, top=None):
        """底部结论条：白底 + 居中逐行文字（≤ 3 行）。"""
        n = len(lines)
        hbox = pad_top + n * gap + 14
        t = top if top is not None else self.h - 20 - hbox
        wbox = wbox or (self.w - 56)
        self.rect((self.w - wbox) / 2, t, wbox, hbox, WHITE, PANEL, 3, rx=14)
        for i, line in enumerate(lines):
            col = INK if not colors else colors[i]
            self.text(self.w / 2, t + pad_top + 28 + i * gap, line, size, col,
                      "middle")
        return t

    def card(self, x, y, w, h, stroke, tint, head, lines=(), size=32,
             tsize=30, gap=44, pad=18):
        """标准卡片：描边 + 淡底 + 标题行（色）+ 若干内容行（正文色）。"""
        self.rect(x, y, w, h, tint, stroke, 4, rx=12)
        self.text(x + pad, y + size + 16, head, size, stroke, "start", "bold")
        for i, ln in enumerate(lines):
            self.text(x + pad, y + size + 16 + gap + i * gap, ln, tsize, INK)

    def xaxis(self, x0, x1, y, ticks=(), label=None, color=INK, size=30,
              tick=8):
        """横轴：轴线 + 刻度 + 刻度值（ticks = [(x, 文本), ...]）。"""
        self.line(x0, y, x1, y, color, 3)
        for tx, s in ticks:
            self.line(tx, y, tx, y + tick, color, 3)
            if s:
                self.text(tx, y + tick + size - 2, s, size, GRAY, "middle")
        if label:
            self.text((x0 + x1) / 2, y + tick + 2 * size + 10, label, size,
                      GRAY, "middle")

    def yaxis(self, x, y0, y1, ticks=(), size=30, tick=8, color=INK):
        """纵轴：轴线 + 刻度 + 刻度值（ticks = [(y, 文本), ...]）。"""
        self.line(x, y0, x, y1, color, 3)
        for ty, s in ticks:
            self.line(x - tick, ty, x, ty, color, 3)
            if s:
                self.text(x - tick - 8, ty + size * 0.35, s, size, GRAY, "end")

    def grid(self, x0, y0, w, h, rows, cols, color=PANEL, sw=2):
        for i in range(1, rows):
            yy = y0 + h * i / rows
            self.line(x0, yy, x0 + w, yy, color, sw)
        for j in range(1, cols):
            xx = x0 + w * j / cols
            self.line(xx, y0, xx, y0 + h, color, sw)

    def cluster(self, cx, cy, r, n, color, seed=0, rmin=3.0, rmax=6.0):
        """确定性散点团（线性同余，无随机库、无网络）。"""
        st = seed * 2654435761 % 2 ** 31 or 7
        for i in range(n):
            st = (1103515245 * st + 12345) % 2 ** 31
            a = (st / 2 ** 31) * 2 * math.pi
            st = (1103515245 * st + 12345) % 2 ** 31
            rr = r * (0.15 + 0.85 * math.sqrt(st / 2 ** 31))
            st = (1103515245 * st + 12345) % 2 ** 31
            rad = rmin + (rmax - rmin) * (st / 2 ** 31)
            self.circle(cx + rr * math.cos(a), cy + rr * math.sin(a), rad,
                        color)

    # ---------- 落盘与自检 ----------
    def cjk(self):
        import re
        return sum(len(re.findall(r"[\u4e00-\u9fff]", b[4]))
                   for b in self._texts)

    def validate(self):
        bad = []
        n = self.cjk()
        if n > self.cjk_max:
            bad.append(f"图内汉字 {n} > {self.cjk_max}（本图声明预算）")
        if self.plan:
            from collections import Counter
            allowed = {c for c in self.plan + self.extra
                       if "\u4e00" <= c <= "\u9fff"}
            got = Counter(c for b in self._texts for c in b[4]
                          if "\u4e00" <= c <= "\u9fff")
            extra = Counter({c: v for c, v in got.items() if c not in allowed})
            if extra:
                bad.append(f"图内出现白名单（方案句 + 译标签）以外的汉字："
                           f"{''.join(extra.elements())}")
        for x0, y0, x1, y1, s in self._texts:
            if x0 < -0.5 or y0 < -0.5 or x1 > self.w + 0.5 or y1 > self.h + 0.5:
                bad.append(f"出画布 {s!r} box={tuple(round(v, 1) for v in (x0, y0, x1, y1))}")
        names = [(b[0], b[1], b[2], b[3], b[4]) for b in self._texts]
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                dx = min(a[2], b[2]) - max(a[0], b[0])
                dy = min(a[3], b[3]) - max(a[1], b[1])
                if dx > 4 and dy > 6:
                    bad.append(f"文字重叠 {a[4]!r} vs {b[4]!r} (dx={dx:.1f}, dy={dy:.1f})")
        if bad:
            raise SystemExit(f"[{self.title}] 自检失败：\n  " + "\n  ".join(bad))

    def save(self, name):
        self.validate()
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        doc = (f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {self.w} {self.h}">\n'
               f'<title>{html.escape(self.title)}</title>\n'
               f'<rect width="{self.w}" height="{self.h}" fill="{PAPER}"/>\n'
               + defs + "\n" + "\n".join(self.parts) + "\n</svg>\n")
        (OUT / name).write_text(doc, encoding="utf-8")
        print(f"wrote {OUT / name}")

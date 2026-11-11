#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_enhancer_looping.py — FIG-M05-15 最近基因不等于靶基因（空间环化）

方案：`reviews/course/M05_FIGP_001.md` §4.2 FIG-M05-15（P35，`.cols` 800×700，new-svg）。
教材依据：§15.4.5 L245–L258；§15.5.3 L367–L376。
机制：增强子在三维上环化（looping）跨越距离更近的 A，激活远端的真实靶标 B；
所以「peak 的最近基因」不等于靶基因。方案原句 24 字逐字上图：
空间调控 4 / 增强子跨越临近基因远程激活 13 / 最近非真实靶标 7 = 24；
另加两处指认「增强子」3、「靶基因」3 → 合计 30 字。
红为唯一警示色：直线「就近指派」箭头 1 处 + 被误判的 A 边框 1 处 = 2 处。
纯示意，无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 15_enhancer_looping.py
"""
from svghelp import *

s = SVG()

s.text(400, 64, "空间调控", 36, BLUE, "middle", "bold")
s.text(400, 112, "增强子跨越临近基因远程激活", 30, INK, "middle")
s.text(400, 152, "最近非真实靶标", 30, INK, "middle")

DNA_Y = 512
s.line(64, DNA_Y, 736, DNA_Y, BLUE, 8, cap="round")
s.text(64, DNA_Y + 46, "DNA", 30, GRAY, "start")

# ---- 增强子（橙）----
ENH_X, ENH_W = 120, 90
s.rect(ENH_X, DNA_Y - 52, ENH_W, 104, ORANGE, "#C0623F", 4, rx=12)
s.text(ENH_X + ENH_W / 2, 632, "增强子", 30, "#C0623F", "middle", "bold")

# ---- 近端 A（红框：会被「最近基因」规则误判的对象）----
GA_X, GW = 330, 90
s.rect(GA_X, DNA_Y - 44, GW, 88, WHITE, RED, 5, rx=12)
s.text(GA_X + GW / 2, DNA_Y + 11, "A", 34, INK, "middle", "bold")

# ---- 远端 B（绿：真实靶标）----
GB_X = 640
s.rect(GB_X, DNA_Y - 44, GW, 88, WHITE, GREEN, 5, rx=12)
s.text(GB_X + GW / 2, DNA_Y + 11, "B", 34, GREEN, "middle", "bold")
s.text(GB_X + GW / 2, 632, "靶基因", 30, GREEN, "middle", "bold")

# ---- 三维环化：增强子绕过 A 直接接到 B（绿弧 + 箭头）----
s.path(f"M {ENH_X + ENH_W} {DNA_Y - 26} C 230 246 596 250 {GB_X + 4} {DNA_Y - 52}",
       GREEN, 6)
s.polygon([(GB_X + 4, DNA_Y - 52), (GB_X - 18, DNA_Y - 86),
           (GB_X - 36, DNA_Y - 44)], GREEN)

# ---- 错误的「就近指派」（红虚线箭头，整条合成 1 个 <g>，红记 1 处）----
a1, a2 = ENH_X + ENH_W + 4, GA_X - 8
s.raw(f'<g stroke="{RED}" fill="{RED}">'
      f'<line x1="{a1}" y1="{DNA_Y - 30}" x2="{a2}" y2="{DNA_Y - 30}" '
      f'stroke-width="4" stroke-dasharray="12 9"/>'
      f'<polygon points="{a2},{DNA_Y - 30} {a2 + 16},{DNA_Y - 40} '
      f'{a2 + 16},{DNA_Y - 20}"/></g>')

s.save("15_enhancer_looping.svg")

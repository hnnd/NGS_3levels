#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""33_six_qc_gates.py — FIG-M05-33 六道质控过闸门禁（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.4 FIG-M05-33（P57，`.cols` 800×700，new-svg）。
教材依据：§15.4.4 L217–L244（四项指标及其适用体系）、§15.6 L425–L428（验收固定顺序：
比对率 → 重复率与 NRF → 片段长度阶梯 → FRiP 与 TSSE → IDR → 注释的 intergenic 比例）。
顺序不能颠倒：先查「数据有没有坏」，再查「实验做没做好」，最后查「峰集可不可信」。

图面：竖向六道闸门，每闸左侧绿节点串成主链（通闸），右侧一条红色横线指向同一根红色
「拦截」立柱——任一闸不合格就在此截断，不进下游。六闸的检查项逐字取方案原句；
此处**不写任何阈值数字**：四项指标的具体通过线依物种与体系而异（§15.4.4 逐条讨论过），
图上写死一条线会变成无入口经验数。

图内汉字 29 字（上限 30），逐字取方案原句「逐级质控：比对率、重复率、阶梯、落峰比、
重复性与注释」：逐级质控 4 ＋ 比对率 3 ＋ 重复率 3 ＋ 阶梯 2 ＋ 落峰比 3 ＋ 重复性 3
＋ 注释 2 ＝ 20，另加拦截立柱名「拦截」2 ＝ 22，加判读句「单一指标不放行」7 ＝ 29。
配色：通闸绿 `#00A087`、质控卡点深蓝 `#3C5488`、拦截警示红 `#E64B35`
（红线与立柱合成一个 `<g>` = 1 处、红字标签 1 处，共 2 处，在上限内）。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 33_six_qc_gates.py
"""
from svghelp import *

s = SVG()

s.text(400, 62, "逐级质控", 36, BLUE, "middle", "bold")

GATES = ["比对率", "重复率", "阶梯", "落峰比", "重复性", "注释"]
SPINE_X, SPINE_W = 210, 6
TOP, STEP = 152, 76
BEAM_X = 684                                    # 拦截立柱
DASH_X0 = 400                                   # 六条虚线统一右端起点（避免参差）

y_first = TOP
y_last = TOP + STEP * (len(GATES) - 1)

# ---------------- 主链：六道闸门 ----------------
s.line(SPINE_X, y_first, SPINE_X, y_last, GREEN, SPINE_W, cap="round")
for i, name in enumerate(GATES):
    y = TOP + i * STEP
    s.circle(SPINE_X, y, 15, GREEN, GREEN, 3)
    s.text(SPINE_X + 34, y + 11, name, 32, BLUE, "start", "bold")

# ---------------- 拦截：任一闸不合格即止步（红线 + 立柱合成 1 个 <g>） ----------------
d = []
for i in range(len(GATES)):
    y = TOP + i * STEP
    d.append(f'<line x1="{DASH_X0}" y1="{y}" x2="{BEAM_X - 8}" y2="{y}" '
             f'stroke-dasharray="12 10"/>')
d.append(f'<line x1="{BEAM_X}" y1="{y_first - 24}" x2="{BEAM_X}" '
         f'y2="{y_last + 24}" stroke-width="7"/>')
s.raw(f'<g stroke="{RED}" fill="none" stroke-width="4">{"".join(d)}</g>')
s.text(BEAM_X + 16, y_first - 30, "拦截", 32, RED, "start", "bold")

# ---------------- 结论（方案的判读要求：六项联查，不能凭单一指标放行） ----------------
s.text(400, 634, "单一指标不放行", 32, INK, "middle", "bold")

s.save("33_six_qc_gates.svg")
print(f"check: 六闸顺序 {GATES}；拦截柱 x={BEAM_X} 贯通 {y_first}–{y_last}")

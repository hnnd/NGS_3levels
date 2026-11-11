#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""37_motif_false_enrichment_table.py — FIG-M05-37 motif 假富集特征表（new-svg）

方案：`reviews/course/M05_FIGP_001.md` §4.4 FIG-M05-37（P61，`.cols` 800×700，new-svg）。
教材依据：§15.4.6 L263–L278（背景匹配是决定性的，只换背景就能造出 Top motif）、
§15.5.4 L377–L386（怎样察觉：看 `P-value`、`% of Targets`、`% of Background` 三列）。

图面两张对照卡，同一横轴量程（0–50%）：
左卡「正常」：targets 24% 明显高于 background 6%（×4.0），Top 几名同属一个家族（绿）；
右卡「假富集」：targets 41% 与 background 33% 只差一两倍（×1.2），Top 榜被高 GC 的简单
基序霸占（红）。两张卡底部的名字行是「Top 榜」的示意：左侧三个名字各不相同、同属一家族；
右侧同一个名字重复三遍，正是「高 GC 简单基序霸占榜首」的样子。两组数字都是**讲义设例**（§15.5.4 原文写明「讲义举例 24% 对 6%」、
「习题里的 41% 对 33%、p = 10⁻¹⁸ 是设例」），故图上显式标「设例」，不冒充实测：
本图因此不写 p 值，只给比例关系。

图内汉字 29 字（上限 30）：标题「基序假象」4 ＋ 卡名「正常」2「假富集」3 ＋「设例」2
＋ 结论「高碱基偏好致假富集」9 ＋「匹配背景后显著消失」9 ＝ 29。
列名与倍数写拉丁字符（targets／background／×4.0／×1.2），不写整句英文。
配色按方案：正常富集绿 `#00A087`；假富集红 `#E64B35` 只用两处——卡名 1 处、
两根条与百分比与倍数合并成一个 `<g>` 1 处。无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 37_motif_false_enrichment_table.py
"""
from svghelp import *

NORMAL = (24.0, 6.0)                      # §15.5.4 讲义设例：24% 对 6%
FAKE = (41.0, 33.0)                        # §15.5.4 习题设例：41% 对 33%
R_NORMAL = NORMAL[0] / NORMAL[1]           # 4.0
R_FAKE = FAKE[0] / FAKE[1]                 # 1.2424
assert abs(R_NORMAL - 4.0) < 1e-9
assert 1.2 < R_FAKE < 1.3

s = SVG()

s.text(400, 58, "基序假象", 36, BLUE, "middle", "bold")

CW_, CH_, GAP = 330, 366, 40
X0, Y0 = 30, 100
BAR_X, BAR_W = 24, 170
TOPV = 50.0                                # 两张卡共用同一量程 0–50%
BH = 44                                    # 条高


def draw_card(x, title, vals, color, ratio, family=None):
    s.rect(x, Y0, CW_, CH_, WHITE, PANEL, 3, rx=14)
    s.text(x + CW_ / 2, Y0 + 48, title, 32, color, "middle", "bold")
    for i, (cap, v) in enumerate(zip(("targets", "background"), vals)):
        cy = Y0 + 104 + i * 88
        s.text(x + BAR_X, cy - 12, cap, 30, GRAY, "start")
        s.rect(x + BAR_X, cy, BAR_W * v / TOPV, BH,
               color if i == 0 else WHITE, color if i == 1 else None, 3, rx=8)
        s.text(x + BAR_X + BAR_W * v / TOPV + 14, cy + 32,
               f"{v:.0f}%", 30, color, "start", "bold")
    s.text(x + CW_ / 2, Y0 + CH_ - 30, ratio, 30, color, "middle", "bold")
    if family:
        s.text(x + CW_ / 2, Y0 + CH_ - 72, family, 30, color, "middle", "bold")


# ---------------- 左：正常（绿） ----------------
draw_card(X0, "正常", NORMAL, GREEN, "×4.0", "SP1 · KLF · EGR")

# ---------------- 右：假富集（红：卡名 1 处 ＋ 条/百分比/倍数合成 <g> 1 处） ----------------
FX = X0 + CW_ + GAP
s.rect(FX, Y0, CW_, CH_, WHITE, PANEL, 3, rx=14)
s.text(FX + CW_ / 2, Y0 + 48, "假富集", 32, RED, "middle", "bold")

bars = []
for i, (cap, v) in enumerate(zip(("targets", "background"), FAKE)):
    cy = Y0 + 104 + i * 88
    bars.append(f'<text x="{FX + BAR_X}" y="{cy - 12}" font-size="30" '
                f'text-anchor="start" fill="{GRAY}">{cap}</text>')
    if i == 0:
        bars.append(f'<rect x="{FX + BAR_X}" y="{cy}" width="{BAR_W * v / TOPV:.1f}" '
                    f'height="{BH}" rx="8" fill="{RED}"/>')
    else:
        bars.append(f'<rect x="{FX + BAR_X}" y="{cy}" width="{BAR_W * v / TOPV:.1f}" '
                    f'height="{BH}" rx="8" fill="none" stroke-width="3"/>')
    bars.append(f'<text x="{FX + BAR_X + BAR_W * v / TOPV + 14:.1f}" y="{cy + 32}" '
                f'font-size="30" text-anchor="start">{v:.0f}%</text>')
bars.append(f'<text x="{FX + CW_ / 2}" y="{Y0 + CH_ - 72}" font-size="30" '
            f'text-anchor="middle" font-weight="bold">SP1 SP1 SP1</text>')
bars.append(f'<text x="{FX + CW_ / 2}" y="{Y0 + CH_ - 30}" font-size="30" '
            f'text-anchor="middle" font-weight="bold">×{R_FAKE:.1f}</text>')
s.raw(f'<g fill="{RED}" stroke="{RED}" font-family="{FONT}">{"".join(bars)}</g>')

# ---------------- 设例声明 ----------------
s.text(400, Y0 + CH_ + 46, "设例", 30, GRAY, "middle")

# ---------------- 结论（方案原句逐字，两句） ----------------
s.text(400, 560, "高碱基偏好致假富集", 32, INK, "middle", "bold")
s.text(400, 618, "匹配背景后显著消失", 32, GREEN, "middle", "bold")

s.save("37_motif_false_enrichment_table.svg")
print(f"check: 正常 {NORMAL[0]:.0f}%/{NORMAL[1]:.0f}% = ×{R_NORMAL:.1f}；"
      f"假富集 {FAKE[0]:.0f}%/{FAKE[1]:.0f}% = ×{R_FAKE:.2f}（§15.5.4 讲义设例）")

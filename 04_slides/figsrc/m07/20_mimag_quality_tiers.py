#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_mimag_quality_tiers.py — FIG-M07-22 MIMAG 基因组质量三档界限与门槛

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-22（P38，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.5（MIMAG：高质需完整度 >90% 且污染度 <5%，外加 rRNA/tRNA 齐全；
中质 ≥50% 与 <10%；其余归低质/废弃）。三档阈值都是标准门槛定义，不是实测数据；档位文字
「大于九十小于五」即 >90% 与 <5% 的口语化写法。
图内汉字 = 方案清单逐字，共 27 字（高质：大于九十小于五 / 中质：大于五十小于十 /
短读难达高质量）。低质卡用灰框 + 星标表示「其余都归这里」，不写字（写字会破 30 红线）。
红色一处语义组：右侧红色虚线括注 + 红字「短读难达高质量」指向高质档。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 20_mimag_quality_tiers.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 三档阶梯卡（越往上门槛越高） ----------------
TIERS = (
    ("高质：大于九十小于五", GREEN, GREEN_TINT, 120, 48, 496),
    ("中质：大于五十小于十", CYAN_DEEP, CYAN_TINT, 300, 112, 496),
)
for cap, edge, tint, y, x, w in TIERS:
    s.rect(x, y, w, 124, tint, edge, 4, rx=16)
    s.label(x + w / 2, y + 62, cap.split("："), 32, edge, "middle", "bold")

# 低质卡（无文字，灰框 + 星标）
s.rect(192, 476, 432, 108, PANEL, GRAY, 4, rx=16)
s.star(240, 530, 28, GRAY)

# 阶梯递降箭头（高 → 中 → 低：门槛逐级放宽）
for x0, y0, y1 in ((96, 244, 300), (160, 424, 476)):
    s.arrow(x0, y0, x0, y1 - 6, GRAY, 4, 12)

# ---------------- 附加门槛：rRNA / tRNA 齐全（圆点串示意，无文字） ----------------
s.rect(48, 620, 496, 52, BLUE_TINT, BLUE, 3, rx=14)
for i in range(6):
    s.circle(96 + i * 44, 646, 10, BLUE if i < 3 else PURPLE)

# ---------------- 红色语义组：右缘虚线括注 + 下方红字「短读难达 / 高质量」 ----------------
BX = 570                                        # 括注线只括高质档（短读够不到的就是这一档）
CY = 182                                        # 括注与两行红字的垂直中心
s.line(BX, CY - 74, BX, CY + 74, RED, 4, dash="10 9")
s.line(BX, CY - 74, BX - 14, CY - 74, RED, 4)
s.line(BX, CY + 74, BX - 14, CY + 74, RED, 4)
s.label(690, CY + 96, ["短读难达", "高质量"], 30, RED, "middle", "bold", leading=1.5)

s.save("20_mimag_quality_tiers.svg")

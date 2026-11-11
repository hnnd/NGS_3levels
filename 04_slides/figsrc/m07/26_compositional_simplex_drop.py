#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""26_compositional_simplex_drop.py — FIG-M07-29 组成性数据几何约束：单纯形与假下降

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-29（P55，`.cols` 一栏 800×700，new-svg）。
教材依据：§19.4.8（相对丰度是组成性数据：各组分之和恒为 1，落在单纯形上；某一菌绝对量暴增，
总分母同步变大，其他绝对量未变的类群相对份额被被动压低，读图者极易误判为「抑制」）。
版式：上排两根「绝对生物量」竖柱（深蓝，A 菌未变、B 菌暴增）；中段青蓝箭头与
「归一化比例恒为一」说明归一化这一步；下排一条等宽组成条（两段拼满整条 = 和恒为一），
A 菌那一段变窄，橙色箭头指出 A 菌的相对份额被动假降；红字「非真实抑制」只出现一次。
柱高与段宽都是示意比例，不标数值（这些数字无实测入口）。
图内汉字 = 方案清单逐字（绝对生物量暴增 7 / 归一化比例恒为一 8 / 未变类群被动假降 8 /
非真实抑制 5）＝ 28 字。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 26_compositional_simplex_drop.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

# ---------------- 上排：绝对生物量（竖柱，A 未变、B 暴增） ----------------
s.text(400, 64, "绝对生物量暴增", 32, BLUE, "middle", "bold")

AB = 330                                  # 绝对量基线
XA, XB, BW = 140, 440, 150
for x, v, col in ((XA, 120, BLUE), (XB, 210, BLUE)):
    s.rect(x, AB - v, BW, v, col, rx=8)
s.line(88, AB, 624, AB, INK, 4)
s.text(112, 356, "A", 30, GRAY, "middle")
s.text(618, 356, "B", 30, GRAY, "middle")
# 暴增提示：B 柱顶粗箭头
s.arrow(XB + BW / 2, AB - 222, XB + BW / 2, AB - 248, ORANGE_DEEP, 5, 14)

# ---------------- 中段：归一化 ----------------
s.text(400, 372, "归一化比例恒为一", 30, CYAN_DEEP, "middle", "bold")
s.arrow(400, 388, 400, 428, CYAN_DEEP, 6, 18)

# ---------------- 下排：组成条（两段拼满整条，和恒为一） ----------------
CY, CH = 440, 68
SEG_L, SEG_R = 120, 680
CUT = SEG_L + 112                          # A 菌归一化后的段宽（示意）
s.rect(SEG_L, CY, SEG_R - SEG_L, CH, PANEL, rx=10)
s.rect(SEG_L, CY, CUT - SEG_L, CH, BLUE_TINT, BLUE, 3, rx=10)
s.rect(CUT, CY, SEG_R - CUT, CH, BLUE, rx=10)
s.text((SEG_L + CUT) / 2, CY + 43, "A", 30, BLUE, "middle", "bold")
s.text((CUT + SEG_R) / 2, CY + 43, "B", 30, WHITE, "middle", "bold")

# ---------------- 橙色：A 菌相对份额被动假降 ----------------
s.arrow((SEG_L + CUT) / 2, CY + CH + 8, (SEG_L + CUT) / 2, CY + CH + 40,
        ORANGE_DEEP, 6, 16)
s.label((SEG_L + CUT) / 2, 592, ["未变类群", "被动假降"], 30, ORANGE_DEEP,
        "middle", "bold", leading=1.34)

# ---------------- 唯一红处 ----------------
s.text(400, 682, "非真实抑制", 34, RED, "middle", "bold")

s.save("26_compositional_simplex_drop.svg")

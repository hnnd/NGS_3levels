#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_confounding_and_truncation_warning.py — 生成 19_confounding_and_truncation_warning.svg
（FIG-M01-22：设计层失效：完全混杂与静默截断）【data-plot】

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-22（P59，cols 一栏，800×700）。
数据（与 demos 现跑一致）：demos/ch13_truncation_confounding.py --selftest
Part 0 真实锚点（29 文件 14 截断，最小 13.3%，rc=0）与 Part 3（全深度
低/中/高表达检出率 2.7%/45.0%/100.0%；B 组截断至 13%–84% 后
1.3%/30.0%/97.7%）。教材 §13.5.4 L367–370。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 19_confounding_and_truncation_warning.py
"""
from svghelp import *  # noqa: F401,F403

FULL = (2.7, 45.0, 100.0)     # 全深度：低/中/高表达层检出率（%）
TRUNC = (1.3, 30.0, 97.7)     # B 组静默截断后
TIERS = ("低", "中", "高")


def main():
    # 与 demos Part 3 印刷值逐一核对
    for f, t in zip(FULL, TRUNC):
        assert t <= f + 1e-9
    assert TRUNC[0] < FULL[0] and TRUNC[2] > 90
    print(f"check: 全深度 {FULL} vs 截断 {TRUNC}（demos Part 3 印刷值）；"
          "锚点 29 文件 14 截断、最小 13.3%、rc=0（demos Part 0 / 根 CLAUDE.md）")

    s = SVG(800, 700)

    # 左栏：完全混杂，两效应绑定（锁）
    s.rect(40, 80, 300, 470, WHITE, PANEL, 3, rx=14)
    s.text(190, 124, "完全混杂两效应绑定", 30, INK, "middle", "bold")
    s.arrow(70, 220, 310, 220, BLUE, 16, 24)
    s.arrow(70, 292, 310, 292, ORANGE, 16, 24)
    s.path("M 172 348 A 18 18 0 1 1 208 348", INK, 6)
    s.rect(150, 348, 80, 56, BLUE, rx=10)
    s.circle(190, 372, 8, WHITE)
    s.line(190, 376, 190, 388, WHITE, 5)
    s.text(190, 505, "静默截断 29 截 14", 30, INK, "middle", "bold")

    # 右栏：检出率条形对比（低表达截断柱红色）
    s.rect(380, 60, 380, 490, WHITE, PANEL, 3, rx=14)
    base, k = 480, 3.3  # 检出率(%) → 高度
    centers = (480, 590, 700)
    bars = []
    for tier, f, t, cx in zip(TIERS, FULL, TRUNC, centers):
        hf, ht = f * k, t * k
        s.rect(cx - 48, base - hf, 42, max(hf, 4), BLUE)
        tcolor = RED if tier == "低" else ORANGE
        s.rect(cx + 6, base - ht, 42, max(ht, 4), tcolor)
        bars.append((tier, f, t, cx, hf, ht))
    for tier, f, t, cx, hf, ht in bars:
        fcol = RED if tier == "低" else INK
        if tier == "低":
            # 矮柱：数值右对齐于柱体上方两侧，避开相邻中组高柱（x≥542）
            s.text(cx - 52, base - hf - 12, f"{f:.1f}", 30, GRAY, "end")
            s.text(cx + 58, base - ht - 12, f"{t:.1f}", 30, fcol, "end")
        elif tier == "中":
            s.text(cx - 27, base - hf - 12, f"{f:.1f}", 30, GRAY, "middle")
            s.text(cx + 27, base - ht - 12, f"{t:.1f}", 30, fcol, "middle")
        else:
            # 高柱顶天：截断柱数值再抬高一行错开
            s.text(cx - 27, base - hf - 12, f"{f:.1f}", 30, GRAY, "middle")
            s.text(cx + 27, base - ht - 46, f"{t:.1f}", 30, fcol, "middle")
        s.text(cx, base + 44, tier, 30, GRAY, "middle")
    s.line(410, base, 740, base, BLUE, 4)

    # 红色警示（2 处：低表达塌陷 + 列表偏高表达；引出线并入塌陷簇）
    s.line(507, 492, 507, 545, RED, 4, dash="10 8")
    s.text(483, 585, "低表达检出塌至 1.3%", 30, RED, "middle", "bold")
    s.text(775, 320, "列表偏高表达", 30, RED, "middle", "bold", rotate=90)

    s.save("19_confounding_and_truncation_warning.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

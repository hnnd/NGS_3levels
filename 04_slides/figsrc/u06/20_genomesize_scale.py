#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_genomesize_scale.py — 生成 20_genomesize_scale.svg（FIG-U06-20：genomeSize 量级算术）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-20（P62，cols 一栏，800×700）。
数据：1.6×10⁸ bp ÷ genomeSize 三档（除法可复核，教材 §8.5.3 L391）：
  4m→40×（绿，正确）；40m→4×（橙）；4g→0.04×（红，学生最常写错）。
「1.28×」类日志指纹留在 deck 文字并标「示意指纹（讲义 ⑨E3，设例）」，不进图。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 20_genomesize_scale.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    total = 1.6e8
    rows = [("4m", 4e6, "40×", GREEN), ("40m", 4e7, "4×", ORANGE),
            ("4g", 4e9, "0.04×", RED)]
    for name, gs, expect, _ in rows:
        assert abs(total / gs - float(expect.replace("×", ""))) < 1e-9
    print("check: 1.6e8/4m=40；/40m=4；/4g=0.04")

    s = SVG(800, 700)
    # 读段总量牌：上标 8 用独立 <text> 定位（U+2078 无字形；tspan dy 在
    # 部分渲染器下基线错位，D127 修订为绝对定位三段文字，读法不变）
    s.rect(60, 66, 420, 90, WHITE, BLUE, 4, rx=14)
    s.raw(f'<text x="336" y="124" font-family="{FONT}" font-size="36" '
          f'fill="{BLUE}" text-anchor="end" font-weight="bold">读段 '
          f'1.6×10</text>')
    s.raw(f'<text x="340" y="108" font-family="{FONT}" font-size="30" '
          f'fill="{BLUE}" text-anchor="start" font-weight="bold">8</text>')
    s.raw(f'<text x="356" y="124" font-family="{FONT}" font-size="36" '
          f'fill="{BLUE}" text-anchor="start" font-weight="bold"> bp</text>')

    # 三行除法条（左框加宽到容纳最长文字 genomeSize = 40m）
    for i, (name, gs, expect, color) in enumerate(rows):
        y = 200 + i * 110
        s.rect(40, y, 380, 76, WHITE, PANEL, 3, rx=12)
        s.text(230, y + 50, f"genomeSize = {name}", 32, INK, "middle", "bold")
        s.arrow(430, y + 38, 470, y + 38, GRAY, 6)
        s.rect(485, y, 175, 76, color, rx=12)
        s.text(572, y + 50, expect, 40, WHITE, "middle", "bold")

    # 底部灰色注记
    s.text(400, 572, "单位只有 k/m/g", 30, GRAY, "middle", "bold")
    s.text(400, 632, "改完删 -d 重跑", 30, GRAY, "middle", "bold")

    s.save("20_genomesize_scale.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

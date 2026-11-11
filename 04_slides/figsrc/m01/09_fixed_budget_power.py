#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_fixed_budget_power.py — 生成 09_fixed_budget_power.svg
（FIG-M01-11：同一预算下功效阶梯）【data-plot】

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-11（P28，cols 一栏，800×700）。
数据（与 demos 现跑一致）：demos/ch13_variance_partition.py --selftest Part 2
（两组共 180 M，δ=1.0, α=0.05；3×30 M: SE 0.8433 功效 0.152；6×15 M: 0.6146/0.313；
9×10 M: 0.5164/0.444；18×5 M: 0.3944/0.693）。教材 §13.4.3 L174–183。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 09_fixed_budget_power.py
"""
import math
import sys
from pathlib import Path

from svghelp import *  # noqa: F401,F403

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from ch13_variance_partition import power_twosample  # noqa: E402

COMBOS = [(3, 30), (6, 15), (9, 10), (18, 5)]  # (n, d M)，每组预算 90 M
PRINTED_PW = [0.152, 0.313, 0.444, 0.693]      # demos Part 2 印刷值
PRINTED_SE = [0.8433, 0.6146, 0.5164, 0.3944]


def main():
    bars = []
    for (n, d), ppw, pse in zip(COMBOS, PRINTED_PW, PRINTED_SE):
        v = 1.0 + 2.0 / d
        se = math.sqrt(2 * v / n)
        pw = power_twosample(n, v, 1.0, 0.05)
        assert abs(pw - ppw) < 5e-4, (n, d, pw, ppw)
        assert abs(se - pse) < 5e-4, (n, d, se, pse)
        bars.append((n, d, se, pw))
        print(f"check: {n}×{d} M  SE={se:.4f}（demos {pse}）  "
              f"功效={pw:.3f}（demos {ppw}）")

    s = SVG(800, 700)
    s.text(60, 46, "同一预算 180 M", 34, INK, "start", "bold")
    s.text(740, 46, "SE 从 0.84 降到 0.39", 30, INK, "end", "bold")

    base, k = 580, 586.7  # 功效 → 高度
    colors = [RED, CYAN, PURPLE, GREEN]
    centers = [160, 340, 520, 700]
    for (n, d, se, pw), color, cx in zip(bars, colors, centers):
        h = pw * k
        s.rect(cx - 55, base - h, 110, h, color, rx=8)
        s.text(cx, base - h + 38, f"{pw:.3f}", 30, WHITE, "middle", "bold")
        s.text(cx, base - h - 14, f"SE {se:.2f}", 30, GRAY, "middle")
        s.text(cx, base + 42, f"{n}×{d}", 30, GRAY, "middle")
    s.line(90, base, 760, base, BLUE, 4)

    # 功效单调上升（绿趋势线）
    s.polyline([(350, 160), (430, 135), (505, 112)], GREEN, 5)
    s.text(430, 96, "功效单调上升", 30, GREEN, "middle", "bold")

    # 底部结论条
    s.rect(200, 640, 400, 52, BLUE, rx=12)
    s.text(400, 677, "加重复优先于加深度", 32, WHITE, "middle", "bold")

    s.save("09_fixed_budget_power.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_false_loss_vs_threshold_relaxation.py — 13_false_loss_vs_threshold_relaxation.svg
（FIG-M02-18，P37，cols）：漏检率 q=1% 下放宽 k 对抗真核心误判丢失【data-plot】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-18。数据（与 demos 现跑一致）：
demos/ch11_core_threshold.py --selftest：q=1%、n=12 时 k=0 误失 11.36%，
放宽到 k=1 降至 0.62%（约降 18 倍），k=2 为 0.02%。无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 13_false_loss_vs_threshold_relaxation.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch11_core_threshold as demo  # noqa: E402

from svghelp import (BLUE, GREEN, GRAY, INK, PURPLE, RED, SVG, WHITE)


def check_data():
    vals = {k: demo.p_misjudge(12, 0.01, k) * 100 for k in (0, 1, 2)}
    assert abs(vals[0] - 11.3615) < 1e-3, vals[0]
    assert abs(vals[1] - 0.6175) < 5e-3, vals[1]
    assert abs(vals[2] - 0.0205) < 5e-3, vals[2]
    ratio = vals[0] / vals[1]
    print(f"check: k=0 {vals[0]:.2f}%、k=1 {vals[1]:.2f}%、k=2 {vals[2]:.2f}%"
          f"（降 {ratio:.0f} 倍，demos 复算）")
    return vals


def main():
    vals = check_data()

    s = SVG(800, 700)
    s.text(400, 96, "漏检率 q=1% 下真核心误失率", 34, BLUE, "middle", "bold")

    # 柱状区：0..12% → 高 400px，基线 y=560
    base, scale = 560.0, 400.0 / 12.0
    bars = [(150, 150, RED, "k=0 误失 11.36%"),
            (400, max(vals[1] * scale, 10), GREEN, "k=1 降至 0.62%"),
            (620, max(vals[2] * scale, 8), PURPLE, None)]
    s.line(90, base, 740, base, INK, 5)
    for cx, h, color, lab in bars:
        s.rect(cx - 70, base - h, 140, h, color, rx=6)
        if lab:
            s.text(cx, base - h - 22, lab, 30, color, "middle", "bold")
        s.text(cx, base + 44, f"k={bars.index((cx, h, color, lab))}",
               32, INK, "middle", "bold")

    # 骤降箭头（k=0 → k=1，18×）
    s.line(240, 250, 330, 500, GRAY, 5, dash="12 10")
    s.polygon([(330, 500), (312, 474), (336, 462)], GRAY)
    s.text(262, 350, "18×", 32, GRAY, "middle", "bold")

    s.text(400, 656, "放宽阈值对抗注释漏检", 34, INK, "middle", "bold")

    s.save("13_false_loss_vs_threshold_relaxation.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

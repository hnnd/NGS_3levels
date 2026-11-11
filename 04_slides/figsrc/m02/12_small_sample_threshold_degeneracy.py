#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_small_sample_threshold_degeneracy.py — 12_small_sample_threshold_degeneracy.svg
（FIG-M02-17，P36，cols）：小样本 95% 阈值退化阶梯【data-plot】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-17。数据（与 demos 现跑一致）：
demos/ch11_core_threshold.py --selftest：n=4 与 n=12 时 ⌈0.95n⌉=n（k=0，
95%≡100%）；n=20 起才允许缺 1 株（k=1）。无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 12_small_sample_threshold_degeneracy.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch11_core_threshold as demo  # noqa: E402

from svghelp import (BLUE, CYAN, GRAY, INK, RED, SVG, WHITE)


def check_data():
    ks = {n: demo.k_allowed(n, 0.95) for n in range(1, 25)}
    assert ks[4] == 0 and ks[12] == 0, (ks[4], ks[12])
    assert ks[19] == 0 and ks[20] == 1, (ks[19], ks[20])
    print("check: n=4 与 n=12 → k=0；n=20 起 k=1（demos 复算）")
    return ks


def main():
    ks = check_data()

    s = SVG(800, 700)

    # 坐标区：n∈[1,24] → px 90..740；k∈[0,2.4] → py 560..120
    x0, x1, y0, y1 = 90.0, 740.0, 560.0, 120.0

    def px(n):
        return x0 + (n - 1) / 23.0 * (x1 - x0)

    def py(k):
        return y0 - k / 2.4 * (y0 - y1)

    # 阶梯折线（深蓝）
    pts = []
    for n in range(1, 25):
        pts.append((px(n), py(ks[n])))
        if n < 24 and ks[n + 1] != ks[n]:
            pts.append((px(n + 1), py(ks[n])))
    s.polyline(pts, BLUE, 7)

    # 坐标轴与刻度
    s.line(x0, y0, x1 + 12, y0, INK, 5)
    s.line(x0, y0, x0, y1 - 12, INK, 5)
    for n in (1, 4, 8, 12, 16, 20, 24):
        s.line(px(n), y0, px(n), y0 + 10, INK, 4)
        s.text(px(n), y0 + 44, str(n), 30, INK, "middle")
    for k in (0, 1, 2):
        s.line(x0 - 10, py(k), x0, py(k), INK, 4)
        s.text(x0 - 18, py(k) + 11, str(k), 30, INK, "end")

    # 红色退化区间标注（n=4..12 恒 k=0）：文在上、括号贴 k=0 线
    s.text((px(4) + px(12)) / 2, 470, "退化为全株共有 k=0", 30, RED,
           "middle", "bold")
    s.text((px(4) + px(12)) / 2, 508, "95%≡100%", 34, RED, "middle", "bold")
    s.line(px(4), 528, px(12), 528, RED, 6)
    s.line(px(4), 528, px(4), 552, RED, 6)
    s.line(px(12), 528, px(12), 552, RED, 6)

    # 标题与 n=20 标注（青蓝，标签在点左侧避免出界）
    s.text(60, 100, "n=4 与 n=12：95%≡100%", 34, BLUE, "start", "bold")
    s.circle(px(20), py(1), 11, WHITE, CYAN, 6)
    s.text(px(20) - 24, py(1) + 11, "n=20 起才允许缺 1 株", 30, CYAN, "end",
           "bold")

    s.text(400, 656, "报核心必带 n、m、k", 32, INK, "middle", "bold")

    s.save("12_small_sample_threshold_degeneracy.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

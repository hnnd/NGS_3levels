#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_overlap_readlen_bars.py — FIG-M06-07 重叠×读长合成演示（data-plot）

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-07（P18，cols 一栏 800×700，data-plot）。
数据来源：`demos/ch18_overlap_trunclen.py --selftest` 现跑输出（本脚本 import 同函数、同参数复算
并断言）：S1 重叠 187 bp / 合并保留 99.0%；S2 重叠 40 bp / 19.6%；S4 重叠 40 bp / 78.2%。
展示「同为 40 bp 重叠，PE300 保住质量后合并恢复」；S2 与 S4 的差别不在重叠而在读长。
图内汉字 = 方案原句逐字，共 15 字（充裕九成九 / 两难仅两成 / 换长读恢复）；其余为场景代号、
重叠算式与百分比。无网络；随机数经 demos 同种子（20261104）复算，不另取种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 07_overlap_readlen_bars.py
"""
import contextlib
import io
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]           # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch18_overlap_trunclen as ov                  # noqa: E402

from svghelp import *                              # noqa: F401,F403,E402


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        r = ov.run(20000, 2.0, 12, 20, 20261104)
    s1, s2, s4 = (r["S1 V4 正常"], r["S2 V3-V4 保重叠"], r["S4 V3-V4 配 PE300"])

    # 与 demos --selftest 的断言同口径：图里只画这三个场景的三个数
    assert s1["overlap"] == 187 and 0.985 <= s1["merged"] <= 0.995, s1
    assert s2["overlap"] == 40 and 0.19 <= s2["merged"] <= 0.20, s2
    assert s4["overlap"] == 40 and 0.77 <= s4["merged"] <= 0.79, s4
    assert s4["merged"] > 3 * s2["merged"]          # 同 40 bp 重叠，读长决定成败

    vals = [
        ("S1", "O = 187 bp", s1["merged"], GREEN, "充裕九成九"),
        ("S2", "O = 40 bp", s2["merged"], RED, "两难仅两成"),
        ("S4", "O = 40 bp", s4["merged"], BLUE, "换长读恢复"),
    ]
    print("check: " + "  ".join(f"{c} 重叠 {o} 合并 {100*v:.1f}%" for c, o, v, _, _ in vals))

    s = SVG()

    # ---- 坐标框：0 / 50% / 100% 三条参考线 ----
    L, B, T = 108, 512, 168
    s.line(L, B, 780, B, INK, 4)
    for frac in (0.0, 0.5, 1.0):
        y = B - frac * (B - T)
        if frac > 0:
            s.line(L, y, 780, y, PANEL, 3, dash="10 9")
        s.line(L - 10, y, L, y, INK, 3)
        s.text(L - 18, y + 10, f"{int(frac*100)}%", 30, GRAY, "end")

    centers = (222, 436, 650)
    BW = 112
    for cx, (code, eq, v, col, cn) in zip(centers, vals):
        y = B - v * (B - T)
        s.rect(cx - BW / 2, y, BW, B - y, col, rx=8)
        # 百分比写在条顶（红条低，写在条内会压字，统一放条外上方）
        s.text(cx, y - 16, f"{100*v:.1f}%", 34, col, "middle", "bold")
        s.text(cx, B + 44, code, 32, GRAY, "middle", "bold")
        s.text(cx, B + 86, eq, 30, INK, "middle")
        s.text(cx, B + 136, cn, 30, col if col != RED else ORANGE_DEEP,
              "middle", "bold")

    s.save("07_overlap_readlen_bars.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

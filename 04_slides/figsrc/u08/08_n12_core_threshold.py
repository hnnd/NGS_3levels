#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_n12_core_threshold.py — 生成 08_n12_core_threshold.svg（FIG-U08-08：
n=12 整数阶梯退化与放宽漏检率）

方案：reviews/course/U08_FIGP_001.md §4 FIG-U08-08（P24，cols 一栏，800×700）【data-plot】。
数据（与 demos 现跑一致）：demos/ch11_core_threshold.py —— k_allowed(n,p)=n−⌈p·n⌉；
n=12 时 100%/99%/95% 三档均需 12 株（k=0）；缺 1 株真实比例 11/12=91.67%；
q=1% 漏检率下误判率 p_misjudge(12,0.01,0)=11.36%（=1−0.99^12），
放宽到缺 1 株 p_misjudge(12,0.01,1)=0.62%（教材 §11.4.4、§11.5.2）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 08_n12_core_threshold.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "textbook"
                       / "demos"))
import ch11_core_threshold as demo  # noqa: E402

from svghelp import *  # noqa: F401,F403,E402


def main():
    # —— 数据复核（与 demos selftest 同一公式同一参数）——
    assert demo.k_allowed(12, 1.00) == 0
    assert demo.k_allowed(12, 0.99) == 0
    assert demo.k_allowed(12, 0.95) == 0
    real_k1 = (12 - 1) / 12                       # 0.91666…
    assert abs(real_k1 - 0.9167) < 1e-3
    p100 = demo.p_misjudge(12, 0.01, 0)
    pk1 = demo.p_misjudge(12, 0.01, 1)
    assert abs(p100 - 0.113615) < 1e-5            # 11.36%
    assert abs(pk1 - 0.00617) < 5e-4              # 0.62%
    print(f"check: n=12 三档 k=0；缺 1 株={real_k1:.2%}；"
          f"误判 {p100:.2%} → {pk1:.2%}")

    s = SVG(800, 700)
    # 左栏标题
    s.text(40, 64, "n=12：95% 仍为 12 株", 34, BLUE, "start", "bold")

    # —— 左面板：取整阶梯（柱高=需存在的株数）——
    LX0, LY1, BW, GAP, SCALE = 70, 380, 62, 26, 22
    steps = [("100%", "12", BLUE, 12),
             ("99%", "12", BLUE, 12),
             ("95%", "12", BLUE, 12),
             ("缺 1 株", "11", CYAN, 11)]
    for i, (lab, val, color, h) in enumerate(steps):
        x = LX0 + i * (BW + GAP)
        ytop = LY1 - h * SCALE
        s.rect(x, ytop, BW, h * SCALE, color, rx=6)
        s.text(x + BW / 2, ytop - 16, val, 32, color, "middle", "bold")
        s.text(x + BW / 2, LY1 + 44, lab, 30, INK, "middle")
    # 12 株全有基准虚线
    s.line(LX0 - 20, LY1 - 12 * SCALE, LX0 + 3 * (BW + GAP) + BW + 8,
           LY1 - 12 * SCALE, GRAY, 3, dash="10 8")
    # k 标注行（bars 1–3 共享 k=0；bar4 k=1）
    s.text(219, LY1 + 96, "k=0 缺 0 株", 30, GRAY, "middle")
    s.text(371, LY1 + 96, "k=1 缺 1 株", 30, CYAN_DEEP, "middle")
    s.text(70, LY1 + 150, "缺 1 株为 91.67%", 32, INK, "start", "bold")

    # —— 右面板：漏检误判率柱状（11.36% vs 0.62%）——
    RX0, RY1 = 510, 420
    rscale = 2500                                 # 100% → 2500px
    bars = [("k=0", p100, RED), ("k=1", pk1, GREEN)]
    for i, (lab, v, color) in enumerate(bars):
        x = RX0 + i * 140
        h = v * rscale
        s.rect(x, RY1 - h, 84, h, color, rx=6)
        s.text(x + 42, RY1 - h - 16, f"{v:.2%}", 32, color, "middle", "bold")
        s.text(x + 42, RY1 + 44, lab, 32, INK, "middle", "bold")
    s.line(RX0 - 16, RY1, 760, RY1, INK, 3)

    # 底部结论横幅
    s.rect(120, 590, 560, 62, BLUE, rx=12)
    s.text(400, 633, "漏检误判：11.36% 降至 0.62%", 34, WHITE, "middle",
           "bold")
    s.text(400, 680, "合成算例 demos/ch11_core_threshold.py", 30, GRAY,
           "middle")

    s.save("08_n12_core_threshold.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

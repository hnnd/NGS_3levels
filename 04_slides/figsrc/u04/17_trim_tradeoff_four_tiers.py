#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_trim_tradeoff_four_tiers.py — 生成 17_trim_tradeoff_four_tiers.svg
（FIG-U04-20：四档阈值清洗收益与代价折线【data-plot】）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-20（P51，cols 一栏，viewBox 800×700）。
横轴 Q15–Q30 四档；深蓝柱 = 保留碱基（持续跌），绿线 = Q30%（阈值升高质量升）；
Q30 处红字「三十档达标百 / 有效碱基剩六成」（121,980 / 200,000 = 61.0%）。
数据来源（直接调用 demos，逐项一致）：demos/ch06_trim_threshold.py
  gen_reads(seed=42) + run_fastp_model（window=4, length_required=50）。
依据：教材 §6.4.5 L144–154；demos --selftest PASS 21/21。
图内汉字 27，红色 1 处。无网络、固定种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 17_trim_tradeoff_four_tiers.py
"""
import sys

from svghelp import *

ROOT = Path(__file__).resolve().parents[3]  # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from ch06_trim_threshold import REAL_RUNS, gen_reads, run_fastp_model  # noqa: E402


def main():
    reads = gen_reads(42, 2000)
    tiers, bars, line = (15, 20, 25, 30), [], []
    for q in tiers:
        r = run_fastp_model(reads, q, 4, 50)
        want = REAL_RUNS[q]
        assert r["passed"] == want["passed"] == 2000
        assert r["bases"] == want["bases"]
        assert abs(r["q30_pct"] - want["q30_pct"]) < 0.01
        bars.append(r["bases"])
        line.append(r["q30_pct"])
    assert bars == [181973, 172152, 151168, 121980]
    print(f"check: 碱基 {bars} bp；Q30% {['%.2f' % v for v in line]}")

    s = SVG(800, 700)
    X0, BASE, TOP = 100, 520, 180
    VMAX = 200000.0
    HS = BASE - TOP            # 柱高比例尺（200k → 340px）

    def gy_b(v):
        return BASE - v / VMAX * HS

    def gy_q(p):
        return BASE - p / 100.0 * HS

    # 网格与左轴（碱基）
    for v, lab in ((200000, "200k"), (150000, "150k"), (100000, "100k"),
                   (50000, "50k")):
        s.line(X0, gy_b(v), 740, gy_b(v), PANEL, sw=3)
        s.text(X0 - 12, gy_b(v) + 10, lab, 30, GRAY, "end")
    s.line(X0, BASE, 740, BASE, INK, sw=4)
    s.line(X0, TOP, X0, BASE, INK, sw=4)
    s.text(110, 84, "保留碱基持续跌", 30, BLUE, "start", "bold")
    s.text_rot(38, (TOP + BASE) / 2, "Bases (bp)", -90)

    # 深蓝柱（四档保留碱基，数值标签置于柱内顶部）
    xcs = []
    for i, q in enumerate(tiers):
        cx = 188 + i * 160
        xcs.append(cx)
        h = bars[i] / VMAX * HS
        s.rect(cx - 38, BASE - h, 76, h, BLUE, rx=8)
        s.text(cx, BASE - h + 42, f"{round(bars[i] / 1000)}k", 30, WHITE,
               "middle", "bold")

    # 绿线（Q30%，数值标签放在柱间空隙）
    pts = [(xcs[i] + 60, gy_q(line[i])) for i in range(4)]
    s.polyline(pts, GREEN, sw=6)
    for i, (px, py) in enumerate(pts):
        s.circle(px, py, 9, GREEN)
    gaps = [(268, 265), (428, 243), (592, 212)]
    for i, (lx, ly) in enumerate(gaps):
        s.text(lx, ly, f"{line[i]:.1f}%", 30, GREEN_DEEP, "middle", "bold")
    s.text(712, 114, f"{line[3]:.1f}%", 30, GREEN_DEEP, "end", "bold")
    s.text(740, 60, "阈值升高质量升", 30, GREEN_DEEP, "end", "bold")

    # Q30 处红字（唯一红色处）
    s.text(664, 612, "三十档达标百", 30, RED, "middle", "bold")
    s.text(664, 660, "有效碱基剩六成", 30, RED, "middle", "bold")

    # 横轴档位
    for i, q in enumerate(tiers):
        s.text(xcs[i], 566, f"Q{q}", 30, GRAY, "middle", "bold")

    s.save("17_trim_tradeoff_four_tiers.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

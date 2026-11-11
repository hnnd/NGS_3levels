#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_orf_length_decay.py — 生成 05_orf_length_decay.svg（FIG-U07-05：随机序列 ORF 随长度指数衰减）【data-plot】

方案：reviews/course/U07_FIGP_001.md §4.2 FIG-U07-05（P17，cols 一栏，viewBox 800×700）。
数据（与 demos 现跑一致，import 复算）：demos/ch09_orf_length.py --selftest
（G=1,000,000 bp，双链六框，固定种子 20261104）：
门槛 30 → 观测 22,170（期望 22,205.8）；门槛 300 → 观测 0（期望 0.1，精确 0.0521）；
曲线 E = 6·p·(G/3)·(1−p)^L（教材 §9.4.2 L108–122）。纵轴对数刻度。
合成算例标注（图内灰字）。无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 05_orf_length_decay.py
"""
from svghelp import *  # noqa: F401,F403
import ch09_orf_length as orfdemo

G = 1_000_000
SEED = 20261104


def main():
    rows = orfdemo.run(G, [30, 60, 100, 150, 300], SEED)
    obs = {L: o for L, o, _ in rows}
    exp = {L: e for L, _, e in rows}
    assert [obs[L] for L in (30, 60, 100, 150, 300)] == [22170, 5206, 768, 64, 0]
    assert abs(exp[30] - 22205.8) < 0.1 and abs(exp[300] - 0.0521) < 1e-3
    print(f"check: L=30 obs={obs[30]} exp={exp[30]:.1f}; "
          f"L=300 obs={obs[300]} exp={exp[300]:.4f}")

    s = SVG(800, 700)
    s.text(770, 44, "合成算例", 30, GRAY, "end")

    # 坐标系：x 轴 y=540（100..740），y 轴 x=100（140..540），对数刻度
    XA0, XA1, YA1 = 100, 740, 540
    s.line(XA0, 140, XA0, YA1, BLUE, 5)
    s.line(XA0, YA1, XA1, YA1, BLUE, 5)

    def y_of(v):  # log10(v) ∈ [0, 4.346] → [540, 150]
        return YA1 - max(0.0, min(4.5, __import__("math").log10(v))) * 86.0

    for v in (1, 10, 100, 1000, 10000):
        y = y_of(v)
        s.line(XA0, y, XA1, y, PANEL, 3)
        s.text(92, y + 10, f"{v:g}", 30, GRAY, "end")
    s.raw(f'<g transform="rotate(-90 30 350)">'
          f'<text x="30" y="350" font-family="{FONT}" font-size="30" '
          f'fill="{GRAY}" text-anchor="middle">expected count</text></g>')

    def x_of(L):
        return 140 + (L - 30) / 270.0 * 560.0

    for L in (30, 60, 100, 150, 300):
        x = x_of(L)
        s.line(x, YA1, x, YA1 + 12, BLUE, 4)
        s.text(x, 586, str(L), 30, GRAY, "middle")
    s.text(440, 632, "ORF length (codons)", 30, GRAY, "middle")

    # 理论曲线 E = 6·p·(G/3)·(1−p)^L（深蓝实线，低于基线的点裁掉）
    pts = []
    for L in range(30, 301, 5):
        e = orfdemo.expected_orfs(G, L)
        y = y_of(e)
        if y > YA1:
            break
        pts.append((x_of(L), y))
    s.curve(pts, BLUE, 6)

    # 对比标注柱：L=30 观测 22,170（青蓝高柱）；L=300 跌落基线（期望 0.1）
    x30 = x_of(30)
    s.rect(x30 - 16, y_of(obs[30]), 32, YA1 - y_of(obs[30]), CYAN, rx=6)
    s.circle(x30, y_of(obs[30]), 10, BLUE)
    x300 = x_of(300)
    s.rect(x300 - 16, YA1 - 22, 32, 22, CYAN, rx=6)
    s.polygon([(x300 - 14, YA1 - 26), (x300 + 14, YA1 - 26), (x300, YA1 - 6)],
              BLUE)

    # 左上标注（方案逐字）
    s.text(116, 92, "门槛 30：出 22,170 个", 32, CYAN_DEEP, "start", "bold")
    s.text(116, 136, "门槛 300：期望 0.1 个", 32, GRAY, "start", "bold")

    # 底部红色警示条（唯一红色）
    s.rect(216, 646, 368, 48, RED, rx=12)
    s.text(400, 680, "罕见是强证据，不等于一定", 30, WHITE, "middle", "bold")

    s.save("05_orf_length_decay.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

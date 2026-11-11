#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_resolution_ari_plateau.py — 生成 12_resolution_ari_plateau.svg
（FIG-P02-14：聚类稳定性扫描的 ARI 平台与种子间波动）【data-plot】

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-14（Slide 31，cols 一栏，800×700）。
数据：**直接调用** demos/ch17_resolution_ari.py 的 make_data / kmeans / ari
（同一数据、同一网格 k=2…16、每 k 5 个种子、seed=20261104），逐点断言
k=2 → 0.228、k=7 → 0.731、k=16 → 0.603、平台 k=7…12 的 ARI ∈ [0.693, 0.731]，
并打印平台区种子间 sd（方案文字写作 0.015–0.038，实测 sd(k=7)=0.056，
图中据此只画误差棒、不写 sd 区间）。
图内汉字 = 方案指定整句逐字一致（30 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 12_resolution_ari_plateau.py
"""
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]        # NGS_3Levels/
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from svghelp import *  # noqa: F401,F403
import ch17_resolution_ari as demo  # noqa: E402

TEXT = "平台区兰德指数最高且波动最小。结论须限定稳定区间，单点定稿不可信。"
CELLS, DIMS, KMAX, SEEDS, SEED = 2400, 12, 16, 5, 20261104


def compute():
    X, truth = demo.make_data(CELLS, DIMS, np.random.default_rng(SEED))
    rows = {}
    for k in range(2, KMAX + 1):
        aris = []
        for s in range(SEEDS):
            rng = np.random.default_rng(SEED + 97 * k + s)
            aris.append(demo.ari(truth, demo.kmeans(X, k, rng)))
        rows[k] = (float(np.mean(aris)), float(np.std(aris)))
    return rows


def main():
    rows = compute()
    assert round(rows[2][0], 3) == 0.228
    assert round(rows[7][0], 3) == 0.731
    assert round(rows[16][0], 3) == 0.603
    plateau = [rows[k][0] for k in range(7, 13)]
    assert round(min(plateau), 3) == 0.693 and round(max(plateau), 3) == 0.731
    print("check: " + "  ".join(f"k={k}:{rows[k][0]:.3f}±{rows[k][1]:.3f}"
                                for k in (2, 7, 12, 16)))

    s = SVG(800, 700, "ARI plateau across k", plan=TEXT)
    X0, X1, YT, YB = 150, 700, 130, 430

    def px(k):
        return X0 + (k - 2) / (KMAX - 2) * (X1 - X0)

    def py(v):
        return YB - v * (YB - YT)

    s.line(X0, YT, X0, YB, INK, 3)
    s.line(X0, YB, X1 + 10, YB, INK, 3)
    s.yaxis(X0, YT, YB, [(py(1.0), "1.0"), (py(0.5), "0.5"), (py(0.0), "0.0")])
    for k in (2, 5, 8, 11, 14, 16):
        s.line(px(k), YB, px(k), YB + 8, INK, 3)
        s.text(px(k), YB + 40, str(k), 30, GRAY, "middle")
    s.text((X0 + X1) / 2, 500, "k (clusters)", 30, GRAY, "middle")

    # 平台带（绿）：k = 7…12，ARI 0.693–0.731
    s.rect(px(7), py(0.731), px(12) - px(7), py(0.693) - py(0.731),
           GREEN_TINT, GREEN, 3, rx=6)

    # 曲线 + 种子间 sd 误差棒
    pts = [(px(k), py(rows[k][0])) for k in rows]
    for k in rows:
        x = px(k)
        m, sd = rows[k]
        s.line(x, py(m - sd), x, py(m + sd), BLUE, 3)
        s.line(x - 6, py(m - sd), x + 6, py(m - sd), BLUE, 3)
        s.line(x - 6, py(m + sd), x + 6, py(m + sd), BLUE, 3)
    s.polyline(pts, BLUE, 5)
    for x, y in pts:
        s.circle(x, y, 6, BLUE)

    # 平台标注（深蓝括号）
    s.bracket(px(7), px(12), 150, 8, BLUE, 4)
    s.text((px(7) + px(12)) / 2, 136, "k = 7..12", 30, BLUE, "middle", "bold")

    # 峰值与两端数值
    s.text(px(7), py(0.731) - 18, "0.731", 30, GREEN, "middle", "bold")
    s.text(px(2) + 6, py(0.228) + 34, "0.228", 30, GRAY, "start")
    s.text(px(16), py(0.603) - 18, "0.603", 30, GRAY, "middle")

    # 红色（1 处）：单点定稿不可信
    s.text(700, 400, "NO SINGLE K", 30, RED, "end", "bold")

    s.caption(["平台区兰德指数最高且波动最小。",
               "结论须限定稳定区间，单点定稿不可信。"], [INK, INK], 30,
              top=536)
    s.save("12_resolution_ari_plateau.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())

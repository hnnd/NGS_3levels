#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_ccs_vote_decay.py — 生成 05_ccs_vote_decay.svg（FIG-U03-05：CCS 错误率衰减）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-05（P22，cols 一栏，800×700）【data-plot】。
数据：demos/ch04_ccs_vote.py --selftest 现跑（p=0.10、n_pos=100000、seed=20261103），
此处用同一函数、同一种子、同一调用顺序复算并断言：
  passes 1 → 1.004e-1（Q10.0）；3 → 2.249e-2（Q16.5）；5 → 4.230e-3（Q23.7）；
  11 → 4.000e-5（Q44.0）。改善倍数 1× / 4× / 24× / 2,500×。
无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 05_ccs_vote_decay.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]  # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch04_ccs_vote as demo  # noqa: E402

from svghelp import *  # noqa: F401,F403,E402

PASSES = [1, 3, 5, 11]
EXPECTED = {1: 1.004e-1, 3: 2.249e-2, 5: 4.230e-3, 11: 4.000e-5}
IMPROVE = {1: "1×", 3: "4×", 5: "24×", 11: "2,500×"}

Y0, Y1 = 150, 580  # 1e-1 → 1e-5（对数四档）


def y_of(resid):
    import math
    return Y0 + (-math.log10(resid) - 1) / 4 * (Y1 - Y0)


def main():
    # 与 demos 完全相同的复算（同一 rng 顺序：1,3,5,11）
    rng = np.random.default_rng(20261103)
    resid = {k: demo.consensus_residual(0.10, k, 100000, rng) for k in PASSES}
    for k in PASSES:
        assert abs(resid[k] - EXPECTED[k]) < 5e-4, \
            f"passes={k}: {resid[k]} ≠ demos 现跑 {EXPECTED[k]}"
        print(f"check: passes={k:>2} 残留 {resid[k]:.3e}（demos 一致）")

    s = SVG(800, 700)
    s.text(400, 44, "多圈共识错误率随通过次数急剧下降", 32, BLUE, "middle",
           "bold")
    s.text(400, 82, "多数票稀释随机误差", 30, GRAY, "middle", "bold")

    # Q 值参考虚线（Q10–Q40，标签在左侧，避免与 passes=11 柱顶标签相撞）
    for q, val in ((10, 1e-1), (20, 1e-2), (30, 1e-3), (40, 1e-4)):
        y = y_of(val)
        s.line(90, y, 700, y, GRAY, 3, dash="10 10")
        s.text(82, y + 10, f"Q{q}", 28, GRAY, "end", "bold")

    # 柱状 + 折线
    centers = {1: 170, 3: 330, 5: 490, 11: 650}
    tops = []
    for k in PASSES:
        cx = centers[k]
        yt = y_of(resid[k])
        tops.append((cx, yt))
        s.rect(cx - 50, yt, 100, Y1 - yt, CYAN, rx=8)
        yl = yt - 56 if k == 11 else yt - 42  # Q40 参考线 y≈472，passes=11 标签上移避让
        hot = RED if k == 11 else BLUE
        s.text(cx, yl, IMPROVE[k], 30, hot, "middle", "bold")
        if k == 11:
            s.text(cx, yt + 36, f"{resid[k]:.1e}", 26, WHITE, "middle",
                   "bold")
        else:
            s.text(cx, yt - 12, f"{resid[k]:.1e}", 26, INK, "middle",
                   "bold")
        s.text(cx, Y1 + 40, f"{k}", 32, INK, "middle", "bold")
    s.polyline(tops, BLUE, 6)
    for cx, yt in tops:
        s.circle(cx, yt, 8, BLUE)
    s.text(90, Y1 + 82, "passes →", 28, GRAY, "start", "bold")

    # 红色焦点：passes=11 改善倍数标红（柱顶标签）+ 适用条件
    s.text(400, 672, "仅独立随机", 30, RED, "middle", "bold")

    s.save("05_ccs_vote_decay.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

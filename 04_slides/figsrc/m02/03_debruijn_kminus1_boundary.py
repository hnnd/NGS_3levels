#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""03_debruijn_kminus1_boundary.py — 03_debruijn_kminus1_boundary.svg
（FIG-M02-04，P14，cols）：de Bruijn 图 k−1 边界分叉与欧拉路径歧义【data-plot】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-04。数据（与 demos 现跑一致）：
demos/ch08_debruijn_repeat.py --selftest（R=100、侧翼 300、种子 20261102）：
k=97（k−1=96）分叉 2/多拷贝 5；k=101（k−1=100）分叉 1/多拷贝 1/共享 0；
k=102（k−1=101）分叉 0。无网络；种子固定。
用法：PYTHONDONTWRITEBYTECODE=1 python3 03_debruijn_kminus1_boundary.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch08_debruijn_repeat as demo  # noqa: E402

from svghelp import (BLUE, GREEN, GRAY, INK, ORANGE, RED, SVG, WHITE)


def check_data():
    rng = np.random.default_rng(20261102)
    genome, _, _ = demo.build_genome(rng, 300, 100)
    cases = {}
    for k in (97, 101, 102):
        cases[k] = demo.dbg_stats(genome, k)
    assert cases[97] == (4, 5, 2), cases[97]
    assert cases[101] == (0, 1, 1), cases[101]
    assert cases[102] == (0, 0, 0), cases[102]
    print(f"check: k=97→{cases[97]}；k=101→{cases[101]}；k=102→{cases[102]}"
          "（共享/多拷贝/分叉，demos 复算）")
    return {97: 2, 101: 1, 102: 0}


def row_graph(s, y, branch, mode):
    """行内右侧小图：两入口 → 共享节点 → 出口（mode: collapse/border/free）。"""
    if mode == "free":
        s.arrow(440, y + 80, 720, y + 80, GREEN, 8)
        s.circle(520, y + 80, 9, GREEN)
        s.circle(640, y + 80, 9, GREEN)
        s.text(724, y + 92, "0", 40, GREEN, "start", "bold")
        return
    # 两个入口（青蓝）
    s.arrow(440, y + 44, 520, y + 58, BLUE, 7)
    s.arrow(440, y + 116, 520, y + 102, BLUE, 7)
    if mode == "collapse":
        # 共享区（橙）+ 红色两个出口：欧拉路径不唯一
        s.rect(522, y + 48, 76, 64, ORANGE, rx=8)
        s.arrow(600, y + 62, 700, y + 30, RED, 7)
        s.arrow(600, y + 98, 700, y + 130, RED, 7)
        s.text(716, y + 96, str(branch), 44, RED, "start", "bold")
    else:  # border：单节点 2 进 2 出（红描边 = 保守组装器在此断开）
        s.rect(522, y + 44, 80, 72, ORANGE, RED, 7, rx=8)
        s.arrow(604, y + 60, 700, y + 44, BLUE, 7)
        s.arrow(604, y + 100, 700, y + 116, BLUE, 7)
        s.text(716, y + 96, str(branch), 44, ORANGE, "start", "bold")


def main():
    branch = check_data()

    s = SVG(800, 700)

    rows = [
        (70, "k−1 < R：分叉 2 塌缩", RED, "collapse", 97),
        (270, "k−1 = R：分叉 1 断开", ORANGE, "border", 101),
        (470, "k−1 > R：分叉 0 连通", GREEN, "free", 102),
    ]
    for y, label, color, mode, _ in rows:
        s.rect(40, y, 720, 170, WHITE, "#E9E9E5", 3, rx=14)
        s.text(64, y + 62, label, 33, color, "start", "bold")
        s.text(64, y + 118, "k=" + {"collapse": "97", "border": "101",
                                   "free": "102"}[mode], 30, GRAY, "start")
        row_graph(s, y, branch[{"collapse": 97, "border": 101,
                                "free": 102}[mode]], mode)

    s.text(400, 676, "共享节点始于 k−1", 34, BLUE, "middle", "bold")
    s.save("03_debruijn_kminus1_boundary.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

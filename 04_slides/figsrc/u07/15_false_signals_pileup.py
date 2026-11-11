#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_false_signals_pileup.py — 生成 15_false_signals_pileup.svg（FIG-U07-15：四场景 pileup 计数对比）【data-plot】

方案：reviews/course/U07_FIGP_001.md §4.2 FIG-U07-15（P37，cols 一栏，viewBox 800×700）。
数据（与 demos 现跑一致，import 复算）：demos/ch09_igv_false_signals.py --selftest
（45× 覆盖、15 条 alt、读段 150 bp、末端窗口 10 bp、固定种子 20261104）：
real 0.40/0.00/0.07；strand 1.00/0.00/0.07；mapq0 0.40/1.00/0.07；
endbias 0.40/0.00/1.00（教材 §9.4.7 L302–316）。合成算例标注（图内灰字）。
无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 15_false_signals_pileup.py
"""
from svghelp import *  # noqa: F401,F403
from ch09_igv_false_signals import SCENARIOS, counters, simulate

N_READS, N_ALT, RL, EW, SEED = 45, 15, 150, 10, 20261104

ROWS = [
    ("real", "真实基准", GREEN),
    ("strand", "单链偏好", ORANGE),
    ("mapq0", "重复区", GRAY),
    ("endbias", "末端聚集", CYAN_DEEP),
]


def main():
    data = {}
    for sc in SCENARIOS:
        reads = simulate(sc, N_READS, N_ALT, RL, EW, SEED)
        data[sc] = tuple(round(v, 2) for v in counters(reads, RL, EW))
    assert data["real"] == (0.40, 0.00, 0.07)
    assert data["strand"] == (1.00, 0.00, 0.07)
    assert data["mapq0"] == (0.40, 1.00, 0.07)
    assert data["endbias"] == (0.40, 0.00, 1.00)
    for sc in SCENARIOS:
        print(f"check: [{sc}] fwd/mapq0/end = "
              f"{data[sc][0]:.2f}/{data[sc][1]:.2f}/{data[sc][2]:.2f}")

    s = SVG(800, 700)
    s.text(776, 44, "合成算例", 30, GRAY, "end")

    x_units = [200 + i * 30 for i in range(15)]
    for r, (sc, name, color) in enumerate(ROWS):
        y = 100 + r * 115
        s.text(24, y + 30, sc, 30, GRAY, "start")
        s.text(24, y + 68, name, 30, color, "start", "bold")
        if sc == "real":
            fwd = round(data[sc][0] * N_ALT)  # 6 正 + 9 反
            for i, x in enumerate(x_units):
                c = ORANGE if i < fwd else PURPLE
                s.rect(x, y + 22, 26, 40, c, rx=5)
            s.text(700, y + 52, "0.40", 30, GRAY, "middle")
        elif sc == "strand":
            for x in x_units:
                s.rect(x, y + 22, 26, 40, ORANGE, rx=5)
        elif sc == "mapq0":
            for x in x_units:
                s.rect(x, y + 22, 26, 40, WHITE, GRAY, 4, rx=5, dash="9 7")
        else:
            for x in x_units:
                s.rect(x, y + 22, 26, 40, CYAN, rx=5)
            s.line(196, y + 14, 196, y + 70, ORANGE, 7)
            s.line(654, y + 14, 654, y + 70, ORANGE, 7)

    # 三个异常场景共用红色大括号标注 1.00（红色语义处 1）
    y_top, y_bot = 100 + 115 + 14, 100 + 3 * 115 + 70
    s.path(f"M 684 {y_top} L 694 {y_top} L 694 {y_bot} L 684 {y_bot}",
           RED, 5)
    s.text(742, (y_top + y_bot) / 2 + 10, "1.00", 32, RED, "middle", "bold")

    # 底部红色结论横幅（红色语义处 2）
    s.rect(240, 596, 320, 58, RED, rx=12)
    s.text(400, 637, "线索不是判决", 34, WHITE, "middle", "bold")

    s.save("15_false_signals_pileup.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

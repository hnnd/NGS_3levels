#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_threshold_ladder_ladder.py — 生成 12_threshold_ladder_ladder.svg
（FIG-P05-12：P29「阈值阶梯：同一个分母，四种性质」，cols 左栏）【data-plot】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-12（800×700，中文共 27 字）。
数据入口：教材 §21.4.4 的阈值算术阶梯（手算规则，与
`textbook/demos/ch21_thresholds_fwer_fdr.py --selftest` 部分 A 的打印值逐位一致）：
  0.05/500000 = 1.0×10⁻⁷（朴素 Bonferroni，M 取 50 万）
  0.05/25000 = 2.0×10⁻⁶（M_eff Bonferroni，剪枝集 2.5 万当有效检验数）
  1/25000    = 4.0×10⁻⁵（suggestive 线）
  0.05/36901 = 1.35×10⁻⁶（RDP1 实测 M = 36,901 口径）
  5×10⁻⁸     = 0.05/10⁶（人类惯例值；比 M_eff 口径严 40 倍）
40 倍只在「剪枝集 25000 当 M_eff」这一设例口径下成立，换估计量倍数即变
（教材 §21.4.4、方案 §5.3 W3），图注与 `.ref` 必须带上这句限定。
图内中文严格取方案给定两句（18 + 9 = 27 字）；阈值数字与 −log10 p 刻度为符号。
配色：绿＝推荐的 M_eff 阈值，橙＝suggestive 线，深蓝＝朴素 Bonferroni；
红色只标「人类阈值 vs 自交作物」这一处差距。
依赖：只做四则运算，不需 numpy/scipy。
用法：PYTHONDONTWRITEBYTECODE=1 python3 12_threshold_ladder_ladder.py
"""
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["人类阈值严格四十倍自交作物假阴性灾难",   # 18
           "建议按有效检验定界"]                   # 9
TEXT = "".join(PHRASES)


def check_data():
    """阈值算术（教材 §21.4.4 手算；demos 部分 A 打印同值）。"""
    naive = 0.05 / 500000
    meff = 0.05 / 25000
    sug = 1.0 / 25000
    rdp1 = 0.05 / 36901
    human = 5e-8
    assert abs(naive - 1.0e-7) < 1e-15, naive
    assert abs(meff - 2.0e-6) < 1e-15, meff
    assert abs(sug - 4.0e-5) < 1e-15, sug
    assert abs(rdp1 - 1.355e-6) < 1e-9, rdp1
    assert abs(meff / human - 40.0) < 1e-9, meff / human
    return dict(naive=naive, meff=meff, sug=sug, rdp1=rdp1, human=human)


def main():
    d = check_data()
    s = SVG(800, 700, "Threshold ladder on the -log10 p scale", plan=TEXT)

    xa, xb = 200.0, 690.0

    def py(v):                        # v = -log10(p)
        return 600.0 - (v - 4.0) / 4.0 * 530.0

    # ---------- 标尺与刻度 ----------
    s.line(xa, 600, xa, 60, INK, 5)
    s.text(xa, 44, "-log10 p", 30, GRAY, "middle", "bold")
    for v in (4, 5, 6, 7, 8):
        s.line(xa - 10, py(v), xa, py(v), INK, 4)
        s.text(xa - 20, py(v) + 11, str(v), 30, GRAY, "end")

    # ---------- 五条阈值线 ----------
    rows = [(d["human"], RED, "5×10", "−8", "above", xb, RED),
            (d["naive"], BLUE, "1×10", "−7", "below", xb, BLUE),
            (d["rdp1"], CYAN_DEEP, "1.35×10", "−6", "above", xb, CYAN_DEEP),
            (d["meff"], GREEN, "2×10", "−6", "below", 560, GREEN),
            (d["sug"], ORANGE, "4×10", "−5", "above", xb, ORANGE)]
    for val, col, base, sup, side, lx, tc in rows:
        v = -math.log10(val)
        yy = py(v)
        s.line(xa, yy, lx, yy, col, 5,
               dash=None if side == "above" else "14 9")
        ly = yy - 12 if side == "above" else yy + 32
        s.sci(lx, ly, base, sup, 30, tc, "end", "bold")

    # ---------- 40 倍跨度 ----------
    # 跨度标注用中性灰：红色只留给「人类阈值线」与底部结论句两处
    s.darrow(740, py(-math.log10(d["human"])), 740,
             py(-math.log10(d["meff"])), GRAY, 4, 13)
    s.text(736, 288, "40×", 30, GRAY, "end", "bold")

    # ---------- 两句结论 ----------
    s.text(400, 654, PHRASES[0], 32, RED, "middle", "bold")
    s.text(400, 690, PHRASES[1], 32, GREEN, "middle", "bold")

    s.save("12_threshold_ladder_ladder.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_amplicon_redlight_contrast.py — 生成 07_amplicon_redlight_contrast.svg
（FIG-U04-07：扩增子对照——名额未满红灯照报【data-plot】）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-07（P20，cols 一栏，viewBox 800×700）。
左栏随机文库：10 万满额（触发观察上限），去重剩 100.0% → PASS（绿）；
右栏扩增子文库：仅 8,171 种 50-mer（未触发上限），去重剩 4.09% → FAIL（红），
最高单条 13.89% → FAIL（红）；底部红字「名额未满照报红」。
数据来源（直接调用 demos 生成器与判定函数，固定种子，逐项一致）：
demos/ch06_amplicon_redlight.py --selftest（seed=20261103）。
依据：教材 §6.4.3 L88–94。图内汉字 24，红色 2 处。
用法：PYTHONDONTWRITEBYTECODE=1 python3 07_amplicon_redlight_contrast.py
"""
import sys

import numpy as np

from svghelp import *

ROOT = Path(__file__).resolve().parents[3]  # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from ch06_amplicon_redlight import (  # noqa: E402
    fastqc_duplication, fastqc_overrepresented, gen_amplicon_like,
    gen_wgs_like,
)

SEED = 20261103


def main():
    rng = np.random.default_rng(SEED)
    wgs = gen_wgs_like(rng, 200000, 150)
    amp = gen_amplicon_like(rng, 200000, 40, 150, 0.005)
    pct_w, st_w, nuniq_w, frozen_w = fastqc_duplication(wgs)
    pct_a, st_a, nuniq_a, frozen_a = fastqc_duplication(amp)
    top_a, toppct_a, _, ost_a = fastqc_overrepresented(amp)
    assert frozen_w and nuniq_w == 100000 and abs(pct_w - 100.0) < 1e-9
    assert st_w == "pass"
    assert (not frozen_a and nuniq_a == 8171
            and abs(pct_a - 4.085500000000001) < 1e-6 and st_a == "fail")
    assert top_a == 27788 and abs(toppct_a - 13.894) < 1e-9 and ost_a == "fail"
    print(f"check: WGS {nuniq_w} 满额 {pct_w:.4f}% PASS；"
          f"amplicon {nuniq_a} 未满 {pct_a:.4f}% FAIL，"
          f"top {top_a} = {toppct_a:.4f}% FAIL")

    s = SVG(800, 700)
    BASE, TOP = 520, 110          # 基线、100% 顶
    HMAX = BASE - TOP

    # 100% 参考网格与基线
    s.line(60, TOP, 740, TOP, PANEL, sw=3)
    s.text(740, 140, "100%", 30, GRAY, "end")
    s.line(60, BASE, 740, BASE, INK, sw=4)

    # 左栏：随机文库（绿，PASS）
    s.text(185, 78, "随机：十万满额", 30, INK, "middle", "bold")
    s.rect(120, TOP, 130, HMAX, GREEN, rx=8)
    s.text(185, (TOP + BASE) / 2 + 10, "100.0%", 30, WHITE, "middle", "bold")
    s.rect(120, 548, 130, 54, GREEN, rx=10)
    s.text(185, 586, "PASS", 30, WHITE, "middle", "bold")

    # 右栏：扩增子文库（红，双 FAIL）
    s.text(560, 78, "扩增子：仅 8171 种", 30, INK, "middle", "bold")
    h1 = HMAX * pct_a / 100.0                     # 4.09%
    h2 = HMAX * toppct_a / 100.0                  # 13.89%
    s.rect(430, BASE - h1, 90, h1, RED, rx=6)
    s.text(475, BASE - h1 - 16, "去重剩 4.09%", 30, RED, "middle", "bold")
    s.rect(570, BASE - h2, 90, h2, RED, rx=6)
    s.text(615, BASE - h2 - 16, "最高单条 13.89%", 30, RED, "middle", "bold")
    s.rect(430, 548, 230, 54, RED, rx=10)
    s.text(545, 586, "FAIL", 30, WHITE, "middle", "bold")

    # 底部红字
    s.text(400, 658, "名额未满照报红", 30, RED, "middle", "bold")

    s.save("07_amplicon_redlight_contrast.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
